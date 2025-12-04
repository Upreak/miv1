from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class CandidateProfileCreate(BaseModel):
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    bio: Optional[str] = None
    is_actively_searching: Optional[bool] = None
    highest_education: Optional[str] = None
    year_of_passing: Optional[int] = None
    skills: Optional[List[str]] = None
    certificates: Optional[List[str]] = None
    projects_summary: Optional[str] = None
    total_experience_years: Optional[float] = None
    current_role: Optional[str] = None
    expected_role: Optional[str] = None
    job_type_preference: Optional[str] = None
    current_locations: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    ready_to_relocate: Optional[str] = None
    notice_period: Optional[int] = None
    availability_date: Optional[date] = None
    shift_preference: Optional[str] = None
    work_authorization: Optional[str] = None
    current_ctc: Optional[int] = None
    expected_ctc: Optional[int] = None
    currency: Optional[str] = None
    is_ctc_negotiable: Optional[bool] = None
    looking_for_jobs_abroad: Optional[bool] = None
    sector_preference: Optional[str] = None
    preferred_industries: Optional[List[str]] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    dob: Optional[date] = None
    languages: Optional[List[str]] = None
    reservation_category: Optional[str] = None
    disability: Optional[str] = None
    willingness_to_travel: Optional[str] = None
    has_driving_license: Optional[bool] = None
    has_current_offers: Optional[bool] = None
    number_of_offers: Optional[int] = None
    best_time_to_contact: Optional[str] = None
    preferred_contact_mode: Optional[str] = None
    alternate_email: Optional[str] = None
    alternate_phone: Optional[str] = None
    time_zone: Optional[str] = None

class CandidateProfileUpdate(BaseModel):
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    bio: Optional[str] = None
    is_actively_searching: Optional[bool] = None
    highest_education: Optional[str] = None
    year_of_passing: Optional[int] = None
    skills: Optional[List[str]] = None
    certificates: Optional[List[str]] = None
    projects_summary: Optional[str] = None
    total_experience_years: Optional[float] = None
    current_role: Optional[str] = None
    expected_role: Optional[str] = None
    job_type_preference: Optional[str] = None
    current_locations: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    ready_to_relocate: Optional[str] = None
    notice_period: Optional[int] = None
    availability_date: Optional[date] = None
    shift_preference: Optional[str] = None
    work_authorization: Optional[str] = None
    current_ctc: Optional[int] = None
    expected_ctc: Optional[int] = None
    currency: Optional[str] = None
    is_ctc_negotiable: Optional[bool] = None
    looking_for_jobs_abroad: Optional[bool] = None
    sector_preference: Optional[str] = None
    preferred_industries: Optional[List[str]] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    dob: Optional[date] = None
    languages: Optional[List[str]] = None
    reservation_category: Optional[str] = None
    disability: Optional[str] = None
    willingness_to_travel: Optional[str] = None
    has_driving_license: Optional[bool] = None
    has_current_offers: Optional[bool] = None
    number_of_offers: Optional[int] = None
    best_time_to_contact: Optional[str] = None
    preferred_contact_mode: Optional[str] = None
    alternate_email: Optional[str] = None
    alternate_phone: Optional[str] = None
    time_zone: Optional[str] = None

class CandidateProfileResponse(BaseModel):
    user_id: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    resume_url: Optional[str] = None
    resume_last_updated: Optional[datetime] = None
    bio: Optional[str] = None
    is_actively_searching: Optional[bool] = None
    highest_education: Optional[str] = None
    year_of_passing: Optional[int] = None
    skills: Optional[List[str]] = None
    certificates: Optional[List[str]] = None
    projects_summary: Optional[str] = None
    total_experience_years: Optional[float] = None
    current_role: Optional[str] = None
    expected_role: Optional[str] = None
    job_type_preference: Optional[str] = None
    current_locations: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    ready_to_relocate: Optional[str] = None
    notice_period: Optional[int] = None
    availability_date: Optional[date] = None
    shift_preference: Optional[str] = None
    work_authorization: Optional[str] = None
    current_ctc: Optional[int] = None
    expected_ctc: Optional[int] = None
    currency: Optional[str] = None
    is_ctc_negotiable: Optional[bool] = None
    looking_for_jobs_abroad: Optional[bool] = None
    sector_preference: Optional[str] = None
    preferred_industries: Optional[List[str]] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    dob: Optional[date] = None
    languages: Optional[List[str]] = None
    reservation_category: Optional[str] = None
    disability: Optional[str] = None
    willingness_to_travel: Optional[str] = None
    has_driving_license: Optional[bool] = None
    has_current_offers: Optional[bool] = None
    number_of_offers: Optional[int] = None
    best_time_to_contact: Optional[str] = None
    preferred_contact_mode: Optional[str] = None
    alternate_email: Optional[str] = None
    alternate_phone: Optional[str] = None
    time_zone: Optional[str] = None

    class Config:
        from_attributes = True

class WorkHistoryCreate(BaseModel):
    company_name: str
    job_title: str
    start_date: date
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    responsibilities: Optional[str] = None
    tools_used: Optional[List[str]] = None
    ctc_at_role: Optional[str] = None

class WorkHistoryUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    responsibilities: Optional[str] = None
    tools_used: Optional[List[str]] = None
    ctc_at_role: Optional[str] = None

class WorkHistoryResponse(BaseModel):
    id: str
    profile_id: str
    company_name: str
    job_title: str
    start_date: date
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    responsibilities: Optional[str] = None
    tools_used: Optional[List[str]] = None
    ctc_at_role: Optional[str] = None

    class Config:
        from_attributes = True