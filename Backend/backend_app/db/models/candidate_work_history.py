"""
Candidate Work History Model (Section F)
"""
from sqlalchemy import Column, String, Text, DATE, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from backend_app.db.connection import Base


class CandidateWorkHistory(Base):
    """Candidate work history model"""
    
    __tablename__ = "candidate_work_history"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True)
    
    # Foreign key to candidate profile
    profile_id = Column(UUID(as_uuid=True), ForeignKey("candidate_profiles.user_id"))
    
    # Work experience details
    company_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE)
    is_current = Column(Boolean, default=False)
    responsibilities = Column(Text)
    tools_used = Column(String(500))  # JSONB as string for simplicity
    ctc_at_role = Column(String(100))
    
    def __repr__(self):
        return f"<CandidateWorkHistory(id={self.id}, company={self.company_name}, title={self.job_title})>"