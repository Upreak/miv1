"""
Candidate Profile Model
Stores the "Master Profile" of a user. One user = One Profile. Independent of specific jobs.
"""
from sqlalchemy import Column, String, Text, Integer, DECIMAL, DATE, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from backend_app.db.connection import Base


class CandidateProfile(Base):
    """Candidate profile model for master profile"""
    
    __tablename__ = "candidate_profiles"
    
    # Primary key (One-to-One with User)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    
    # Contact information
    phone = Column(String(20))
    linkedin_url = Column(String(500))
    portfolio_url = Column(String(500))
    github_url = Column(String(500))
    resume_url = Column(String(1000))  # Link to the master resume file (S3)
    resume_last_updated = Column(TIMESTAMP(timezone=True))
    bio = Column(Text)  # Professional Summary
    is_actively_searching = Column(Boolean, default=True)
    
    # Skills & Education (Section B)
    highest_education = Column(String(255))
    year_of_passing = Column(Integer)
    skills = Column(JSONB)  # ["React", "TypeScript"]
    certificates = Column(JSONB)  # ["AWS Certified"]
    projects_summary = Column(Text)
    ai_skills_vector = Column(String(500))  # For semantic search matching (pgvector)
    
    # Job Preferences (Section C)
    total_experience_years = Column(DECIMAL(3, 1))
    current_role = Column(String(255))
    expected_role = Column(String(255))
    job_type_preference = Column(String(100))  # Full-time/Contract
    current_locations = Column(JSONB)  # ["Bangalore"]
    preferred_locations = Column(JSONB)  # ["Remote", "Mumbai"]
    ready_to_relocate = Column(String(50))  # 'Yes', 'No', 'Open to Discussion'
    notice_period = Column(Integer)  # Days
    availability_date = Column(DATE)
    shift_preference = Column(String(100))  # Day/Night/Flex
    work_authorization = Column(String(255))
    
    # Salary Info (Section D)
    current_ctc = Column(DECIMAL(12, 2))
    expected_ctc = Column(DECIMAL(12, 2))
    currency = Column(String(10))
    is_ctc_negotiable = Column(Boolean, default=False)
    
    # Personal & Broader Preferences (Section E)
    looking_for_jobs_abroad = Column(Boolean, default=False)
    sector_preference = Column(String(100))  # Private/Govt
    preferred_industries = Column(JSONB)
    gender = Column(String(50))
    marital_status = Column(String(50))
    dob = Column(DATE)
    languages = Column(JSONB)
    reservation_category = Column(String(50))  # General/OBC/SC/ST
    disability = Column(String(255))  # Text description or NULL
    willingness_to_travel = Column(String(100))
    has_driving_license = Column(Boolean, default=False)
    
    # Contact & Availability (Section G)
    has_current_offers = Column(Boolean, default=False)
    number_of_offers = Column(Integer, default=0)
    best_time_to_contact = Column(String(100))
    preferred_contact_mode = Column(String(100))  # Email/Call/WhatsApp
    alternate_email = Column(String(255))
    alternate_phone = Column(String(20))
    time_zone = Column(String(100))
    
    def __repr__(self):
        return f"<CandidateProfile(user_id={self.user_id})>"