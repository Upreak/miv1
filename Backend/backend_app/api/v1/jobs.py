"""
Jobs API Routes
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_jobs():
    """Get all jobs"""
    return {"message": "Jobs endpoint - under development"}

@router.get("/{job_id}")
async def get_job(job_id: str):
    """Get job by ID"""
    return {"message": f"Job {job_id} - under development"}
