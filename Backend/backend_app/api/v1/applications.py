"""
Applications API Routes
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_applications():
    """Get all applications"""
    return {"message": "Applications endpoint - under development"}

@router.get("/{application_id}")
async def get_application(application_id: str):
    """Get application by ID"""
    return {"message": f"Application {application_id} - under development"}
