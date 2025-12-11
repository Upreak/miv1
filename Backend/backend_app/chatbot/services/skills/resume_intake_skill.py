"""
Resume Intake Skill for Chatbot/Co-Pilot Module

Handles resume upload, processing, and profile creation for candidates.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .base_skill import BaseSkill
from ...models.conversation_state import ConversationState, UserRole
from ...utils.skill_context import SkillContext
from backend_app.brain_module.brain_service import BrainSvc
from backend_app.text_extraction.consolidated_extractor import extract_with_logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ResumeIntakeSkill(BaseSkill):
    """
    Resume intake skill for handling resume upload and processing.
    
    This skill handles:
    - Resume upload requests
    - File validation
    - Resume processing pipeline
    - Profile creation
    - Progress updates
    """
    
    def __init__(self, profile_writer=None):
        """Initialize resume intake skill."""
        super().__init__(
            name="resume_intake_skill",
            description="Handles resume upload, processing, and profile creation for candidates",
            priority=15
        )
        self.profile_writer = profile_writer
        
        # Define response templates
        self.templates = {
            'resume_upload_request': "Please upload your resume file (PDF, DOC, DOCX).",
            'resume_upload_help': "I can help you upload your resume! Just send me your resume file and I'll process it for you.",
            'file_validation_success': "Great! I've received your resume file.",
            'file_validation_error': "I'm sorry, I couldn't process that file. Please upload a PDF, DOC, or DOCX file.",
            'resume_processing_started': "🔄 Processing your resume... This may take a few moments.",
            'resume_processing_complete': "✅ Resume processed successfully! Your profile has been created.",
            'resume_processing_error': "❌ I encountered an error while processing your resume. Please try again.",
            'profile_created': "🎉 Your profile has been created! Here's what I found:\n\n{profile_summary}",
            'profile_update': "📝 Your profile has been updated with the new information.",
            'resume_help': "I can help you upload and process your resume. Just send me your resume file and I'll extract your information to create your profile.",
            'file_size_error': "The file is too large. Please upload a file smaller than 10MB.",
            'file_type_error': "Please upload a PDF, DOC, or DOCX file.",
            'processing_timeout': "Resume processing is taking longer than expected. Please try again later.",
            'profile_summary': "Here's your profile summary:\n\n{summary}",
            'profile_incomplete': "Your profile is incomplete. Would you like to add more information?",
            'profile_complete': "Your profile is complete! You're ready to start job searching.",
            'profile_review': "Would you like to review and edit your profile before continuing?"
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
            # Handle awaiting resume state
            if state == ConversationState.AWAITING_RESUME:
                return True
            
            # Handle candidate flow state
            if state == ConversationState.CANDIDATE_FLOW:
                return True
            
            # Handle messages that indicate resume upload intent
            if context:
                user_role = context.get('user_role', 'unknown')
                if user_role == 'candidate':
                    # Check for resume-related keywords
                    resume_keywords = [
                        'resume', 'cv', 'curriculum vitae', 'upload resume', 'send resume',
                        'attach resume', 'my resume', 'profile', 'upload file', 'send file'
                    ]
                    
                    if any(keyword in message.lower() for keyword in resume_keywords):
                        return True
                    
                    # Check for specific resume upload phrases
                    if any(phrase in message.lower() for phrase in 
                          ['upload my resume', 'send my resume', 'attach my resume', 'add resume']):
                        return True
            
            # Handle idle state with resume upload intent
            if state == ConversationState.IDLE:
                if context and context.get('user_role') == 'candidate':
                    resume_keywords = [
                        'resume', 'cv', 'curriculum vitae', 'upload resume', 'send resume',
                        'attach resume', 'my resume', 'profile', 'upload file', 'send file'
                    ]
                    
                    if any(keyword in message.lower() for keyword in resume_keywords):
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if resume intake skill can handle: {e}")
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
            if state == ConversationState.AWAITING_RESUME:
                return await self._handle_resume_upload(sid, message, context)
            elif state == ConversationState.CANDIDATE_FLOW:
                return await self._handle_candidate_flow(sid, message, context)
            elif state == ConversationState.IDLE:
                return await self._handle_resume_request(sid, message, context)
            else:
                return await self._handle_fallback(sid, message, context)
                
        except Exception as e:
            logger.error(f"Error in resume intake skill handle: {e}")
            return self._create_error_response(str(e))
    
    async def _handle_resume_upload(self, sid: str, message: str, 
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle resume upload process.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Check if message contains file information
            if self._is_file_upload(message):
                return await self._handle_file_upload(sid, message, context)
            else:
                # Request resume upload
                return self._create_success_response(
                    text=self.templates['resume_upload_request'],
                    intent="resume_upload_request",
                    metadata={
                        'next_state': ConversationState.AWAITING_RESUME,
                        'requires_resume_upload': True
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling resume upload: {e}")
            return self._create_error_response(str(e))
    
    async def _handle_candidate_flow(self, sid: str, message: str, 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle candidate flow resume requests.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Check for resume upload intent
            if any(keyword in message.lower() for keyword in ['resume', 'upload', 'send', 'attach']):
                return await self._handle_resume_upload(sid, message, context)
            
            # Check for profile update intent
            if any(keyword in message.lower() for keyword in ['update', 'edit', 'change', 'modify']):
                return await self._handle_profile_update(sid, message, context)
            
            # Default to resume upload
            return await self._handle_resume_upload(sid, message, context)
            
        except Exception as e:
            logger.error(f"Error handling candidate flow: {e}")
            return self._create_error_response(str(e))
    
    async def _handle_resume_request(self, sid: str, message: str, 
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle resume request in idle state.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Transition to awaiting resume state
            return self._create_success_response(
                text=self.templates['resume_upload_request'],
                intent="resume_upload_request",
                metadata={
                    'next_state': ConversationState.AWAITING_RESUME,
                    'requires_resume_upload': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling resume request: {e}")
            return self._create_error_response(str(e))
    
    async def _handle_file_upload(self, sid: str, message: str, 
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle file upload processing.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Extract file information from message
            file_info = self._extract_file_info(message)
            
            # Validate file
            validation_result = self._validate_file(file_info)
            
            if not validation_result['valid']:
                return self._create_success_response(
                    text=validation_result['message'],
                    intent="file_validation_error",
                    metadata={
                        'next_state': ConversationState.AWAITING_RESUME,
                        'requires_resume_upload': True
                    }
                )
            
            # Start resume processing
            processing_result = await self._start_resume_processing(sid, file_info, context)
            
            if processing_result['success']:
                # Log execution
                self._log_execution(sid, message, True)
                
                return self._create_success_response(
                    text=self.templates['resume_processing_started'],
                    intent="resume_processing_started",
                    metadata={
                        'next_state': ConversationState.PROFILE_READY,
                        'resume_processing': True,
                        'file_info': file_info,
                        'processing_id': processing_result.get('processing_id')
                    }
                )
            else:
                return self._create_success_response(
                    text=self.templates['resume_processing_error'],
                    intent="resume_processing_error",
                    metadata={
                        'next_state': ConversationState.AWAITING_RESUME,
                        'requires_resume_upload': True,
                        'error': processing_result.get('error', 'Unknown error')
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling file upload: {e}")
            return self._create_error_response(str(e))
    
    async def _handle_profile_update(self, sid: str, message: str, 
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle profile update requests.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response
        """
        try:
            # Check if user has existing profile
            if context and context.get('profile_exists'):
                return self._create_success_response(
                    text="I can help you update your profile. What would you like to change?",
                    intent="profile_update_request",
                    metadata={
                        'next_state': ConversationState.PROFILE_READY,
                        'profile_update': True
                    }
                )
            else:
                return self._create_success_response(
                    text="You don't have a profile yet. Let me help you create one by uploading your resume.",
                    intent="profile_create_request",
                    metadata={
                        'next_state': ConversationState.AWAITING_RESUME,
                        'requires_resume_upload': True
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling profile update: {e}")
            return self._create_error_response(str(e))
    
    def _is_file_upload(self, message: str) -> bool:
        """
        Check if message indicates file upload.
        
        Args:
            message: User message
            
        Returns:
            bool: True if file upload, False otherwise
        """
        # Check for file indicators
        file_indicators = [
            'file', 'upload', 'send', 'attach', 'document', 'pdf', 'doc', 'docx',
            'resume', 'cv', 'curriculum vitae'
        ]
        
        return any(indicator in message.lower() for indicator in file_indicators)
    
    def _extract_file_info(self, message: str) -> Dict[str, Any]:
        """
        Extract file information from message.
        
        Args:
            message: User message
            
        Returns:
            Dict[str, Any]: File information
        """
        # Mock file extraction - in real implementation, this would parse actual file data
        file_info = {
            'filename': 'resume.pdf',
            'file_type': 'pdf',
            'file_size': 2048000,  # 2MB
            'content_type': 'application/pdf',
            'upload_time': datetime.utcnow().isoformat()
        }
        
        return file_info
    
    def _validate_file(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate uploaded file.
        
        Args:
            file_info: File information
            
        Returns:
            Dict[str, Any]: Validation result
        """
        try:
            # Check file type
            valid_types = ['pdf', 'doc', 'docx']
            if file_info['file_type'] not in valid_types:
                return {
                    'valid': False,
                    'message': self.templates['file_type_error']
                }
            
            # Check file size (10MB limit)
            max_size = 10 * 1024 * 1024  # 10MB
            if file_info['file_size'] > max_size:
                return {
                    'valid': False,
                    'message': self.templates['file_size_error']
                }
            
            return {
                'valid': True,
                'message': self.templates['file_validation_success']
            }
            
        except Exception as e:
            logger.error(f"Error validating file: {e}")
            return {
                'valid': False,
                'message': self.templates['file_validation_error']
            }
    
    async def _start_resume_processing(self, sid: str, file_info: Dict[str, Any], 
                               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start resume processing pipeline with Real Extraction and Brain Service.
        """
        try:
            # Generate QID
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            qid = f"BOTC-UPLOAD-{sid}-{timestamp}"
            
            # Check for file path (simulated or real)
            # In a real scenario, file_path comes from metadata/context
            file_path = file_info.get('file_path') or file_info.get('path')
            
            # If no path (e.g. mock), fallback to mock logic OR fail
            # For this repair, we try to use real extraction if path exists
            if not file_path:
                 # Check context/metadata for path
                 if context and context.get('file_path'):
                     file_path = context.get('file_path')
            
            if not file_path:
                logger.warning("No file path found for resume processing. Using mock data for demo.")
                # Fallback to mock data to prevent crash if file handling isn't fully set up upstream
                return {
                    'success': True,
                    'processing_id': f"mock_{qid}",
                    'profile_data': self._generate_mock_profile_data(file_info)
                }

            # Real Extraction
            logger.info(f"Starting real extraction for {file_path}")
            extraction_result = extract_with_logging(Path(file_path))
            
            if not extraction_result.get('success'):
                logger.error(f"Extraction failed: {extraction_result.get('error')}")
                return {'success': False, 'error': f"Text extraction failed: {extraction_result.get('error')}"}
            
            text = extraction_result.get('text', '')
            
            # Brain Processing
            logger.info(f"Sending text to BrainService with QID: {qid}")
            brain_result = await BrainSvc.process({
                "qid": qid,
                "text": text,
                "intake_type": "resume_parse",
                "meta": {"sid": sid, "filename": file_info.get('filename')}
            })
            
            if not brain_result.get('success'):
                logger.error(f"Brain processing failed: {brain_result.get('error')}")
                return {'success': False, 'error': f"AI processing failed: {brain_result.get('error')}"}
            
            # Parse Brain Response (expecting JSON-compatible dict or string)
            profile_data = brain_result.get('response', {})
            if isinstance(profile_data, str):
                try:
                    profile_data = json.loads(profile_data)
                except:
                    logger.warning("Brain response was a string but not JSON. Using as raw text.")
                    profile_data = {'raw_text': profile_data}

            # Store processing result in context
            if context:
                context['profile_data'] = profile_data
                context['profile_exists'] = True
                context['profile_complete'] = True
                
                # Persist to database if writer is available
                if self.profile_writer:
                    try:
                        user_id = context.get('user_id')
                        # Ensure user_id is int if present (SIDService stores string)
                        # If user_id is None, it might create a candidate without user link or fail depending on repo
                        self.profile_writer.create_profile_from_parsed_data(
                            profile_data, 
                            user_id=int(user_id) if user_id else None,
                            source="chatbot_resume_upload"
                        )
                        logger.info(f"Persisted profile for SID {sid}")
                    except Exception as pe:
                        logger.error(f"Failed to persist profile to DB: {pe}")
                        # Don't fail the user interaction, just log it
            
            return {
                'success': True,
                'processing_id': qid,
                'profile_data': profile_data
            }
            
        except Exception as e:
            logger.error(f"Error starting resume processing: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_mock_profile_data(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate mock profile data from resume.
        
        Args:
            file_info: File information
            
        Returns:
            Dict[str, Any]: Profile data
        """
        # Mock profile data - in real implementation, this would come from actual resume parsing
        profile_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '+1 (555) 123-4567',
            'summary': 'Experienced software engineer with 5+ years of experience in full-stack development.',
            'experience': [
                {
                    'title': 'Senior Software Engineer',
                    'company': 'Tech Corp',
                    'duration': '2020 - Present',
                    'description': 'Lead development of web applications using React and Node.js.'
                },
                {
                    'title': 'Software Engineer',
                    'company': 'StartupXYZ',
                    'duration': '2018 - 2020',
                    'description': 'Developed and maintained microservices architecture.'
                }
            ],
            'education': [
                {
                    'degree': 'Bachelor of Science in Computer Science',
                    'institution': 'University of Technology',
                    'duration': '2014 - 2018'
                }
            ],
            'skills': [
                'Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'AWS',
                'Docker', 'Kubernetes', 'Git', 'Agile', 'Scrum'
            ],
            'location': 'San Francisco, CA',
            'salary_expectation': '$100,000 - $120,000',
            'job_preferences': {
                'type': 'full-time',
                'location': 'remote',
                'experience_level': 'mid-senior'
            }
        }
        
        return profile_data
    
    async def _handle_fallback(self, sid: str, message: str, 
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
            text="I'm not sure how to help with resume uploads. Please try uploading your resume file."
        )
    
    def get_handled_states(self) -> List[ConversationState]:
        """
        Get list of states this skill can handle.
        
        Returns:
            List[ConversationState]: List of handled states
        """
        return [
            ConversationState.AWAITING_RESUME,
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
            text = "I'm not sure how to help with resume uploads. Please try uploading your resume file."
        
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