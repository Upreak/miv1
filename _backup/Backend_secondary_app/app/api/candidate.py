from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.db import get_db
from app.schemas.candidates import CandidateProfileCreate, CandidateProfileUpdate, CandidateProfileResponse, WorkHistoryCreate, WorkHistoryUpdate, WorkHistoryResponse
from app.models.candidate_profiles import CandidateProfile
from app.models.candidate_work_history import CandidateWorkHistory
from uuid import UUID
from datetime import datetime

router = APIRouter()

@router.post("/profile", response_model=CandidateProfileResponse)
async def create_candidate_profile(
    profile: CandidateProfileCreate,
    db: Session = Depends(get_db)
):
    try:
        candidate_profile = CandidateProfile(
            user_id=UUID(profile.user_id) if hasattr(profile, 'user_id') else None,
            phone=profile.phone,
            linkedin_url=profile.linkedin_url,
            portfolio_url=profile.portfolio_url,
            github_url=profile.github_url,
            bio=profile.bio,
            is_actively_searching=profile.is_actively_searching,
            highest_education=profile.highest_education,
            year_of_passing=profile.year_of_passing,
            skills=profile.skills,
            certificates=profile.certificates,
            projects_summary=profile.projects_summary,
            total_experience_years=profile.total_experience_years,
            current_role=profile.current_role,
            expected_role=profile.expected_role,
            job_type_preference=profile.job_type_preference,
            current_locations=profile.current_locations,
            preferred_locations=profile.preferred_locations,
            ready_to_relocate=profile.ready_to_relocate,
            notice_period=profile.notice_period,
            availability_date=profile.availability_date,
            shift_preference=profile.shift_preference,
            work_authorization=profile.work_authorization,
            current_ctc=profile.current_ctc,
            expected_ctc=profile.expected_ctc,
            currency=profile.currency,
            is_ctc_negotiable=profile.is_ctc_negotiable,
            looking_for_jobs_abroad=profile.looking_for_jobs_abroad,
            sector_preference=profile.sector_preference,
            preferred_industries=profile.preferred_industries,
            gender=profile.gender,
            marital_status=profile.marital_status,
            dob=profile.dob,
            languages=profile.languages,
            reservation_category=profile.reservation_category,
            disability=profile.disability,
            willingness_to_travel=profile.willingness_to_travel,
            has_driving_license=profile.has_driving_license,
            has_current_offers=profile.has_current_offers,
            number_of_offers=profile.number_of_offers,
            best_time_to_contact=profile.best_time_to_contact,
            preferred_contact_mode=profile.preferred_contact_mode,
            alternate_email=profile.alternate_email,
            alternate_phone=profile.alternate_phone,
            time_zone=profile.time_zone
        )
        
        db.add(candidate_profile)
        db.commit()
        db.refresh(candidate_profile)
        
        return candidate_profile
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating candidate profile: {str(e)}"
        )

@router.get("/profile/{user_id}", response_model=CandidateProfileResponse)
async def get_candidate_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    try:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == UUID(user_id)).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate profile not found"
            )
        
        return profile
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving candidate profile: {str(e)}"
        )

@router.put("/profile/{user_id}", response_model=CandidateProfileResponse)
async def update_candidate_profile(
    user_id: str,
    profile_update: CandidateProfileUpdate,
    db: Session = Depends(get_db)
):
    try:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == UUID(user_id)).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate profile not found"
            )
        
        for field, value in profile_update.dict(exclude_unset=True).items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        
        return profile
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating candidate profile: {str(e)}"
        )

@router.post("/work-history", response_model=WorkHistoryResponse)
async def add_work_history(
    work_history: WorkHistoryCreate,
    db: Session = Depends(get_db)
):
    try:
        work_hist = CandidateWorkHistory(
            profile_id=UUID(work_history.profile_id),
            company_name=work_history.company_name,
            job_title=work_history.job_title,
            start_date=work_history.start_date,
            end_date=work_history.end_date,
            is_current=work_history.is_current,
            responsibilities=work_history.responsibilities,
            tools_used=work_history.tools_used,
            ctc_at_role=work_history.ctc_at_role
        )
        
        db.add(work_hist)
        db.commit()
        db.refresh(work_hist)
        
        return work_hist
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding work history: {str(e)}"
        )

@router.get("/work-history/{profile_id}", response_model=List[WorkHistoryResponse])
async def get_work_history(
    profile_id: str,
    db: Session = Depends(get_db)
):
    try:
        work_histories = db.query(CandidateWorkHistory).filter(
            CandidateWorkHistory.profile_id == UUID(profile_id)
        ).all()
        
        return work_histories
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving work history: {str(e)}"
        )

@router.put("/work-history/{history_id}", response_model=WorkHistoryResponse)
async def update_work_history(
    history_id: str,
    work_history_update: WorkHistoryUpdate,
    db: Session = Depends(get_db)
):
    try:
        work_hist = db.query(CandidateWorkHistory).filter(
            CandidateWorkHistory.id == UUID(history_id)
        ).first()
        
        if not work_hist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Work history not found"
            )
        
        for field, value in work_history_update.dict(exclude_unset=True).items():
            setattr(work_hist, field, value)
        
        db.commit()
        db.refresh(work_hist)
        
        return work_hist
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating work history: {str(e)}"
        )

@router.delete("/work-history/{history_id}")
async def delete_work_history(
    history_id: str,
    db: Session = Depends(get_db)
):
    try:
        work_hist = db.query(CandidateWorkHistory).filter(
            CandidateWorkHistory.id == UUID(history_id)
        ).first()
        
        if not work_hist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Work history not found"
            )
        
        db.delete(work_hist)
        db.commit()
        
        return {"message": "Work history deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting work history: {str(e)}"
        )