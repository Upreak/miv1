from sqlalchemy import Column, String, TIMESTAMP, DATE, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.db import Base
import uuid

class ExternalJobPosting(Base):
    __tablename__ = "external_job_postings"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    source = Column(String, nullable=False)  # 'AI_Scraper', 'LinkedIn', 'Indeed'
    original_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    location = Column(String)
    posted_date = Column(DATE)
    summary = Column(String)
    salary_text = Column(String)  # e.g., "$100k - $120k" or "Not Disclosed"
    job_type = Column(String)  # 'Remote', 'Contract', 'Full-time'
    fetched_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    expires_at = Column(TIMESTAMP)  # TTL for cache (e.g., 24 hours)