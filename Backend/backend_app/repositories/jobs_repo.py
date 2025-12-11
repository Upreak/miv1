from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from datetime import datetime

# Implied import based on standard structure
# Adjusting to likely import path
try:
    from backend_app.db.models.jobs import Job
except ImportError:
    try:
        from backend_app.models.jobs import Job
    except ImportError:
        # Fallback if both fail, defining a minimal class for linting to pass 
        # (This will fail at runtime if not found, but we are fixing the repo file)
        pass 

class JobsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, title: str, company: str, location: str, description: str, 
                  job_type: str = "Full-time", salary_range: str = None, 
                  experience_level: str = None, requirements: str = None, 
                  benefits: str = None, recruiter_id: str = None) -> Job:
        
        job = Job(
            title=title,
            company=company,
            location=location,
            description=description,
            job_type=job_type,
            salary_range=salary_range,
            experience_level=experience_level,
            requirements=requirements,
            benefits=benefits,
            recruiter_id=recruiter_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        return self.db.query(Job).filter(Job.id == job_id).first()

    def search_jobs(self, keywords: List[str] = None, location: str = None, 
                   job_type: str = None, limit: int = 10) -> List[Job]:
        query = self.db.query(Job)

        if keywords:
            # Simple keyword search in title or description
            keyword_filters = []
            for keyword in keywords:
                keyword_filters.append(Job.title.ilike(f"%{keyword}%"))
                keyword_filters.append(Job.description.ilike(f"%{keyword}%"))
            query = query.filter(or_(*keyword_filters))

        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))

        if job_type:
            query = query.filter(Job.job_type.ilike(f"%{job_type}%"))

        return query.order_by(desc(Job.created_at)).limit(limit).all()

    def get_all_jobs(self, limit: int = 100) -> List[Job]:
        return self.db.query(Job).order_by(desc(Job.created_at)).limit(limit).all()
