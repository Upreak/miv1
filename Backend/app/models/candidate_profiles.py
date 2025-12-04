from sqlalchemy import Column, String, TIMESTAMP, DECIMAL, DATE, Integer, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from app.core.db import Base
import uuid

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    
    user_id = Column(PG_UUID(as_uuid=True), primary_key=True)  # FK -> users.id
    phone = Column(String)
    linkedin_url = Column(String)
    portfolio_url = Column(String)
    github_url = Column(String)
    resume_url = Column(String)  # Link to the master resume file (S3)
    resume_last_updated = Column(TIMESTAMP)
    bio = Column(String)  # Professional Summary
    is_actively_searching = Column(String)  # Boolean stored as string
    
    # Skills & Education (Section B)
    highest_education = Column(String)
    year_of_passing = Column(Integer)
    skills = Column(JSONB)  # ["React", "TypeScript"]
    certificates = Column(JSONB)  # ["AWS Certified"]
    projects_summary = Column(String)
    ai_skills_vector = Column(String)  # VECTOR for semantic search matching (pgvector)
    
    # Job Preferences (Section C)
    total_experience_years = Column(DECIMAL)
    current_role = Column(String)
    expected_role = Column(String)
    job_type_preference = Column(String)  # Full-time/Contract
    current_locations = Column(JSONB)  # ["Bangalore"]
    preferred_locations = Column(JSONB)  # ["Remote", "Mumbai"]
    ready_to_relocate = Column(String)  # 'Yes', 'No', 'Open to Discussion'
    notice_period = Column(Integer)  # Days
    availability_date = Column(DATE)
    shift_preference = Column(String)  # Day/Night/Flex
    work_authorization = Column(String)
    
    # Salary Info (Section D)
    current_ctc = Column(Integer)
    expected_ctc = Column(Integer)
    currency = Column(String)
    is_ctc_negotiable = Column(String)  # Boolean stored as string
    
    # Personal & Broader Preferences (Section E)
    looking_for_jobs_abroad = Column(String)  # Boolean stored as string
    sector_preference = Column(String)  # Private/Govt
    preferred_industries = Column(JSONB)
    gender = Column(String)
    marital_status = Column(String)
    dob = Column(DATE)
    languages = Column(JSONB)
    reservation_category = Column(String)  # General/OBC/SC/ST
    disability = Column(String)  # Text description or NULL
    willingness_to_travel = Column(String)
    has_driving_license = Column(String)  # Boolean stored as string
    
    # Contact & Availability (Section G)
    has_current_offers = Column(String)  # Boolean stored as string
    number_of_offers = Column(Integer)
    best_time_to_contact = Column(String)
    preferred_contact_mode = Column(String)  # Email/Call/WhatsApp
    alternate_email = Column(String)
    alternate_phone = Column(String)
    time_zone = Column(String)