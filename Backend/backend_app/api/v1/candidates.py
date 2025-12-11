"""
Candidates API Routes
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_candidates():
    """Get all candidates"""
    return {"message": "Candidates endpoint - under development"}

@router.get("/{candidate_id}")
async def get_candidate(candidate_id: str):
    """Get candidate by ID"""
    return {"message": f"Candidate {candidate_id} - under development"}
