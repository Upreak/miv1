"""
API Router Module
"""
from fastapi import APIRouter
from backend_app.api.v1 import (
    auth,
    candidates,
    jobs,
    applications,
    extraction,
    brain
)

# Create main API router
api_router = APIRouter()

# Include version 1 routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["Candidates"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(applications.router, prefix="/applications", tags=["Applications"])
api_router.include_router(extraction.router, prefix="/extraction", tags=["Extraction"])
api_router.include_router(brain.router, prefix="/brain", tags=["Brain"])