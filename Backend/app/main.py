from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, resume, candidate, recruiter, sales, admin

app = FastAPI(
    title="AI Recruitment Backend",
    description="Complete backend foundation for AI-powered recruitment platform",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/resume", tags=["Resume Processing"])
app.include_router(candidate.router, prefix="/candidate", tags=["Candidate Management"])
app.include_router(recruiter.router, prefix="/recruiter", tags=["Recruiter Workspace"])
app.include_router(sales.router, prefix="/sales", tags=["Sales CRM"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "AI Recruitment Backend is running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)