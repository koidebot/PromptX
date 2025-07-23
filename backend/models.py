from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

default_criteria = ["relevance", "coherence", "simplicity", "depth"]

class PromptRequest(BaseModel):
    prompt: str
    criteria: Optional[List[str]] = Field(default=default_criteria)
    max_iterations: Optional[int] = Field(default=8)
    min_consecutive_improvements: Optional[int] = Field(default=2)

class ScoreResponse(BaseModel):
    relevance: Optional[int]
    coherence: Optional[int]
    simplicity: Optional[int]
    depth: Optional[int]
    average: Optional[float]

class ImprovementIteration(BaseModel):
    iteration: int
    prompt: str
    scores: ScoreResponse
    improvements_needed: List[str]
    timestamp: datetime

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    total_iterations: int
    current_iteration: Optional[ImprovementIteration]
    final_prompt: Optional[str]
    error: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    total_prompts: int
    total_jobs: int
    created_at: datetime

# Prompt history models
class PromptHistoryResponse(BaseModel):
    id: str
    original_prompt: str
    improved_prompt: str
    total_iterations: int
    created_at: datetime