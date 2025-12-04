from sqlalchemy import Column, String, TIMESTAMP, DATE, Integer, DECIMAL, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from app.core.db import Base
import uuid

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    client_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK -> clients.id
    assigned_recruiter_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK -> users.id
    title = Column(String, nullable=False)  # job_title
    internal_job_id = Column(String, nullable=False)  # job_id
    employment_type = Column(String)  # 'FULL_TIME', 'PART_TIME', 'CONTRACTOR', 'TEMPORARY', 'INTERN'
    work_mode = Column(String)  # 'On-site', 'Remote', 'Hybrid'
    industry = Column(String)
    functional_area = Column(String)
    
    # Location & Compensation
    job_locations = Column(JSONB)  # Array of strings (City, State)
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    currency = Column(String)  # 'INR', 'USD'
    salary_unit = Column(String)  # 'YEAR', 'MONTH', 'HOUR'
    benefits_perks = Column(JSONB)  # Array of strings
    
    # Description & Requirements
    about_company = Column(String)
    job_summary = Column(String)  # Full description
    responsibilities = Column(JSONB)  # Key duties
    experience_required = Column(String)  # e.g. "3-5 Years"
    education_qualification = Column(String)  # e.g. "B.Tech"
    required_skills = Column(JSONB)  # ["React", "Node"]
    preferred_skills = Column(JSONB)
    tools_tech_stack = Column(JSONB)
    
    # Application & Process
    number_of_openings = Column(Integer)
    application_deadline = Column(DATE)
    hiring_process_rounds = Column(JSONB)  # Array of round names e.g. ["Screening", "Tech"]
    notice_period_accepted = Column(String)  # e.g. "Immediate to 30 Days"
    
    # SEO & Metadata
    slug_url = Column(String, unique=True)  # SEO friendly URL
    meta_title = Column(String)  # SEO Title
    meta_description = Column(String)  # SEO Description
    
    # Status
    status = Column(String)  # 'Draft', 'Sourcing', 'Interview', 'Offer', 'Closed'
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))