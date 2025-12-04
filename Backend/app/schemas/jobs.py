from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class JobCreate(BaseModel):
    client_id: str
    assigned_recruiter_id: str
    title: str
    internal_job_id: str
    employment_type: Optional[str] = None
    work_mode: Optional[str] = None
    industry: Optional[str] = None
    functional_area: Optional[str] = None
    job_locations: Optional[List[str]] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    currency: Optional[str] = None
    salary_unit: Optional[str] = None
    benefits_perks: Optional[List[str]] = None
    about_company: Optional[str] = None
    job_summary: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    experience_required: Optional[str] = None
    education_qualification: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    tools_tech_stack: Optional[List[str]] = None
    number_of_openings: Optional[int] = None
    application_deadline: Optional[date] = None
    hiring_process_rounds: Optional[List[str]] = None
    notice_period_accepted: Optional[str] = None
    slug_url: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    status: Optional[str] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    employment_type: Optional[str] = None
    work_mode: Optional[str] = None
    industry: Optional[str] = None
    functional_area: Optional[str] = None
    job_locations: Optional[List[str]] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    currency: Optional[str] = None
    salary_unit: Optional[str] = None
    benefits_perks: Optional[List[str]] = None
    about_company: Optional[str] = None
    job_summary: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    experience_required: Optional[str] = None
    education_qualification: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    tools_tech_stack: Optional[List[str]] = None
    number_of_openings: Optional[int] = None
    application_deadline: Optional[date] = None
    hiring_process_rounds: Optional[List[str]] = None
    notice_period_accepted: Optional[str] = None
    slug_url: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    status: Optional[str] = None

class JobResponse(BaseModel):
    id: str
    client_id: str
    assigned_recruiter_id: str
    title: str
    internal_job_id: str
    employment_type: Optional[str] = None
    work_mode: Optional[str] = None
    industry: Optional[str] = None
    functional_area: Optional[str] = None
    job_locations: Optional[List[str]] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    currency: Optional[str] = None
    salary_unit: Optional[str] = None
    benefits_perks: Optional[List[str]] = None
    about_company: Optional[str] = None
    job_summary: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    experience_required: Optional[str] = None
    education_qualification: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    tools_tech_stack: Optional[List[str]] = None
    number_of_openings: Optional[int] = None
    application_deadline: Optional[date] = None
    hiring_process_rounds: Optional[List[str]] = None
    notice_period_accepted: Optional[str] = None
    slug_url: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobSearch(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[str] = None