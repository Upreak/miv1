from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.db import get_db
from app.schemas.jobs import JobCreate, JobUpdate, JobResponse, JobSearch
from app.schemas.applications import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.schemas.candidates import CandidateProfileResponse
from app.models.jobs import Job
from app.models.applications import Application
from app.models.action_queue import ActionQueue
from uuid import UUID
from datetime import datetime

router = APIRouter()

@router.get("/jobs", response_model=List[JobResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    recruiter_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Job)
        
        if recruiter_id:
            query = query.filter(Job.assigned_recruiter_id == UUID(recruiter_id))
        
        if status:
            query = query.filter(Job.status == status)
        
        jobs = query.offset(skip).limit(limit).all()
        return jobs
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving jobs: {str(e)}"
        )

@router.post("/jobs", response_model=JobResponse)
async def create_job(
    job: JobCreate,
    db: Session = Depends(get_db)
):
    try:
        db_job = Job(
            client_id=UUID(job.client_id),
            assigned_recruiter_id=UUID(job.assigned_recruiter_id),
            title=job.title,
            internal_job_id=job.internal_job_id,
            employment_type=job.employment_type,
            work_mode=job.work_mode,
            industry=job.industry,
            functional_area=job.functional_area,
            job_locations=job.job_locations,
            min_salary=job.min_salary,
            max_salary=job.max_salary,
            currency=job.currency,
            salary_unit=job.salary_unit,
            benefits_perks=job.benefits_perks,
            about_company=job.about_company,
            job_summary=job.job_summary,
            responsibilities=job.responsibilities,
            experience_required=job.experience_required,
            education_qualification=job.education_qualification,
            required_skills=job.required_skills,
            preferred_skills=job.preferred_skills,
            tools_tech_stack=job.tools_tech_stack,
            number_of_openings=job.number_of_openings,
            application_deadline=job.application_deadline,
            hiring_process_rounds=job.hiring_process_rounds,
            notice_period_accepted=job.notice_period_accepted,
            slug_url=job.slug_url,
            meta_title=job.meta_title,
            meta_description=job.meta_description,
            status=job.status or "Draft"
        )
        
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        return db_job
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating job: {str(e)}"
        )

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    try:
        job = db.query(Job).filter(Job.id == UUID(job_id)).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        return job
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving job: {str(e)}"
        )

@router.put("/jobs/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    job_update: JobUpdate,
    db: Session = Depends(get_db)
):
    try:
        job = db.query(Job).filter(Job.id == UUID(job_id)).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        for field, value in job_update.dict(exclude_unset=True).items():
            setattr(job, field, value)
        
        db.commit()
        db.refresh(job)
        
        return job
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating job: {str(e)}"
        )

@router.post("/applications", response_model=ApplicationResponse)
async def submit_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    try:
        db_application = Application(
            job_id=UUID(application.job_id),
            candidate_id=UUID(application.candidate_id),
            status="New",
            is_active=True
        )
        
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        
        # Create timeline entry
        timeline = ActionQueue(
            user_id=UUID(application.candidate_id),
            type="NEW_MATCHES",
            title="New Application Submitted",
            description=f"Candidate applied for job {application.job_id}",
            priority="Medium",
            related_job_id=UUID(application.job_id),
            related_candidate_id=UUID(application.candidate_id),
            created_at=datetime.utcnow()
        )
        
        db.add(timeline)
        db.commit()
        
        return db_application
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting application: {str(e)}"
        )

@router.get("/applications/{job_id}", response_model=List[ApplicationResponse])
async def get_applications_for_job(
    job_id: str,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Application).filter(Application.job_id == UUID(job_id))
        
        if status:
            query = query.filter(Application.status == status)
        
        applications = query.offset(skip).limit(limit).all()
        return applications
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving applications: {str(e)}"
        )

@router.put("/applications/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    application_update: ApplicationUpdate,
    db: Session = Depends(get_db)
):
    try:
        application = db.query(Application).filter(Application.id == UUID(application_id)).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        for field, value in application_update.dict(exclude_unset=True).items():
            setattr(application, field, value)
        
        db.commit()
        db.refresh(application)
        
        return application
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating application: {str(e)}"
        )

@router.get("/action-queue/{user_id}")
async def get_action_queue(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        action_queue = db.query(ActionQueue).filter(
            ActionQueue.user_id == UUID(user_id),
            ActionQueue.is_dismissed == False
        ).offset(skip).limit(limit).all()
        
        return action_queue
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving action queue: {str(e)}"
        )

@router.put("/action-queue/{action_id}/dismiss")
async def dismiss_action(
    action_id: str,
    db: Session = Depends(get_db)
):
    try:
        action = db.query(ActionQueue).filter(ActionQueue.id == UUID(action_id)).first()
        
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Action not found"
            )
        
        action.is_dismissed = True
        db.commit()
        
        return {"message": "Action dismissed successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error dismissing action: {str(e)}"
        )