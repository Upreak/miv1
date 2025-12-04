"""
Applications Model
The MOST CRITICAL table for tracking "One Candidate, Multiple Jobs".
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, Integer, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from backend_app.db.connection import Base


class Application(Base):
    """Application model for job applications"""
    
    __tablename__ = "applications"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Application details
    applied_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Job-Specific Tracking
    status = Column(Enum('New', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn', name='application_status_enum'), default='New')
    is_active = Column(Boolean, default=True)  # True if process is ongoing. False if rejected/hired/withdrawn.
    match_score = Column(Integer)  # 0-100. Specific to this job description.
    ai_custom_summary = Column(Text)  # "Candidate matches React requirement but is expensive for this specific budget."
    
    # Automation & Co-Pilot State
    automation_status = Column(Enum('New', 'Contacting...', 'Awaiting Reply', 'Live Chat', 'Intervention Needed', 'Completed', 'Declined', name='automation_status_enum'), default='New')
    is_recruiter_approved = Column(Boolean, default=False)  # Manual override to boost candidate visibility.
    
    # Manual Follow-up Tracking
    follow_up_status = Column(String(100))  # 'Shortlisted', 'Int-scheduled', 'Offered', 'Joined', 'No Show', 'Under Follow-up', 'Rejected'
    next_follow_up_date = Column(DATE)  # For calendar reminders.
    follow_up_remarks = Column(Text)  # Recruiter's internal notes.
    
    def __repr__(self):
        return f"<Application(id={self.id}, job_id={self.job_id}, candidate_id={self.candidate_id}, status={self.status})>"