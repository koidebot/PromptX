from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from dotenv import load_dotenv
from functools import wraps
from collections import defaultdict
from models import PromptRequest, JobStatus, JobResponse, UserCreate, UserLogin, UserResponse
from typing import List
from prompt_engine import PromptEngine, improve_prompt
from services.prompt_service import PromptService
from services.user_service import UserService
from auth.dependencies import get_current_user
from database.connections import get_db
from database.models import User


load_dotenv()

app = FastAPI(
    title="Prompt Engineering API",
    description="API for improving and optimizing prompts using AI evaluation",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",  # React default
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}

# User-based rate limiting storage
user_requests = defaultdict(list)  # {user_id: [timestamp1, timestamp2, ...]}

def user_rate_limit(max_requests: int, window_hours: int = 24):
    """Decorator for user-based rate limiting"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = None
            for arg_name, arg_value in kwargs.items():
                if arg_name == 'current_user' and hasattr(arg_value, 'id'):
                    current_user = arg_value
                    break
            
            if not current_user:
                raise HTTPException(status_code=500, detail="Rate limiting error: No user found")
            
            user_id = current_user.id
            now = datetime.now()
            window_start = now - timedelta(hours=window_hours)
            
            # Clean old requests outside the window
            user_requests[user_id] = [
                req_time for req_time in user_requests[user_id] 
                if req_time > window_start
            ]
            
            # Check if user has exceeded the limit
            if len(user_requests[user_id]) >= max_requests:
                raise HTTPException(
                    status_code=429, 
                    detail=f"Rate limit exceeded: {max_requests} requests per {window_hours} hours"
                )
            
            # Add current request timestamp
            user_requests[user_id].append(now)
            
            # Call the original function
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@app.post("/auth/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    try:
        user = user_service.create_user(
            email=user_data.email,
            password=user_data.password
        )
        return {"message": "User created successfully", "user_id": user.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user_service = UserService(db)
    try:
        result = user_service.login_user(user_data.email, user_data.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        total_prompts=current_user.total_prompts,
        total_jobs=current_user.total_jobs,
        created_at=current_user.created_at
    )

# Prompt history endpoints
@app.get("/prompt-history")
async def get_prompt_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prompt_service = PromptService(db, current_user.id)
    history = prompt_service.get_user_prompt_history()
    
    prompts = [
        {
            "id": prompt.id,
            "initial_prompt": prompt.original_prompt,
            "final_prompt": prompt.improved_prompt,
            "optimization_score": min(100, max(0, prompt.total_iterations * 10 + 50)),  # Convert iterations to a score
            "created_at": prompt.created_at.isoformat()
        }
        for prompt in history
    ]
    
    return {"prompts": prompts}

@app.post("/improve-prompt", response_model=JobResponse)
@user_rate_limit(max_requests=5, window_hours=24)  # 5 requests per day per user
async def start_prompt_improvement(
    request: PromptRequest, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "user_id": current_user.id,
        "status": "pending",
        "progress": 0,
        "total_iterations": request.max_iterations,
        "current_iteration": None,
        "final_prompt": None,
        "error": None,
        "created_at": datetime.now(),
        "completed_at": None
    }

    async def run_improvement():
        try:
            jobs[job_id]["status"] = "running"
            
            async def progress_callback(iteration_data):
                if job_id in jobs: 
                    jobs[job_id]["progress"] = iteration_data["iteration"]
                    jobs[job_id]["current_iteration"] = iteration_data
            
            result = await improve_prompt(request, progress_callback)
            
            if job_id in jobs:
                jobs[job_id]["status"] = result["status"]
                jobs[job_id]["final_prompt"] = result["final_prompt"]
                jobs[job_id]["completed_at"] = datetime.now()
                if result["iterations"]:
                    jobs[job_id]["progress"] = len(result["iterations"])
                    jobs[job_id]["current_iteration"] = result["iterations"][-1]
                jobs[job_id]["error"] = result["error"]
                
                # Save to database if successful
                if result["status"] == "completed" and result["final_prompt"]:
                    prompt_service = PromptService(db, current_user.id)
                    iterations_count = len(result["iterations"]) if result["iterations"] else 0
                    prompt_service.save_prompt_result(
                        original_prompt=request.prompt,
                        improved_prompt=result["final_prompt"], 
                        total_iterations=iterations_count
                    )
                    prompt_service.update_user_stats()
                    
        except Exception as e:
            if job_id in jobs:  
                jobs[job_id]["status"] = "failed"
                jobs[job_id]["error"] = str(e)
                jobs[job_id]["completed_at"] = datetime.now()

    background_tasks.add_task(run_improvement)

    return JobResponse(
        job_id=job_id,
        status="pending",
        message="Prompt improvement job started successfully"
    )

@app.get("/job/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str, current_user: User = Depends(get_current_user)):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: Job belongs to another user")
    
    return JobStatus(**job)

@app.get("/jobs")
async def list_jobs(current_user: User = Depends(get_current_user)):
    user_jobs = {
        job_id: job for job_id, job in jobs.items() 
        if job["user_id"] == current_user.id
    }
    return {"jobs": list(user_jobs.keys()), "total": len(user_jobs)}

@app.delete("/job/{job_id}")
async def delete_job(job_id: str, current_user: User = Depends(get_current_user)):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: Job belongs to another user")
    
    del jobs[job_id]
    return {"message": f"Job {job_id} deleted successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Prompt Engineering API",
        "docs": "/docs",
        "health": "/health"
    }