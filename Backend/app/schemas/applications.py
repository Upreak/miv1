from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class ApplicationCreate(BaseModel):
    job_id: str
    candidate_id: str

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    is_active: Optional[bool] = None
    match_score: Optional[int] = None
    ai_custom_summary: Optional[str] = None
    automation_status: Optional[str] = None
    is_recruiter_approved: Optional[bool] = None
    follow_up_status: Optional[str] = None
    next_follow_up_date: Optional[date] = None
    follow_up_remarks: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: str
    job_id: str
    candidate_id: str
    applied_at: datetime
    status: str
    is_active: bool
    match_score: Optional[int] = None
    ai_custom_summary: Optional[str] = None
    automation_status: Optional[str] = None
    is_recruiter_approved: Optional[bool] = None
    follow_up_status: Optional[str] = None
    next_follow_up_date: Optional[date] = None
    follow_up_remarks: Optional[str] = None

    class Config:
        from_attributes = True

class ApplicationTimelineCreate(BaseModel):
    application_id: str
    previous_status: Optional[str] = None
    new_status: str
    changed_by: Optional[str] = None
    remarks: Optional[str] = None