"""
Onboarding Skill for Chatbot/Co-Pilot Module

Handles user onboarding, role identification, and initial setup.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .base_skill import BaseSkill
from ...models.conversation_state import ConversationState, UserRole
from ...utils.skill_context import SkillContext

logger = logging.getLogger(__name__)


class OnboardingSkill(BaseSkill):
    """
    Onboarding skill for handling user onboarding and role identification.
    
    This skill handles:
    - Welcome messages
    - Role identification (candidate/recruiter)
    - Initial setup
    - First-time user guidance
    - Session initialization
    """
    
    def __init__(self):
        """Initialize onboarding skill."""
        super().__init__(
            name="onboarding_skill",
            description="Handles user onboarding, role identification, and initial setup",
            priority=20  # Highest priority for onboarding
        )
        
        # Define response templates
        self.templates = {
            'welcome': "👋 Welcome to the AI Recruitment Assistant! I'm here to help you find your dream job or the perfect candidate.",
            'role_request': "Are you a **Candidate** looking for a job or a **Recruiter** looking to hire?",
            'role_candidate': "Great! I'll help you find the perfect job match. To speed things up, do you have a resume you can upload? (Yes/No)",
            'resume_request': "Please upload your resume (PDF or Word document).",
            'manual_setup': "No problem! Let's set up your profile manually. First, I'll need some basic information.",
            'role_recruiter': "Excellent! I'll help you find the best candidates for your open positions.",
            'role_invalid': "I'm sorry, I didn't understand that. Please choose either 'Candidate' or 'Recruiter'.",
            'profile_setup': "Let's set up your profile. First, I'll need some basic information.",
            'name_request': "What's your name?",
            'email_request': "What's your email address?",
            'phone_request': "What's your phone number? (Optional)",
            'profile_complete': "Perfect! Your profile is now complete. How can I help you today?",
            'onboarding_complete': "🎉 Welcome aboard! You're all set to start using the AI Recruitment Assistant.",
            'help_request': "I can help you with:\n\n• **For Candidates:** Find jobs, upload resume, get recommendations\n• **For Recruiters:** Post jobs, find candidates, manage applications\n\nWhat would you like to do?",
            'get_started': "Let's get started! What would you like to do first?",
            'error': "I'm sorry, I encountered an error. Let me help you get started again."
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
            # Handle onboarding state
            if state == ConversationState.ONBOARDING:
                return True
            
            # Handle awaiting role state
            if state == ConversationState.AWAITING_ROLE:
                return True
            
            # Handle initial state (no session or new user)
            if state is None or state == ConversationState.IDLE:
                # Check if this is a new session or first message
                if context and context.get('is_first_message', False):
                    return True
                
                # Check for onboarding keywords
                onboarding_keywords = [
                    'hello', 'hi', 'hey', 'start', 'begin', 'help', 'get started',
                    'new', 'first time', 'welcome', 'onboard', 'setup'
                ]
                
                if any(keyword in message.lower() for keyword in onboarding_keywords):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if onboarding skill can handle: {e}")
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
            if state == ConversationState.ONBOARDING:
                return self._handle_onboarding(sid, message, context)
            elif state == ConversationState.AWAITING_ROLE:
                return self._handle_role_selection(sid, message, context)
            elif state is None or state == ConversationState.IDLE:
                return self._handle_initial_onboarding(sid, message, context)
            else:
                return self._handle_fallback(sid, message, context)
                
        except Exception as e:
            logger.error(f"Error in onboarding skill handle: {e}")
            return self._create_error_response(str(e))
    
    def _handle_onboarding(self, sid: str, message: str, 
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle onboarding process.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Check if role is already determined
            if context and context.get('user_role'):
                return self._handle_profile_setup(sid, message, context)
            
            # Otherwise, request role
            return self._handle_role_selection(sid, message, context)
            
        except Exception as e:
            logger.error(f"Error handling onboarding: {e}")
            return self._create_error_response(str(e))
    
    def _handle_role_selection(self, sid: str, message: str, 
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle role selection.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Normalize message for role detection
            message_lower = message.lower()
            
            # Detect role from message
            if any(candidate_keyword in message_lower for candidate_keyword in 
                   ['candidate', 'job seeker', 'looking for job', 'find job', 'employee']):
                # User is a candidate
                user_role = UserRole.CANDIDATE
                
                # Update context
                if context:
                    context['user_role'] = 'candidate'
                    context['session_state'] = ConversationState.CANDIDATE_FLOW.value
                
                # Log execution
                self._log_execution(sid, message, True)
                
                return self._create_success_response(
                    text=self.templates['role_candidate'],
                    intent="role_selected",
                    metadata={
                        'user_role': 'candidate',
                        'next_state': ConversationState.ONBOARDING,
                        'requires_profile_setup': True,
                        'setup_step': 'resume_check'
                    }
                )
                
            elif any(recruiter_keyword in message_lower for recruiter_keyword in 
                    ['recruiter', 'hiring manager', 'employer', 'company', 'hiring']):
                # User is a recruiter
                user_role = UserRole.RECRUITER
                
                # Update context
                if context:
                    context['user_role'] = 'recruiter'
                    context['session_state'] = ConversationState.RECRUITER_FLOW.value
                
                # Log execution
                self._log_execution(sid, message, True)
                
                return self._create_success_response(
                    text=self.templates['role_recruiter'],
                    intent="role_selected",
                    metadata={
                        'user_role': 'recruiter',
                        'next_state': ConversationState.RECRUITER_FLOW,
                        'requires_profile_setup': True
                    }
                )
                
            else:
                # Invalid role selection
                return self._create_success_response(
                    text=self.templates['role_invalid'],
                    intent="role_invalid",
                    metadata={
                        'next_state': ConversationState.AWAITING_ROLE,
                        'requires_role_selection': True
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling role selection: {e}")
            return self._create_error_response(str(e))
    
    def _handle_initial_onboarding(self, sid: str, message: str, 
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle initial onboarding for new users.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Log execution
            self._log_execution(sid, message, True)
            
            # Send welcome message and request role
            return self._create_success_response(
                text=self.templates['welcome'] + "\n\n" + self.templates['role_request'],
                intent="welcome",
                metadata={
                    'next_state': ConversationState.AWAITING_ROLE,
                    'requires_role_selection': True,
                    'is_first_message': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling initial onboarding: {e}")
            return self._create_error_response(str(e))
    
    def _handle_profile_setup(self, sid: str, message: str, 
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle profile setup.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Check if profile setup is already complete
            if context and context.get('profile_complete'):
                return self._handle_onboarding_complete(sid, message, context)
            
            # Get current setup step
            setup_step = context.get('setup_step', 'name') if context else 'name'
            
            # Handle based on setup step
            if setup_step == 'resume_check':
                return self._handle_resume_check(sid, message, context)
            elif setup_step == 'name':
                return self._handle_name_collection(sid, message, context)
            elif setup_step == 'email':
                return self._handle_email_collection(sid, message, context)
            elif setup_step == 'phone':
                return self._handle_phone_collection(sid, message, context)
            else:
                return self._handle_onboarding_complete(sid, message, context)
                
        except Exception as e:
            logger.error(f"Error handling profile setup: {e}")
            return self._create_error_response(str(e))
    
    def _handle_resume_check(self, sid: str, message: str, 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle resume check response.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Check for yes/no
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['yes', 'y', 'sure', 'ok']):
                # User has resume - transition to resume intake
                return self._create_success_response(
                    text=self.templates['resume_request'],
                    intent="resume_confirmed",
                    metadata={
                        'next_state': ConversationState.AWAITING_RESUME,
                        'requires_resume_upload': True
                    }
                )
            else:
                # User has no resume - proceed to manual setup
                if context:
                    context['setup_step'] = 'name'
                
                return self._create_success_response(
                    text=self.templates['manual_setup'],
                    intent="resume_declined",
                    metadata={
                        'next_state': ConversationState.ONBOARDING,
                        'setup_step': 'name'
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling resume check: {e}")
            return self._create_error_response(str(e))

    def _handle_name_collection(self, sid: str, message: str, 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle name collection.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Validate name
            if len(message.strip()) < 2:
                return self._create_success_response(
                    text="Please enter a valid name.",
                    intent="name_validation_error",
                    metadata={
                        'next_state': ConversationState.ONBOARDING,
                        'setup_step': 'name'
                    }
                )
            
            # Store name in context
            if context:
                context['user_name'] = message.strip()
                context['setup_step'] = 'email'
            
            # Log execution
            self._log_execution(sid, message, True)
            
            # Request email
            return self._create_success_response(
                text=self.templates['email_request'],
                intent="name_collected",
                metadata={
                    'user_name': message.strip(),
                    'next_state': ConversationState.ONBOARDING,
                    'setup_step': 'email'
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling name collection: {e}")
            return self._create_error_response(str(e))
    
    def _handle_email_collection(self, sid: str, message: str, 
                               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle email collection.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Validate email (basic validation)
            if '@' not in message or '.' not in message:
                return self._create_success_response(
                    text="Please enter a valid email address.",
                    intent="email_validation_error",
                    metadata={
                        'next_state': ConversationState.ONBOARDING,
                        'setup_step': 'email'
                    }
                )
            
            # Store email in context
            if context:
                context['user_email'] = message.strip()
                context['setup_step'] = 'phone'
            
            # Log execution
            self._log_execution(sid, message, True)
            
            # Request phone (optional)
            return self._create_success_response(
                text=self.templates['phone_request'],
                intent="email_collected",
                metadata={
                    'user_email': message.strip(),
                    'next_state': ConversationState.ONBOARDING,
                    'setup_step': 'phone'
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling email collection: {e}")
            return self._create_error_response(str(e))
    
    def _handle_phone_collection(self, sid: str, message: str, 
                               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle phone collection.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Store phone in context (optional, so accept empty)
            if context:
                context['user_phone'] = message.strip() if message.strip() else None
                context['setup_step'] = 'complete'
                context['profile_complete'] = True
            
            # Log execution
            self._log_execution(sid, message, True)
            
            # Mark profile as complete
            return self._create_success_response(
                text=self.templates['profile_complete'],
                intent="profile_complete",
                metadata={
                    'user_phone': message.strip() if message.strip() else None,
                    'next_state': ConversationState.IDLE,
                    'setup_step': 'complete',
                    'profile_complete': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling phone collection: {e}")
            return self._create_error_response(str(e))
    
    def _handle_onboarding_complete(self, sid: str, message: str, 
                                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle onboarding completion.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Log execution
            self._log_execution(sid, message, True)
            
            # Send completion message and offer help
            return self._create_success_response(
                text=self.templates['onboarding_complete'] + "\n\n" + self.templates['help_request'],
                intent="onboarding_complete",
                metadata={
                    'next_state': ConversationState.IDLE,
                    'onboarding_complete': True,
                    'requires_action': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling onboarding completion: {e}")
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
            text="I'm not sure how to help with onboarding. Let me get you started again."
        )
    
    def get_handled_states(self) -> List[ConversationState]:
        """
        Get list of states this skill can handle.
        
        Returns:
            List[ConversationState]: List of handled states
        """
        return [
            ConversationState.ONBOARDING,
            ConversationState.AWAITING_ROLE,
            ConversationState.IDLE
        ]
    
    def get_required_fields(self) -> List[str]:
        """
        Get list of required context fields.
        
        Returns:
            List[str]: List of required field names
        """
        return ['sid', 'message']
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """
        Get validation rules for context fields.
        
        Returns:
            Dict[str, Any]: Validation rules
        """
        return {}
    
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
            text = "I'm not sure how to help with onboarding. Let me get you started again."
        
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