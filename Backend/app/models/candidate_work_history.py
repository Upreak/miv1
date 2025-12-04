from sqlalchemy import Column, String, TIMESTAMP, DATE, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from app.core.db import Base
import uuid

class CandidateWorkHistory(Base):
    __tablename__ = "candidate_work_history"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK -> candidate_profiles.user_id
    company_name = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE)
    is_current = Column(String)  # Boolean stored as string
    responsibilities = Column(String)
    tools_used = Column(JSONB)  # ["React", "Node.js"]
    ctc_at_role = Column(String)