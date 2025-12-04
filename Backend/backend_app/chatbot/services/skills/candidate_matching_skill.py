"""
Candidate Matching Skill for Chatbot/Co-Pilot Module

Handles job matching, recommendations, and search for candidates.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .base_skill import BaseSkill
from ...models.conversation_state import ConversationState, UserRole
from ...utils.skill_context import SkillContext

logger = logging.getLogger(__name__)


class CandidateMatchingSkill(BaseSkill):
    """
    Candidate matching skill for finding and recommending jobs.
    
    This skill handles:
    - Job search requests
    - Job matching algorithms
    - Job recommendations
    - Search filters
    - Application suggestions
    """
    
    def __init__(self):
        """Initialize candidate matching skill."""
        super().__init__(
            name="candidate_matching_skill",
            description="Handles job matching, recommendations, and search for candidates",
            priority=12
        )
        
        # Define response templates
        self.templates = {
            'job_search_request': "What type of job are you looking for? Please describe your ideal position.",
            'job_search_help': "I can help you find jobs! Tell me:\n\n• Job title or role\n• Industry or field\n• Location preferences\n• Experience level\n• Skills or technologies",
            'search_processing': "Searching for jobs that match your profile...",
            'search_results': "I found {count} jobs that match your profile:\n\n{jobs}",
            'no_results': "I couldn't find any jobs that match your current profile. Would you like to:\n\n1. Adjust your search criteria\n2. Update your profile\n3. Browse all jobs",
            'job_details': "Here are the details for this job:\n\n{details}",
            'apply_request': "Would you like to apply for this job? (Yes/No)",
            'application_success': "Great! Your application has been submitted successfully.",
            'application_error': "I encountered an error while submitting your application. Please try again.",
            'recommendation_request': "Based on your profile, here are my top recommendations:\n\n{recommendations}",
            'profile_update_needed': "To get better job matches, I recommend updating your profile with more details about your skills and experience.",
            'search_filters': "Let me help you refine your search. What are your preferences?\n\n• Location: {location}\n• Experience: {experience}\n• Salary range: {salary}\n• Job type: {job_type}"
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
            # Handle matching state
            if state == ConversationState.MATCHING:
                return True
            
            # Handle candidate flow state
            if state == ConversationState.CANDIDATE_FLOW:
                return True
            
            # Handle messages that indicate job search intent
            if context:
                user_role = context.get('user_role', 'unknown')
                if user_role == 'candidate':
                    # Check for job-related keywords
                    job_keywords = [
                        'job', 'jobs', 'work', 'position', 'role', 'career', 'employment',
                        'find job', 'search job', 'looking for job', 'job search',
                        'apply', 'application', 'opportunity', 'vacancy', 'opening'
                    ]
                    
                    if any(keyword in message.lower() for keyword in job_keywords):
                        return True
                    
                    # Check for specific job search phrases
                    if any(phrase in message.lower() for phrase in 
                          ['find jobs', 'search jobs', 'job recommendations', 'matching jobs']):
                        return True
            
            # Handle idle state with job search intent
            if state == ConversationState.IDLE:
                if context and context.get('user_role') == 'candidate':
                    job_keywords = [
                        'job', 'jobs', 'work', 'position', 'role', 'career', 'employment',
                        'find job', 'search job', 'looking for job', 'job search',
                        'apply', 'application', 'opportunity', 'vacancy', 'opening'
                    ]
                    
                    if any(keyword in message.lower() for keyword in job_keywords):
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if candidate matching skill can handle: {e}")
            return False
    
    def handle(self, sid: str, message: str, 
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
            if state == ConversationState.MATCHING:
                return self._handle_job_search(sid, message, context)
            elif state == ConversationState.CANDIDATE_FLOW:
                return self._handle_candidate_flow(sid, message, context)
            elif state == ConversationState.IDLE:
                return self._handle_job_request(sid, message, context)
            else:
                return self._handle_fallback(sid, message, context)
                
        except Exception as e:
            logger.error(f"Error in candidate matching skill handle: {e}")
            return self._create_error_response(str(e))
    
    def _handle_job_search(self, sid: str, message: str, 
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle job search.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Extract search criteria from message
            search_criteria = self._extract_search_criteria(message, context)
            
            # Validate profile completeness
            if not self._is_profile_complete(context):
                return self._create_success_response(
                    text=self.templates['profile_update_needed'],
                    intent="profile_update_needed",
                    metadata={
                        'next_state': ConversationState.IDLE,
                        'profile_complete': False
                    }
                )
            
            # Search for jobs
            search_results = self._search_jobs(sid, search_criteria, context)
            
            # Log execution
            self._log_execution(sid, message, True)
            
            if search_results['jobs']:
                return self._create_success_response(
                    text=self.templates['search_results'].format(
                        count=len(search_results['jobs']),
                        jobs=self._format_job_list(search_results['jobs'])
                    ),
                    intent="job_search_results",
                    metadata={
                        'search_results': search_results,
                        'job_count': len(search_results['jobs']),
                        'next_state': ConversationState.IDLE,
                        'search_complete': True
                    }
                )
            else:
                return self._create_success_response(
                    text=self.templates['no_results'],
                    intent="no_job_results",
                    metadata={
                        'search_criteria': search_criteria,
                        'next_state': ConversationState.IDLE,
                        'search_complete': True
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling job search: {e}")
            return self._create_error_response(str(e))
    
    def _handle_candidate_flow(self, sid: str, message: str, 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle candidate flow.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Check for job application intent
            if any(keyword in message.lower() for keyword in ['apply', 'application', 'submit']):
                return self._handle_application_request(sid, message, context)
            
            # Check for job details request
            if any(keyword in message.lower() for keyword in ['details', 'more info', 'tell me more']):
                return self._handle_job_details_request(sid, message, context)
            
            # Default to job search
            return self._handle_job_search(sid, message, context)
            
        except Exception as e:
            logger.error(f"Error handling candidate flow: {e}")
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
            # Check if user has a complete profile
            if not self._is_profile_complete(context):
                return self._create_success_response(
                    text="To help you find the best job matches, I'll need to create your profile first. Would you like to upload your resume?",
                    intent="profile_needed",
                    metadata={
                        'next_state': ConversationState.AWAITING_RESUME,
                        'profile_complete': False
                    }
                )
            
            # Transition to matching state
            return self._create_success_response(
                text=self.templates['job_search_request'],
                intent="job_search_request",
                metadata={
                    'next_state': ConversationState.MATCHING,
                    'requires_search_criteria': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling job request: {e}")
            return self._create_error_response(str(e))
    
    def _extract_search_criteria(self, message: str, 
                               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract search criteria from message.
        
        Args:
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Search criteria
        """
        try:
            criteria = {
                'keywords': [],
                'location': None,
                'experience_level': None,
                'salary_range': None,
                'job_type': None,
                'industry': None
            }
            
            message_lower = message.lower()
            
            # Extract keywords
            job_keywords = ['developer', 'engineer', 'manager', 'designer', 'analyst', 
                          'coordinator', 'specialist', 'associate', 'senior', 'junior']
            
            for keyword in job_keywords:
                if keyword in message_lower:
                    criteria['keywords'].append(keyword)
            
            # Extract location
            location_keywords = ['remote', 'hybrid', 'onsite', 'in office', 'location', 'city']
            for keyword in location_keywords:
                if keyword in message_lower:
                    criteria['location'] = keyword
            
            # Extract experience level
            experience_keywords = ['entry', 'junior', 'mid', 'senior', 'lead', 'principal']
            for keyword in experience_keywords:
                if keyword in message_lower:
                    criteria['experience_level'] = keyword
            
            # Extract job type
            job_type_keywords = ['full-time', 'part-time', 'contract', 'freelance', 'internship']
            for keyword in job_type_keywords:
                if keyword in message_lower:
                    criteria['job_type'] = keyword
            
            # Extract industry
            industry_keywords = ['tech', 'technology', 'software', 'it', 'finance', 'healthcare', 'education']
            for keyword in industry_keywords:
                if keyword in message_lower:
                    criteria['industry'] = keyword
            
            return criteria
            
        except Exception as e:
            logger.error(f"Error extracting search criteria: {e}")
            return {}
    
    def _is_profile_complete(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if user profile is complete.
        
        Args:
            context: Context with user information
            
        Returns:
            bool: True if profile is complete
        """
        if not context:
            return False
        
        required_fields = ['user_name', 'user_email', 'profile_ready']
        return all(field in context for field in required_fields)
    
    def _search_jobs(self, sid: str, criteria: Dict[str, Any], 
                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for jobs based on criteria.
        
        Args:
            sid: Session ID
            criteria: Search criteria
            context: Additional context
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            # This would integrate with the existing job search system
            # For now, return mock results
            
            mock_jobs = [
                {
                    'id': 'job_1',
                    'title': 'Senior Software Engineer',
                    'company': 'TechCorp Inc.',
                    'location': 'San Francisco, CA',
                    'type': 'Full-time',
                    'experience': '5+ years',
                    'salary': '$120,000 - $180,000',
                    'description': 'We are looking for a senior software engineer to join our team...',
                    'match_score': 95,
                    'posted_date': '2024-01-15'
                },
                {
                    'id': 'job_2',
                    'title': 'Full Stack Developer',
                    'company': 'StartupXYZ',
                    'location': 'Remote',
                    'type': 'Full-time',
                    'experience': '3+ years',
                    'salary': '$90,000 - $130,000',
                    'description': 'Join our innovative team as a full stack developer...',
                    'match_score': 88,
                    'posted_date': '2024-01-14'
                },
                {
                    'id': 'job_3',
                    'title': 'Python Developer',
                    'company': 'DataTech Solutions',
                    'location': 'New York, NY',
                    'type': 'Contract',
                    'experience': '2+ years',
                    'salary': '$80,000 - $120,000',
                    'description': 'Seeking a Python developer for data processing projects...',
                    'match_score': 82,
                    'posted_date': '2024-01-13'
                }
            ]
            
            # Filter jobs based on criteria (mock filtering)
            filtered_jobs = mock_jobs
            
            # Sort by match score
            filtered_jobs.sort(key=lambda x: x['match_score'], reverse=True)
            
            return {
                'jobs': filtered_jobs,
                'total_count': len(filtered_jobs),
                'search_criteria': criteria,
                'search_time': 0.5
            }
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return {
                'jobs': [],
                'total_count': 0,
                'search_criteria': criteria,
                'search_time': 0.0,
                'error': str(e)
            }
    
    def _format_job_list(self, jobs: List[Dict[str, Any]]) -> str:
        """
        Format job list for display.
        
        Args:
            jobs: List of jobs
            
        Returns:
            str: Formatted job list
        """
        try:
            if not jobs:
                return "No jobs found."
            
            formatted_jobs = []
            for i, job in enumerate(jobs[:5], 1):  # Show max 5 jobs
                job_text = f"{i}. **{job['title']}** at {job['company']}\n"
                job_text += f"   📍 {job['location']} | 💰 {job['salary']}\n"
                job_text += f"   📊 Match: {job['match_score']}% | 📅 Posted: {job['posted_date']}\n"
                job_text += f"   📝 {job['description'][:100]}...\n"
                formatted_jobs.append(job_text)
            
            return "\n".join(formatted_jobs)
            
        except Exception as e:
            logger.error(f"Error formatting job list: {e}")
            return "Error formatting job results."
    
    def _handle_application_request(self, sid: str, message: str, 
                                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle job application request.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # This would integrate with the existing application system
            # For now, simulate application
            
            # Log execution
            self._log_execution(sid, message, True)
            
            return self._create_success_response(
                text=self.templates['application_success'],
                intent="application_submitted",
                metadata={
                    'application_submitted': True,
                    'next_state': ConversationState.IDLE,
                    'application_complete': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling application request: {e}")
            return self._create_success_response(
                text=self.templates['application_error'],
                intent="application_error",
                metadata={
                    'next_state': ConversationState.IDLE,
                    'application_complete': False
                }
            )
    
    def _handle_job_details_request(self, sid: str, message: str, 
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle job details request.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Mock job details
            job_details = {
                'id': 'job_1',
                'title': 'Senior Software Engineer',
                'company': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'type': 'Full-time',
                'experience': '5+ years',
                'salary': '$120,000 - $180,000',
                'description': 'We are looking for a senior software engineer to join our team. The ideal candidate will have experience with modern web technologies and be able to work in a fast-paced environment.',
                'requirements': [
                    '5+ years of experience in software development',
                    'Strong knowledge of JavaScript, Python, and React',
                    'Experience with cloud platforms (AWS, Azure, GCP)',
                    'Bachelor\'s degree in Computer Science or related field'
                ],
                'benefits': [
                    'Competitive salary and equity',
                    'Health, dental, and vision insurance',
                    '401(k) with company match',
                    'Flexible work schedule',
                    'Professional development budget'
                ]
            }
            
            # Format job details
            details_text = f"**{job_details['title']}**\n\n"
            details_text += f"🏢 **{job_details['company']}**\n"
            details_text += f"📍 {job_details['location']} | 💰 {job_details['salary']}\n"
            details_text += f"📋 {job_details['type']} | 🎓 {job_details['experience']}\n\n"
            details_text += f"**Description:**\n{job_details['description']}\n\n"
            details_text += f"**Requirements:**\n"
            for req in job_details['requirements']:
                details_text += f"• {req}\n"
            details_text += f"\n**Benefits:**\n"
            for benefit in job_details['benefits']:
                details_text += f"• {benefit}\n"
            
            return self._create_success_response(
                text=details_text,
                intent="job_details",
                metadata={
                    'job_details': job_details,
                    'next_state': ConversationState.IDLE
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling job details request: {e}")
            return self._create_error_response(str(e))
    
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
            text="I'm not sure how to help with job searches. Please try describing what type of job you're looking for."
        )
    
    def get_handled_states(self) -> List[ConversationState]:
        """
        Get list of states this skill can handle.
        
        Returns:
            List[ConversationState]: List of handled states
        """
        return [
            ConversationState.MATCHING,
            ConversationState.CANDIDATE_FLOW,
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
            'user_role': lambda x: x == 'candidate'
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
            text = "I'm not sure how to help with job searches. Please try describing what type of job you're looking for."
        
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