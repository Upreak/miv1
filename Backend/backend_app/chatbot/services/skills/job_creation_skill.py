"""
Job Creation Skill for Chatbot/Co-Pilot Module

Handles job posting creation and management for recruiters.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .base_skill import BaseSkill
from ...models.conversation_state import ConversationState, UserRole
from ...utils.skill_context import SkillContext

logger = logging.getLogger(__name__)


class JobCreationSkill(BaseSkill):
    """
    Job creation skill for handling job posting creation and management.
    
    This skill handles:
    - Job posting creation
    - Job description generation
    - Job requirements collection
    - Job posting validation
    - Job publishing
    """
    
    def __init__(self, jobs_repo=None):
        """Initialize job creation skill."""
        super().__init__(
            name="job_creation_skill",
            description="Handles job posting creation and management for recruiters",
            priority=13
        )
        self.jobs_repo = jobs_repo
        
        # Define response templates
        self.templates = {
            'job_creation_request': "Let's create a job posting! What's the job title?",
            'job_title_request': "What's the job title for this position?",
            'company_request': "What's the company name?",
            'location_request': "What's the job location? (Remote, On-site, or Hybrid)",
            'job_type_request': "What's the job type? (Full-time, Part-time, Contract, Internship)",
            'salary_request': "What's the salary range? (e.g., $50,000 - $80,000)",
            'experience_request': "What's the required experience level? (e.g., 2+ years, Mid-level)",
            'description_request': "Please provide a job description:",
            'requirements_request': "What are the key requirements for this position?",
            'benefits_request': "What benefits are offered with this position?",
            'job_preview': "Here's a preview of your job posting:\n\n{preview}",
            'job_confirmation': "Would you like to post this job? (Yes/No)",
            'job_posted': "Great! Your job has been posted successfully.",
            'job_saved': "Your job posting has been saved as a draft.",
            'job_error': "I encountered an error while creating your job posting. Please try again.",
            'job_help': "I can help you create job postings! Just tell me:\n\n• Job title\n• Company name\n• Location\n• Job type\n• Salary range\n• Experience level\n• Job description\n• Requirements\n• Benefits",
            'job_draft_saved': "Your job draft has been saved. You can continue editing later.",
            'job_published': "Your job has been published and is now live!",
            'job_validation_error': "Please provide all required information before posting.",
            'job_fields_missing': "The following fields are required: {fields}"
        }
    
    def can_handle(self, state: ConversationState, message: str, 
                  context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if this skill can handle the current state and message.
        
        Args:
            state: Current conversation state
            message: User message
            context: Additional context
            
        Returns:
            bool: True if skill can handle, False otherwise
        """
        try:
            # Handle job creation state
            if state == ConversationState.JOB_CREATION:
                return True
            
            # Handle recruiter flow state
            if state == ConversationState.RECRUITER_FLOW:
                return True
            
            # Handle messages that indicate job creation intent
            if context:
                user_role = context.get('user_role', 'unknown')
                if user_role == 'recruiter':
                    # Check for job creation keywords
                    job_keywords = [
                        'create job', 'post job', 'new job', 'job posting', 'vacancy',
                        'opening', 'position', 'role', 'hire', 'recruit', 'employment'
                    ]
                    
                    if any(keyword in message.lower() for keyword in job_keywords):
                        return True
                    
                    # Check for specific job creation phrases
                    if any(phrase in message.lower() for phrase in 
                          ['create new job', 'post new job', 'add job', 'new position']):
                        return True
            
            # Handle idle state with job creation intent
            if state == ConversationState.IDLE:
                if context and context.get('user_role') == 'recruiter':
                    job_keywords = [
                        'create job', 'post job', 'new job', 'job posting', 'vacancy',
                        'opening', 'position', 'role', 'hire', 'recruit', 'employment'
                    ]
                    
                    if any(keyword in message.lower() for keyword in job_keywords):
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if job creation skill can handle: {e}")
            return False
    
    async def handle(self, sid: str, message: str, 
              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle the message and return response.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Skill response
        """
        try:
            # Get session state
            state = self._get_session_state_from_context(context)
            
            # Handle based on state
            if state == ConversationState.JOB_CREATION:
                return self._handle_job_creation(sid, message, context)
            elif state == ConversationState.RECRUITER_FLOW:
                return self._handle_recruiter_flow(sid, message, context)
            elif state == ConversationState.IDLE:
                return self._handle_job_request(sid, message, context)
            else:
                return self._handle_fallback(sid, message, context)
                
        except Exception as e:
            logger.error(f"Error in job creation skill handle: {e}")
            return self._create_error_response(str(e))
    
    def _handle_job_creation(self, sid: str, message: str, 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle job creation process.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Get current job creation step
            current_step = context.get('job_creation_step', 'title') if context else 'title'
            
            # Handle based on current step
            if current_step == 'title':
                return self._handle_job_title(sid, message, context)
            elif current_step == 'company':
                return self._handle_company_name(sid, message, context)
            elif current_step == 'location':
                return self._handle_job_location(sid, message, context)
            elif current_step == 'job_type':
                return self._handle_job_type(sid, message, context)
            elif current_step == 'salary':
                return self._handle_salary_range(sid, message, context)
            elif current_step == 'experience':
                return self._handle_experience_level(sid, message, context)
            elif current_step == 'description':
                return self._handle_job_description(sid, message, context)
            elif current_step == 'requirements':
                return self._handle_job_requirements(sid, message, context)
            elif current_step == 'benefits':
                return self._handle_job_benefits(sid, message, context)
            elif current_step == 'preview':
                return self._handle_job_preview(sid, message, context)
            elif current_step == 'confirmation':
                return self._handle_job_confirmation(sid, message, context)
            else:
                return self._handle_fallback(sid, message, context)
                
        except Exception as e:
            logger.error(f"Error handling job creation: {e}")
            return self._create_error_response(str(e))
    
    def _handle_job_title(self, sid: str, message: str, 
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle job title collection.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Validate job title
            if len(message.strip()) < 2:
                return self._create_success_response(
                    text="Please enter a valid job title.",
                    intent="job_title_validation_error",
                    metadata={
                        'next_state': ConversationState.JOB_CREATION,
                        'job_creation_step': 'title'
                    }
                )
            
            # Store job title in context
            if context:
                context['job_title'] = message.strip()
                context['job_creation_step'] = 'company'
            
            # Log execution
            self._log_execution(sid, message, True)
            
            # Request company name
            return self._create_success_response(
                text=self.templates['company_request'],
                intent="job_title_collected",
                metadata={
                    'job_title': message.strip(),
                    'next_state': ConversationState.JOB_CREATION,
                    'job_creation_step': 'company'
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling job title: {e}")
            return self._create_error_response(str(e))
    
    def _handle_company_name(self, sid: str, message: str, 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle company name collection.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Validate company name
            if len(message.strip()) < 2:
                return self._create_success_response(
                    text="Please enter a valid company name.",
                    intent="company_name_validation_error",
                    metadata={
                        'next_state': ConversationState.JOB_CREATION,
                        'job_creation_step': 'company'
                    }
                )
            
            # Store company name in context
            if context:
                context['company_name'] = message.strip()
                context['job_creation_step'] = 'location'
            
            # Log execution
            self._log_execution(sid, message, True)
            
            # Request location
            return self._create_success_response(
                text=self.templates['location_request'],
                intent="company_name_collected",
                metadata={
                    'company_name': message.strip(),
                    'next_state': ConversationState.JOB_CREATION,
                    'job_creation_step': 'location'
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling company name: {e}")
            return self._create_error_response(str(e))
    
    def _handle_job_location(self, sid: str, message: str, 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle job location collection.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Validate location
            message_lower = message.lower()
            valid_locations = ['remote', 'on-site', 'onsite', 'hybrid', 'in office']
            
            if not any(loc in message_lower for loc in valid_locations):
                return self._create_success_response(
                    text="Please enter a valid location (Remote, On-site, or Hybrid).",
                    intent="location_validation_error",
                    metadata={
                        'next_state': ConversationState.JOB_CREATION,
                        'job_creation_step': 'location'
                    }
                )
            
            # Store location in context
            if context:
                context['job_location'] = message.strip()
                context['job_creation_step'] = 'job_type'
            
            # Log execution
            self._log_execution(sid, message, True)
            
            # Request job type
            return self._create_success_response(
                text=self.templates['job_type_request'],
                intent="job_location_collected",
                metadata={
                    'job_location': message.strip(),
                    'next_state': ConversationState.JOB_CREATION,
                    'job_creation_step': 'job_type'
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling job location: {e}")
            return self._create_error_response(str(e))
    
    def _handle_job_type(self, sid: str, message: str, 
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle job type collection.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Validate job type
            message_lower = message.lower()
            valid_job_types = ['full-time', 'part-time', 'contract', 'internship', 'freelance']
            
            if not any(job_type in message_lower for job_type in valid_job_types):
                return self._create_success_response(
                    text="Please enter a valid job type (Full-time, Part-time, Contract, Internship).",
                    intent="job_type_validation_error",
                    metadata={
                        'next_state': ConversationState.JOB_CREATION,
                        'job_creation_step': 'job_type'
                    }
                )
            
            # Store job type in context
            if context:
                context['job_type'] = message.strip()
                context['job_creation_step'] = 'salary'
            
            # Log execution
            self._log_execution(sid, message, True)
            
            # Request salary range
            return self._create_success_response(
                text=self.templates['salary_request'],
                intent="job_type_collected",
                metadata={
                    'job_type': message.strip(),
                    'next_state': ConversationState.JOB_CREATION,
                    'job_creation_step': 'salary'
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling job type: {e}")
            return self._create_error_response(str(e))
    
    def _handle_salary_range(self, sid: str, message: str, 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle salary range collection.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Validate salary range (basic validation)
            if '$' not in message or len(message.strip()) < 5:
                return self._create_success_response(
                    text="Please enter a valid salary range (e.g., $50,000 - $80,000).",
                    intent="salary_validation_error",
                    metadata={
                        'next_state': ConversationState.JOB_CREATION,
                        'job_creation_step': 'salary'
                    }
                )
            
            # Store salary range in context
            if context:
                context['salary_range'] = message.strip()
                context['job_creation_step'] = 'experience'
            
            # Log execution
            self._log_execution(sid, message, True)
            
            # Request experience level
            return self._create_success_response(
                text=self.templates['experience_request'],
                intent="salary_range_collected",
                metadata={
                    'salary_range': message.strip(),
                    'next_state': ConversationState.JOB_CREATION,
                    'job_creation_step': 'experience'
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling salary range: {e}")
            return self._create_error_response(str(e))
    
    def _handle_experience_level(self, sid: str, message: str, 
                               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle experience level collection.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Validate experience level
            if len(message.strip()) < 2:
                return self._create_success_response(
                    text="Please enter a valid experience level.",
                    intent="experience_validation_error",
                    metadata={
                        'next_state': ConversationState.JOB_CREATION,
                        'job_creation_step': 'experience'
                    }
                )
            
            # Store experience level in context
            if context:
                context['experience_level'] = message.strip()
                context['job_creation_step'] = 'description'
            
            # Log execution
            self._log_execution(sid, message, True)
            
            # Request job description
            return self._create_success_response(
                text=self.templates['description_request'],
                intent="experience_level_collected",
                metadata={
                    'experience_level': message.strip(),
                    'next_state': ConversationState.JOB_CREATION,
                    'job_creation_step': 'description'
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling experience level: {e}")
            return self._create_error_response(str(e))
    
    def _handle_job_description(self, sid: str, message: str, 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle job description collection.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Validate job description
            if len(message.strip()) < 20:
                return self._create_success_response(
                    text="Please provide a more detailed job description.",
                    intent="description_validation_error",
                    metadata={
                        'next_state': ConversationState.JOB_CREATION,
                        'job_creation_step': 'description'
                    }
                )
            
            # Store job description in context
            if context:
                context['job_description'] = message.strip()
                context['job_creation_step'] = 'requirements'
            
            # Log execution
            self._log_execution(sid, message, True)
            
            # Request job requirements
            return self._create_success_response(
                text=self.templates['requirements_request'],
                intent="job_description_collected",
                metadata={
                    'job_description': message.strip(),
                    'next_state': ConversationState.JOB_CREATION,
                    'job_creation_step': 'requirements'
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling job description: {e}")
            return self._create_error_response(str(e))
    
    def _handle_job_requirements(self, sid: str, message: str, 
                               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle job requirements collection.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Validate job requirements
            if len(message.strip()) < 10:
                return self._create_success_response(
                    text="Please provide more detailed job requirements.",
                    intent="requirements_validation_error",
                    metadata={
                        'next_state': ConversationState.JOB_CREATION,
                        'job_creation_step': 'requirements'
                    }
                )
            
            # Store job requirements in context
            if context:
                context['job_requirements'] = message.strip()
                context['job_creation_step'] = 'benefits'
            
            # Log execution
            self._log_execution(sid, message, True)
            
            # Request job benefits
            return self._create_success_response(
                text=self.templates['benefits_request'],
                intent="job_requirements_collected",
                metadata={
                    'job_requirements': message.strip(),
                    'next_state': ConversationState.JOB_CREATION,
                    'job_creation_step': 'benefits'
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling job requirements: {e}")
            return self._create_error_response(str(e))
    
    def _handle_job_benefits(self, sid: str, message: str, 
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle job benefits collection.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Store job benefits in context
            if context:
                context['job_benefits'] = message.strip()
                context['job_creation_step'] = 'preview'
            
            # Log execution
            self._log_execution(sid, message, True)
            
            # Generate job preview
            job_preview = self._generate_job_preview(context)
            
            # Request preview confirmation
            return self._create_success_response(
                text=self.templates['job_preview'].format(preview=job_preview),
                intent="job_benefits_collected",
                metadata={
                    'job_benefits': message.strip(),
                    'job_preview': job_preview,
                    'next_state': ConversationState.JOB_CREATION,
                    'job_creation_step': 'preview'
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling job benefits: {e}")
            return self._create_error_response(str(e))
    
    def _handle_job_preview(self, sid: str, message: str, 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle job preview.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Store job preview in context
            if context:
                context['job_creation_step'] = 'confirmation'
            
            # Log execution
            self._log_execution(sid, message, True)
            
            # Request confirmation
            return self._create_success_response(
                text=self.templates['job_confirmation'],
                intent="job_preview_ready",
                metadata={
                    'next_state': ConversationState.JOB_CREATION,
                    'job_creation_step': 'confirmation'
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling job preview: {e}")
            return self._create_error_response(str(e))
    
    def _handle_job_confirmation(self, sid: str, message: str, 
                                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle job confirmation.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Check for confirmation
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['yes', 'y', 'post', 'publish']):
                # Post the job
                post_result = self._post_job(sid, context)
                
                if post_result['success']:
                    # Log execution
                    self._log_execution(sid, message, True)
                    
                    return self._create_success_response(
                        text=self.templates['job_posted'],
                        intent="job_posted",
                        metadata={
                            'job_posted': True,
                            'job_id': post_result.get('job_id'),
                            'next_state': ConversationState.IDLE,
                            'job_complete': True
                        }
                    )
                else:
                    return self._create_success_response(
                        text=self.templates['job_error'],
                        intent="job_post_error",
                        metadata={
                            'next_state': ConversationState.IDLE,
                            'job_complete': False,
                            'error': post_result.get('error', 'Unknown error')
                        }
                    )
            else:
                # Save as draft
                draft_result = self._save_job_draft(sid, context)
                
                if draft_result['success']:
                    # Log execution
                    self._log_execution(sid, message, True)
                    
                    return self._create_success_response(
                        text=self.templates['job_saved'],
                        intent="job_draft_saved",
                        metadata={
                            'job_draft_saved': True,
                            'job_id': draft_result.get('job_id'),
                            'next_state': ConversationState.IDLE,
                            'job_complete': True
                        }
                    )
                else:
                    return self._create_success_response(
                        text=self.templates['job_error'],
                        intent="job_save_error",
                        metadata={
                            'next_state': ConversationState.IDLE,
                            'job_complete': False,
                            'error': draft_result.get('error', 'Unknown error')
                        }
                    )
                    
        except Exception as e:
            logger.error(f"Error handling job confirmation: {e}")
            return self._create_error_response(str(e))
    
    def _handle_recruiter_flow(self, sid: str, message: str, 
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle recruiter flow.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Check for job creation intent
            if any(keyword in message.lower() for keyword in ['create job', 'post job', 'new job']):
                return self._handle_job_request(sid, message, context)
            
            # Check for job management intent
            if any(keyword in message.lower() for keyword in ['edit job', 'update job', 'manage jobs']):
                return self._create_success_response(
                    text="Job management features coming soon! For now, you can create new job postings.",
                    intent="job_management_coming_soon",
                    metadata={
                        'next_state': ConversationState.IDLE
                    }
                )
            
            # Default to job creation
            return self._handle_job_request(sid, message, context)
            
        except Exception as e:
            logger.error(f"Error handling recruiter flow: {e}")
            return self._create_error_response(str(e))
    
    def _handle_job_request(self, sid: str, message: str, 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle job request in idle state.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Transition to job creation state
            return self._create_success_response(
                text=self.templates['job_creation_request'],
                intent="job_creation_request",
                metadata={
                    'next_state': ConversationState.JOB_CREATION,
                    'job_creation_step': 'title',
                    'requires_job_creation': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling job request: {e}")
            return self._create_error_response(str(e))
    
    def _generate_job_preview(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate job preview from collected data.
        
        Args:
            context: Context with job data
            
        Returns:
            str: Job preview
        """
        try:
            if not context:
                return "No job data available."
            
            preview = f"**{context.get('job_title', 'Job Title')}**\n\n"
            preview += f"🏢 **{context.get('company_name', 'Company Name')}**\n"
            preview += f"📍 {context.get('job_location', 'Location')} | 💼 {context.get('job_type', 'Job Type')}\n"
            preview += f"💰 {context.get('salary_range', 'Salary Range')} | 🎓 {context.get('experience_level', 'Experience Level')}\n\n"
            preview += f"**Description:**\n{context.get('job_description', 'Job description not provided.')}\n\n"
            preview += f"**Requirements:**\n{context.get('job_requirements', 'Requirements not provided.')}\n\n"
            preview += f"**Benefits:**\n{context.get('job_benefits', 'Benefits not provided.')}\n"
            
            return preview
            
        except Exception as e:
            logger.error(f"Error generating job preview: {e}")
            return "Error generating job preview."
    
    def _post_job(self, sid: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Post job to the system.
        
        Args:
            sid: Session ID
            context: Context with job data
            
        Returns:
            Dict[str, Any]: Post result
        """
        try:
            # This would integrate with the existing job posting system
            # For now, simulate posting
            
            # Store job data (mock default)
            job_data = {
                'id': f"job_{datetime.utcnow().timestamp()}",
                'title': context.get('job_title', ''),
                'company': context.get('company_name', ''),
            }

            if self.jobs_repo:
                job = self.jobs_repo.create_job(
                    title=context.get('job_title', ''),
                    company=context.get('company_name', ''),
                    location=context.get('job_location', ''),
                    description=context.get('job_description', ''),
                    job_type=context.get('job_type', 'Full-time'),
                    salary_range=context.get('salary_range'),
                    experience_level=context.get('experience_level'),
                    requirements=context.get('job_requirements'),
                    benefits=context.get('job_benefits'),
                    recruiter_id=sid # or context.get('user_id') if available
                )
                job_id = str(job.id)
                job_data = {
                    'id': job_id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'status': 'active'
                }
                logger.info(f"Persisted job {job_id} to DB")
            else:
                # Fallback to mock
                import uuid
                job_id = f"job_{uuid.uuid4().hex[:8]}"
                job_data['id'] = job_id
            
            return {
                'success': True,
                'job_id': job_id,
                'job_data': job_data
            }
            
        except Exception as e:
            logger.error(f"Error posting job: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_job_draft(self, sid: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Save job draft.
        
        Args:
            sid: Session ID
            context: Context with job data
            
        Returns:
            Dict[str, Any]: Save result
        """
        try:
            # This would integrate with the existing job draft system
            # For now, simulate saving
            
            # Generate mock draft ID
            import uuid
            draft_id = f"draft_{uuid.uuid4().hex[:8]}"
            
            # Store draft data (mock)
            draft_data = {
                'id': draft_id,
                'title': context.get('job_title', ''),
                'company': context.get('company_name', ''),
                'location': context.get('job_location', ''),
                'type': context.get('job_type', ''),
                'salary': context.get('salary_range', ''),
                'experience': context.get('experience_level', ''),
                'description': context.get('job_description', ''),
                'requirements': context.get('job_requirements', ''),
                'benefits': context.get('job_benefits', ''),
                'created_date': datetime.utcnow().isoformat(),
                'status': 'draft',
                'created_by': sid
            }
            
            # Log draft saving
            logger.info(f"Job draft saved: {draft_id}")
            
            return {
                'success': True,
                'job_id': draft_id,
                'job_data': draft_data
            }
            
        except Exception as e:
            logger.error(f"Error saving job draft: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _handle_fallback(self, sid: str, message: str, 
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle fallback cases.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        # Log execution
        self._log_execution(sid, message, False, error="Fallback handling")
        
        return self._create_fallback_response(
            text="I'm not sure how to help with job creation. Please try describing what type of job you'd like to create."
        )
    
    def get_handled_states(self) -> List[ConversationState]:
        """
        Get list of states this skill can handle.
        
        Returns:
            List[ConversationState]: List of handled states
        """
        return [
            ConversationState.JOB_CREATION,
            ConversationState.RECRUITER_FLOW,
            ConversationState.IDLE
        ]
    
    def get_required_fields(self) -> List[str]:
        """
        Get list of required context fields.
        
        Returns:
            List[str]: List of required field names
        """
        return ['sid', 'message', 'user_role']
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """
        Get validation rules for context fields.
        
        Returns:
            Dict[str, Any]: Validation rules
        """
        return {
            'user_role': lambda x: x == 'recruiter'
        }
    
    def get_response_templates(self) -> Dict[str, str]:
        """
        Get response templates for different scenarios.
        
        Returns:
            Dict[str, str]: Response templates
        """
        return self.templates
    
    def _get_session_state_from_context(self, context: Dict[str, Any]) -> ConversationState:
        """
        Get session state from context.
        
        Args:
            context: Context dictionary
            
        Returns:
            ConversationState: Session state
        """
        if not context:
            return ConversationState.IDLE
        
        state_str = context.get('session_state', 'idle')
        try:
            return ConversationState(state_str)
        except ValueError:
            return ConversationState.IDLE
    
    def _create_success_response(self, text: str, 
                               intent: str = "success",
                               metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create success response.
        
        Args:
            text: Success message
            intent: Success intent
            metadata: Additional metadata
            
        Returns:
            Dict[str, Any]: Success response
        """
        response = {
            'text': text,
            'intent': intent,
            'confidence': 0.9,
            'timestamp': datetime.utcnow().isoformat(),
            'skill_used': self.name,
            'metadata': metadata or {}
        }
        
        # Add next state if specified
        if 'next_state' in metadata:
            response['next_state'] = metadata['next_state']
        
        return response
    
    def _create_error_response(self, error_message: str, 
                             intent: str = "error") -> Dict[str, Any]:
        """
        Create error response.
        
        Args:
            error_message: Error message
            intent: Error intent
            
        Returns:
            Dict[str, Any]: Error response
        """
        return {
            'text': f"I'm sorry, I encountered an error: {error_message}",
            'intent': intent,
            'confidence': 0.0,
            'timestamp': datetime.utcnow().isoformat(),
            'skill_used': self.name,
            'metadata': {'error': error_message}
        }
    
    def _create_fallback_response(self, text: str = None) -> Dict[str, Any]:
        """
        Create fallback response.
        
        Args:
            text: Fallback message
            
        Returns:
            Dict[str, Any]: Fallback response
        """
        if text is None:
            text = "I'm not sure how to help with job creation. Please try describing what type of job you'd like to create."
        
        return {
            'text': text,
            'intent': 'fallback',
            'confidence': 0.3,
            'timestamp': datetime.utcnow().isoformat(),
            'skill_used': self.name
        }
    
    def _log_execution(self, sid: str, message: str, success: bool, 
                      response: Dict[str, Any] = None, error: str = None) -> None:
        """
        Log skill execution.
        
        Args:
            sid: Session ID
            message: User message
            success: Whether execution was successful
            response: Skill response
            error: Error message if any
        """
        try:
            self.execution_count += 1
            
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
            
            # Log execution details
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'skill': self.name,
                'sid': sid,
                'message': message,
                'success': success,
                'response': response,
                'error': error
            }
            
            logger.info(f"Skill execution: {log_entry}")
            
        except Exception as e:
            logger.error(f"Error logging skill execution: {e}")
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics.
        
        Returns:
            Dict[str, Any]: Execution statistics
        """
        return {
            'name': self.name,
            'total_executions': self.execution_count,
            'successful_executions': self.success_count,
            'error_executions': self.error_count,
            'success_rate': (self.success_count / max(self.execution_count, 1)) * 100,
            'created_at': self.created_at.isoformat()
        }