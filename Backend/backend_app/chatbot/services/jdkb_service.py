from typing import List, Dict, Any, Optional
import logging

from ...repositories.jobs_repo import JobsRepository
from ...db.models.jobs import Job

logger = logging.getLogger(__name__)

class JDKBService:
    """
    Job Description Knowledge Base Service.
    Handles interaction with the job repository and matching logic.
    """
    def __init__(self, jobs_repository: JobsRepository):
        self.jobs_repository = jobs_repository

    def search_jobs(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for jobs based on criteria.
        
        Args:
            criteria: Dictionary containing search filters:
                     - keywords: List[str]
                     - location: str
                     - job_type: str
                     
        Returns:
            Dict containing 'jobs' list and metadata.
        """
        try:
            keywords = criteria.get('keywords', [])
            location = criteria.get('location')
            job_type = criteria.get('job_type')
            
            # Use repository to fetch real data
            jobs = self.jobs_repository.search_jobs(
                keywords=keywords,
                location=location,
                job_type=job_type,
                limit=10  # Default limit
            )
            
            # Format results for the skill to consume
            formatted_jobs = []
            for job in jobs:
                formatted_jobs.append({
                    'id': str(job.id),
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'type': job.job_type,
                    'salary': job.salary_range,
                    'experience': job.experience_level,
                    'description': job.description,
                    'match_score': 0, # Placeholder for AI matching score if we implement it later
                    'posted_date': job.created_at.strftime('%Y-%m-%d') if job.created_at else 'N/A'
                })
                
            return {
                'jobs': formatted_jobs,
                'total_count': len(formatted_jobs),
                'search_criteria': criteria,
                'source': 'database' 
            }
            
        except Exception as e:
            logger.error(f"Error in JDKBService search: {e}")
            return {
                'jobs': [],
                'total_count': 0,
                'error': str(e)
            }

    def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Fetch full details for a specific job."""
        try:
            job = self.jobs_repository.get_job_by_id(job_id)
            if not job:
                return None
            
            return {
                'id': str(job.id),
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'type': job.job_type,
                'salary': job.salary_range,
                'experience': job.experience_level,
                'description': job.description,
                'requirements': [job.requirements] if job.requirements else [],
                'benefits': [job.benefits] if job.benefits else []
            }
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return None
