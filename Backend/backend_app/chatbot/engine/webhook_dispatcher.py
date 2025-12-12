import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from .validation_utils import validate_email, validate_phone, sanitize_phone
from ...repositories.jobs_repo import JobsRepository
from ...chatbot.services.application_service import ApplicationService

logger = logging.getLogger(__name__)

class WebhookDispatcher:
    def __init__(self, session_service=None, db_session: Session = None):
        """
        Initialize webhook dispatcher.
        
        Args:
            session_service: Chatbot session service
            db_session: Database session for repositories
        """
        self.session_service = session_service
        self.db_session = db_session
        
        # Initialize repositories if db_session is provided
        if db_session:
            self.jobs_repo = JobsRepository(db_session)
            self.application_service = ApplicationService(db_session)
        else:
            self.jobs_repo = None
            self.application_service = None

    async def dispatch(self, call: str, session_id: str, params: Dict, metadata: Dict) -> Optional[str]:
        """
        Dispatch the webhook call to the appropriate handler.
        Returns the name of an event to trigger, or None.
        """
        logger.info(f"Dispatching webhook: {call}")
        
        if call == "check_user_status":
            return await self.check_user_status(session_id, params)
        
        if call == "resume_upload_handler":
            return await self.handle_resume_upload(params, metadata)
        
        if call == "get_candidate_applications":
            return await self.get_candidate_applications(session_id, params)
        
        if call == "get_recommended_jobs":
            return await self.get_recommended_jobs(session_id, params)
        
        if call == "save_job_posting":
            return await self.save_job_posting(params)
        
        if call == "check_recruiter_availability":
            return await self.check_recruiter_availability(params)

        logger.warning(f"Unknown webhook call: {call}")
        return None

    async def check_user_status(self, session_id: str, params: Dict) -> str:
        """
        Check if user is new or returning, and what type.
        Queries database for user profile.
        """
        try:
            # Check session params first (from flow_state)
            if params.get("full_name") or params.get("email"):
                # Check if recruiter
                if params.get("recruiter_name") or params.get("company_name"):
                    return "user_is_returning_recruiter"
                else:
                    return "user_is_returning_candidate"
            
            # If no params, check database via session_service
            # In production: query user table or candidate_profiles by user_id
            # For now, fallback to new user
            return "user_is_new"
        except Exception as e:
            logger.error(f"Error checking user status: {e}")
            return "user_is_new"

    async def get_candidate_applications(self, session_id: str, params: Dict) -> str:
        """
        Fetch candidate's applications from database.
        """
        try:
            candidate_id = params.get("candidate_id") or params.get("user_id")
            
            if not candidate_id:
                logger.warning("No candidate_id found in params")
                return "no_applications"
            
            # Use ApplicationService if available
            if self.application_service and self.db_session:
                # Query applications for this candidate
                # Note: ApplicationService doesn't have get_by_candidate method
                # We'll need to query directly or create the method
                # For now, using mock data with pagination support
                
                applications = [
                    {"job_title": "Frontend Developer", "company": "TechCorp", "status": "Under Review"},
                    {"job_title": "React Engineer", "company": "StartupXYZ", "status": "Interview Scheduled"},
                    {"job_title": "Full Stack Dev", "company": "BigCo", "status": "Application Sent"}
                ]
            else:
                # Fallback to mock data
                applications = [
                    {"job_title": "Frontend Developer", "company": "TechCorp", "status": "Under Review"},
                    {"job_title": "React Engineer", "company": "StartupXYZ", "status": "Interview Scheduled"},
                    {"job_title": "Full Stack Dev", "company": "BigCo", "status": "Application Sent"}
                ]
            
            if applications:
                # Format applications with pagination support
                total_count = len(applications)
                current_page = params.get("applications_page", 0)
                page_size = 5
                
                start_idx = current_page * page_size
                end_idx = start_idx + page_size
                page_apps = applications[start_idx:end_idx]
                
                if page_apps:
                    summary_lines = []
                    for i, app in enumerate(page_apps, start=start_idx + 1):
                        summary_lines.append(
                            f"{i}. {app['job_title']} at {app['company']} - Status: {app['status']}"
                        )
                    
                    params["applications_summary"] = "\n".join(summary_lines)
                    params["applications_total"] = total_count
                    params["applications_page"] = current_page
                    params["applications_has_more"] = end_idx < total_count
                    
                    return "applications_loaded"
                else:
                    return "no_applications"
            else:
                return "no_applications"
        except Exception as e:
            logger.error(f"Error fetching applications: {e}")
            return "no_applications"

    async def get_recommended_jobs(self, session_id: str, params: Dict) -> str:
        """
        Fetch recommended jobs based on candidate profile.
        Uses skills and preferences from params to search jobs.
        """
        try:
            # Extract candidate preferences
            skills = params.get("skills_list", "").split(",") if params.get("skills_list") else []
            location_pref = params.get("location")
            
            # Pagination support
            current_page = params.get("jobs_page", 0)
            page_size = 5
            
            if self.jobs_repo:
                # Use real database query
                all_jobs = self.jobs_repo.search_jobs(
                    keywords=skills if skills else None,
                    location=location_pref,
                    limit=50  # Fetch more for pagination
                )
                
                # Format jobs
                job_list = []
                for job in all_jobs:
                    salary = f" - {job.salary_range}" if hasattr(job, 'salary_range') and job.salary_range else ""
                    job_list.append(
                        f"{job.title} at {job.company} ({job.location}){salary}"
                    )
            else:
                # Fallback to mock data
                job_list = [
                    "Senior Python Developer at AI Corp (Remote) - $120k-150k",
                    "Backend Engineer at DataTech (New York) - $100k-130k",
                    "Full Stack Developer at FinanceApp (Hybrid) - $110k-140k",
                    "DevOps Engineer at CloudSys (Remote) - $115k-145k",
                    "Software Architect at EnterpriseX (San Francisco) - $140k-180k",
                    "React Developer at WebCo (Remote) - $105k-135k",
                    "Python Engineer at MLStartup (Boston) - $110k-145k"
                ]
            
            if job_list:
                # Implement pagination
                total_count = len(job_list)
                start_idx = current_page * page_size
                end_idx = start_idx + page_size
                page_jobs = job_list[start_idx:end_idx]
                
                if page_jobs:
                    params["recommended_jobs"] = "\n".join([f"{i+1}. {job}" for i, job in enumerate(page_jobs, start=start_idx + 1)])
                    params["jobs_total"] = total_count
                    params["jobs_page"] = current_page
                    params["jobs_has_more"] = end_idx < total_count
                    
                    return "jobs_loaded"
                else:
                    return "no_jobs_found"
            else:
                return "no_jobs_found"
        except Exception as e:
            logger.error(f"Error fetching recommendations: {e}")
            return "no_jobs_found"

    async def save_job_posting(self, params: Dict) -> Optional[str]:
        """
        Save recruiter's job posting to database with validation.
        """
        try:
            job_title = params.get("job_title")
            job_location = params.get("job_location")
            job_description = params.get("job_description")
            company_name = params.get("company_name", "Unknown Company")
            recruiter_id = params.get("recruiter_id")
            
            # Validation
            if not job_title or len(job_title) < 3:
                logger.warning("Invalid job title")
                return "validation_failed"
            
            if not job_description or len(job_description) < 10:
                logger.warning("Job description too short")
                return "validation_failed"
            
            logger.info(f"Saving job posting: {job_title} at {company_name}")
            
            # Save to database if repository available
            if self.jobs_repo:
                job = self.jobs_repo.create_job(
                    title=job_title,
                    company=company_name,
                    location=job_location or "Not Specified",
                    description=job_description,
                    recruiter_id=recruiter_id
                )
                params["job_id"] = job.id if hasattr(job, 'id') else None
                logger.info(f"Job created with ID: {params.get('job_id')}")
            else:
                logger.info("No database connection - job posting logged only")
            
            return None  # No event to trigger
        except Exception as e:
            logger.error(f"Error saving job posting: {e}")
            return "save_failed"

    async def handle_resume_upload(self, params: Dict, metadata: Dict) -> str:
        try:
             if metadata and "document" in metadata:
                # Stubbed logic
                # In real app: FileIntakeService.process_file(metadata['document'])
                
                # Mock Results (would come from resume parser)
                extracted_name = "John Doe"
                extracted_email = "john.doe@example.com"
                extracted_phone = "+1-555-0123"
                extracted_education = "B.Tech Computer Science"
                extracted_experience = "4 years"
                extracted_skills = "Python, FastAPI, React"
                
                # Validate extracted data
                if extracted_email and not validate_email(extracted_email):
                    logger.warning(f"Invalid email extracted: {extracted_email}")
                    extracted_email = None
                
                if extracted_phone and not validate_phone(extracted_phone):
                    logger.warning(f"Invalid phone extracted: {extracted_phone}")
                    extracted_phone = None
                else:
                    # Sanitize valid phone
                    extracted_phone = sanitize_phone(extracted_phone) if extracted_phone else None
                
                # Update params with validated data
                if extracted_name:
                    params["full_name"] = extracted_name
                if extracted_email:
                    params["email"] = extracted_email
                if extracted_phone:
                    params["mobile"] = extracted_phone
                if extracted_education:
                    params["highest_education"] = extracted_education
                if extracted_experience:
                    params["total_experience"] = extracted_experience
                if extracted_skills:
                    params["skills"] = extracted_skills
                
                # Return success if we extracted at least name or email
                if extracted_name or extracted_email:
                    return "file_parsed_success"
                else:
                    return "file_parsed_failure"
             
             return "file_parsed_failure"
        except Exception as e:
            logger.error(f"Error in resume handler: {e}")
            return "file_parsed_failure"

    async def check_recruiter_availability(self, params: Dict) -> str:
        # Check if human recruiter is online
        # For now, always fail to test AI fallback
        return "recruiter_unavailable"
