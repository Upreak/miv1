from sqlalchemy import Column, String, TIMESTAMP, DATE, Integer, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.db import Base
import uuid

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    job_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK -> jobs.id
    candidate_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK -> users.id
    applied_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    
    # Job-Specific Tracking
    status = Column(String)  # 'New', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn'
    is_active = Column(String)  # Boolean stored as string - True if process is ongoing
    match_score = Column(Integer)  # 0-100. Specific to this job description
    ai_custom_summary = Column(String)  # "Candidate matches React requirement but is expensive for this specific budget."
    
    # Automation & Co-Pilot State
    automation_status = Column(String)  # 'New', 'Contacting...', 'Awaiting Reply', 'Live Chat', 'Intervention Needed', 'Completed', 'Declined'
    is_recruiter_approved = Column(String)  # Boolean stored as string - Manual override to boost candidate visibility
    
    # Manual Follow-up Tracking
    follow_up_status = Column(String)  # 'Shortlisted', 'Int-scheduled', 'Offered', 'Joined', 'No Show', 'Under Follow-up', 'Rejected'
    next_follow_up_date = Column(DATE)
    follow_up_remarks = Column(String)