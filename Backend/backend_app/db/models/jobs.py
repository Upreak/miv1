"""
Jobs Model (Internal Postings)
Manages internal job postings and the hiring pipeline. Google Jobs Compliant Schema.
"""
from sqlalchemy import Column, String, Text, DATE, Integer, DECIMAL, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from backend_app.db.connection import Base


class Job(Base):
    """Jobs model for internal postings"""
    
    __tablename__ = "jobs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Basic details
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    assigned_recruiter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String(500), nullable=False)  # job_title
    internal_job_id = Column(String(100))  # job_id
    
    # Job type and classification
    employment_type = Column(Enum('FULL_TIME', 'PART_TIME', 'CONTRACTOR', 'TEMPORARY', 'INTERN', name='employment_type_enum'))
    work_mode = Column(Enum('On-site', 'Remote', 'Hybrid', name='work_mode_enum'))
    industry = Column(String(255))
    functional_area = Column(String(255))
    
    # Location and compensation
    job_locations = Column(JSONB)  # Array of strings (City, State)
    min_salary = Column(DECIMAL(10, 2))
    max_salary = Column(DECIMAL(10, 2))
    currency = Column(String(10))  # 'INR', 'USD'
    salary_unit = Column(Enum('YEAR', 'MONTH', 'HOUR', name='salary_unit_enum'))
    benefits_perks = Column(JSONB)  # Array of strings
    
    # Description and requirements
    about_company = Column(Text)
    job_summary = Column(Text)  # Full description
    responsibilities = Column(JSONB)  # Key duties
    experience_required = Column(String(100))  # e.g. "3-5 Years"
    education_qualification = Column(String(255))  # e.g. "B.Tech"
    required_skills = Column(JSONB)  # ["React", "Node"]
    preferred_skills = Column(JSONB)
    tools_tech_stack = Column(JSONB)
    
    # Application and process
    number_of_openings = Column(Integer)
    application_deadline = Column(DATE)
    hiring_process_rounds = Column(JSONB)  # Array of round names e.g. ["Screening", "Tech"]
    notice_period_accepted = Column(String(100))  # e.g. "Immediate to 30 Days"
    
    # SEO and metadata
    slug_url = Column(String(500), unique=True)
    meta_title = Column(String(500))
    meta_description = Column(String(1000))
    
    # Status
    status = Column(Enum('Draft', 'Sourcing', 'Interview', 'Offer', 'Closed', name='job_status_enum'), default='Draft')
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Job(id={self.id}, title={self.title}, client_id={self.client_id})>"