from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from dotenv import load_dotenv
from models import PromptRequest, JobStatus, JobResponse, ImprovementIteration, ScoreResponse
from prompt_engine import improve_prompt

load_dotenv()

app = FastAPI(
    title="Prompt Engineering API",
    description="API for improving and optimizing prompts using AI evaluation",
    version="1.0.0"
)

jobs = {}

@app.post("/improve-prompt", response_model=JobResponse)
async def start_prompt_improvement(request: PromptRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
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
            result = await improve_prompt(request)
            jobs[job_id]["status"] = result["status"]
            jobs[job_id]["final_prompt"] = result["final_prompt"]
            jobs[job_id]["completed_at"] = datetime.now()
            if result["iterations"]:
                jobs[job_id]["progress"] = len(result["iterations"])
                jobs[job_id]["current_iteration"] = result["iterations"][-1]
            jobs[job_id]["error"] = result["error"]
        except Exception as e:
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
async def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(**jobs[job_id])

@app.get("/jobs")
async def list_jobs():
    return {"jobs": list(jobs.keys()), "total": len(jobs)}

@app.delete("/job/{job_id}")
async def delete_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
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