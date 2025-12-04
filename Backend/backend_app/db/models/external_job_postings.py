"""
External Job Postings Model (Hot Drops)
Persists the "Daily Hot Drops" found by the AI to prevent re-fetching.
"""
from sqlalchemy import Column, String, Text, DATE, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from backend_app.db.connection import Base


class ExternalJobPosting(Base):
    """External job postings model for Hot Drops"""
    
    __tablename__ = "external_job_postings"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Job details
    source = Column(String(100), nullable=False)  # 'AI_Scraper', 'LinkedIn', 'Indeed'
    original_url = Column(Text, nullable=False)
    title = Column(String(500), nullable=False)
    company_name = Column(String(255), nullable=False)
    location = Column(String(255))
    posted_date = Column(DATE)
    summary = Column(Text)
    salary_text = Column(String(255))  # Scraped salary (e.g., "$100k - $120k" or "Not Disclosed")
    job_type = Column(String(100))  # 'Remote', 'Contract', 'Full-time'
    
    # Metadata
    fetched_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    expires_at = Column(TIMESTAMP(timezone=True))  # TTL for cache (e.g., 24 hours)
    
    def __repr__(self):
        return f"<ExternalJobPosting(id={self.id}, title={self.title}, company={self.company_name})>"