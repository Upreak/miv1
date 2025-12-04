"""
Co-Pilot Service for Chatbot/Co-Pilot Module

Central AI brain for the chatbot system that orchestrates conversations,
generates contextual responses, and coordinates between different skills.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union

from .llm_service import LLMService
from .sid_service import SIDService
from .skill_registry import SkillRegistry
from .message_router import MessageRouter
from ..models.conversation_state import ConversationContext, ConversationStateManager
from ..utils.skill_context import SkillContext

logger = logging.getLogger(__name__)


class CoPilotService:
    """
    Co-Pilot Service - Central AI brain for the chatbot system.
    
    This service is responsible for:
    - Orchestrating conversations across different platforms
    - Generating contextual AI responses
    - Coordinating between skills and services
    - Managing conversation flow and state
    - Providing intelligent suggestions and guidance
    """
    
    def __init__(self, llm_service: LLMService, sid_service: SIDService,
                 skill_registry: SkillRegistry, message_router: MessageRouter):
        """
        Initialize Co-Pilot Service.
        
        Args:
            llm_service: LLM service for AI responses
            sid_service: SID service for session management
            skill_registry: Skill registry for skill management
            message_router: Message router for routing messages
        """
        self.llm_service = llm_service
        self.sid_service = sid_service
        self.skill_registry = skill_registry
        self.message_router = message_router
        
        # Initialize conversation templates
        self.conversation_templates = {
            'welcome': [
                "Welcome to your AI Career Assistant! I'm here to help you with your job search and career goals.",
                "Hello! I'm your AI career assistant. Let's get started on your job search journey.",
                "Welcome aboard! I'll help you find the perfect job and build an amazing career."
            ],
            'role_selection': [
                "Are you a job seeker looking for opportunities or a recruiter looking for candidates?",
                "Let me help you get started. Are you here to find a job or to hire someone?",
                "What brings you here today? Are you looking for a new career opportunity or seeking candidates?"
            ],
            'candidate_flow': [
                "Great! I'll help you find the perfect job match. Let's start by understanding your background.",
                "Perfect! As a job seeker, I'll help you discover opportunities that match your skills and experience.",
                "Excellent! I'll guide you through creating a great profile and finding job opportunities."
            ],
            'recruiter_flow': [
                "Great! I'll help you find the perfect candidates. Let's start by creating your job posting.",
                "Perfect! As a recruiter, I'll help you attract top talent and streamline your hiring process.",
                "Excellent! I'll assist you in creating compelling job descriptions and finding qualified candidates."
            ],
            'help_menu': [
                "Here's what I can help you with:\n\n"
                "🔍 **Job Search**: Find jobs that match your profile\n"
                "📝 **Resume Help**: Create and optimize your resume\n"
                "🎯 **Career Guidance**: Get advice on your career path\n"
                "📊 **Application Tracking**: Monitor your application status\n"
                "💼 **Interview Prep**: Prepare for interviews\n\n"
                "What would you like to explore?",
                
                "I'm here to help with:\n\n"
                "• Finding jobs that match your skills\n"
                "• Building a professional resume\n"
                "• Career planning and advice\n"
                "• Application management\n"
                "• Interview preparation\n\n"
                "What interests you most?",
                
                "Your AI career assistant can help:\n\n"
                "✅ Job discovery and matching\n"
                "✅ Resume writing and optimization\n"
                "✅ Career guidance and planning\n"
                "✅ Application tracking\n"
                "✅ Interview preparation\n\n"
                "What would you like to work on?"
            ]
        }
    
    def generate_contextual_reply(self, sid: str, message: str, 
                                 profile: Optional[Dict[str, Any]] = None,
                                 job: Optional[Dict[str, Any]] = None,
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate contextual reply based on conversation history and context.
        
        Args:
            sid: Session ID
            message: User message
            profile: Optional user profile data
            job: Optional job data
            context: Additional context
            
        Returns:
            Dict[str, Any]: Generated response
        """
        try:
            # Get session information
            session = self.sid_service.get_by_sid(sid)
            if not session:
                return self._create_error_response("Session not found")
            
            # Prepare conversation context
            conversation_context = self._prepare_conversation_context(
                session, message, profile, job, context
            )
            
            # Generate AI response
            ai_response = self.llm_service.generate_reply(
                context=conversation_context,
                message=message
            )
            
            # Create response structure
            response = {
                'text': ai_response,
                'intent': 'contextual_reply',
                'confidence': 0.9,
                'timestamp': datetime.utcnow().isoformat(),
                'skill_used': 'copilot_service',
                'metadata': {
                    'session_state': session.state.value if session.state else None,
                    'user_role': session.role.value if session.role else None,
                    'profile_available': profile is not None,
                    'job_available': job is not None,
                    'context_size': len(conversation_context) if conversation_context else 0
                }
            }
            
            # Update session with response
            self._update_session_with_ai_response(session, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating contextual reply: {e}")
            return self._create_error_response(str(e))
    
    def handle_message(self, channel: str, channel_user_id: str, 
                      message: str, message_type: str = "text",
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle incoming message from any platform.
        
        Args:
            channel: Platform channel
            channel_user_id: Platform-specific user ID
            message: User message
            message_type: Type of message
            metadata: Additional metadata
            
        Returns:
            Dict[str, Any]: Response from the system
        """
        try:
            # Route message through the message router
            response = self.message_router.route(
                channel=channel,
                channel_user_id=channel_user_id,
                message=message,
                message_type=message_type,
                metadata=metadata
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return self._create_error_response(str(e))
    
    def get_conversation_summary(self, sid: str) -> Dict[str, Any]:
        """
        Generate conversation summary for a session.
        
        Args:
            sid: Session ID
            
        Returns:
            Dict[str, Any]: Conversation summary
        """
        try:
            session = self.sid_service.get_by_sid(sid)
            if not session:
                return self._create_error_response("Session not found")
            
            # Get conversation history (this would typically come from message repository)
            history = self._get_conversation_history(sid)
            
            # Generate summary
            summary = self.llm_service.summarize_conversation(history)
            
            return {
                'summary': summary,
                'session_info': {
                    'sid': sid,
                    'user_role': session.role.value if session.role else None,
                    'conversation_state': session.state.value if session.state else None,
                    'message_count': session.message_count,
                    'created_at': session.created_at.isoformat(),
                    'updated_at': session.updated_at.isoformat()
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return self._create_error_response(str(e))
    
    def get_intelligent_suggestions(self, sid: str, context: Dict[str, Any] = None) -> List[str]:
        """
        Get intelligent suggestions based on conversation context.
        
        Args:
            sid: Session ID
            context: Additional context
            
        Returns:
            List[str]: List of suggestions
        """
        try:
            session = self.sid_service.get_by_sid(sid)
            if not session:
                return []
            
            suggestions = []
            
            # Get suggestions based on user role and conversation state
            if session.role.value == 'candidate':
                suggestions.extend(self._get_candidate_suggestions(session, context))
            elif session.role.value == 'recruiter':
                suggestions.extend(self._get_recruiter_suggestions(session, context))
            
            # Add general suggestions
            suggestions.extend(self._get_general_suggestions(session, context))
            
            return suggestions[:5]  # Return max 5 suggestions
            
        except Exception as e:
            logger.error(f"Error generating intelligent suggestions: {e}")
            return []
    
    def create_conversation_context(self, sid: str) -> ConversationContext:
        """
        Create conversation context for a session.
        
        Args:
            sid: Session ID
            
        Returns:
            ConversationContext: Conversation context
        """
        try:
            session = self.sid_service.get_by_sid(sid)
            if not session:
                raise ValueError(f"Session {sid} not found")
            
            # Create conversation context
            context = ConversationContext(
                sid=sid,
                user_id=session.user_id,
                role=session.role,
                current_state=session.state,
                metadata=session.context or {}
            )
            
            # Add conversation history
            history = self._get_conversation_history(sid)
            for entry in history:
                context.add_message(entry['content'], entry['sender'])
            
            return context
            
        except Exception as e:
            logger.error(f"Error creating conversation context: {e}")
            raise
    
    def update_conversation_state(self, sid: str, new_state: str, 
                                 context_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update conversation state for a session.
        
        Args:
            sid: Session ID
            new_state: New conversation state
            context_data: Additional context data
            
        Returns:
            bool: True if updated successfully
        """
        try:
            from ..models.conversation_state import ConversationState
            
            # Convert string to enum
            state_enum = ConversationState(new_state)
            
            # Update session state
            success = self.sid_service.update_session_state(sid, state_enum)
            
            if success and context_data:
                # Update context data
                for key, value in context_data.items():
                    self.sid_service.update_context(sid, key, value)
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating conversation state: {e}")
            return False
    
    def get_conversation_insights(self, sid: str) -> Dict[str, Any]:
        """
        Get conversation insights for a session.
        
        Args:
            sid: Session ID
            
        Returns:
            Dict[str, Any]: Conversation insights
        """
        try:
            session = self.sid_service.get_by_sid(sid)
            if not session:
                return self._create_error_response("Session not found")
            
            # Get conversation history
            history = self._get_conversation_history(sid)
            
            # Analyze conversation patterns
            insights = self._analyze_conversation_patterns(history, session)
            
            # Get skill usage statistics
            skill_stats = self.skill_registry.get_execution_stats('copilot_service')
            
            return {
                'session_info': {
                    'sid': sid,
                    'user_role': session.role.value if session.role else None,
                    'conversation_state': session.state.value if session.state else None,
                    'message_count': session.message_count,
                    'created_at': session.created_at.isoformat(),
                    'updated_at': session.updated_at.isoformat()
                },
                'conversation_insights': insights,
                'skill_usage': skill_stats,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating conversation insights: {e}")
            return self._create_error_response(str(e))
    
    def _prepare_conversation_context(self, session, message: str,
                                    profile: Optional[Dict[str, Any]] = None,
                                    job: Optional[Dict[str, Any]] = None,
                                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Prepare conversation context for AI response generation.
        
        Args:
            session: Session object
            message: User message
            profile: Optional user profile
            job: Optional job data
            context: Additional context
            
        Returns:
            Dict[str, Any]: Prepared context
        """
        # Get conversation history
        history = self._get_conversation_history(session.sid)
        
        # Build context
        conversation_context = {
            'user_role': session.role.value if session.role else 'unknown',
            'conversation_state': session.state.value if session.state else 'unknown',
            'channel': session.channel,
            'message': message,
            'history': history,
            'profile': profile or {},
            'job': job or {},
            'session_context': session.context or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add additional context if provided
        if context:
            conversation_context.update(context)
        
        return conversation_context
    
    def _update_session_with_ai_response(self, session, response: Dict[str, Any]) -> None:
        """
        Update session with AI response.
        
        Args:
            session: Session object
            response: AI response
        """
        try:
            # Update last message
            if response.get('text'):
                self.sid_service.update_last_message(session.sid, response['text'])
            
            # Update message count
            self.sid_service.increment_message_count(session.sid)
            
            # Update context with AI response metadata
            if 'metadata' in response:
                for key, value in response['metadata'].items():
                    self.sid_service.update_context(session.sid, key, value)
            
        except Exception as e:
            logger.error(f"Error updating session with AI response: {e}")
    
    def _get_conversation_history(self, sid: str) -> List[Dict[str, str]]:
        """
        Get conversation history for a session.
        
        Args:
            sid: Session ID
            
        Returns:
            List[Dict[str, str]]: Conversation history
        """
        try:
            # This would typically query the message repository
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def _analyze_conversation_patterns(self, history: List[Dict[str, str]], 
                                     session) -> Dict[str, Any]:
        """
        Analyze conversation patterns.
        
        Args:
            history: Conversation history
            session: Session object
            
        Returns:
            Dict[str, Any]: Pattern analysis
        """
        try:
            # Basic pattern analysis
            total_messages = len(history)
            user_messages = len([h for h in history if h.get('sender') == 'user'])
            bot_messages = len([h for h in history if h.get('sender') == 'bot'])
            
            # Analyze message types
            message_types = {}
            for entry in history:
                msg_type = entry.get('type', 'text')
                message_types[msg_type] = message_types.get(msg_type, 0) + 1
            
            # Calculate conversation duration
            if history:
                first_message = history[0]
                last_message = history[-1]
                # This would need proper timestamp parsing
                conversation_duration = "unknown"
            else:
                conversation_duration = "no_messages"
            
            return {
                'total_messages': total_messages,
                'user_messages': user_messages,
                'bot_messages': bot_messages,
                'message_types': message_types,
                'conversation_duration': conversation_duration,
                'average_message_length': self._calculate_average_message_length(history),
                'conversation_topics': self._extract_conversation_topics(history)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing conversation patterns: {e}")
            return {}
    
    def _calculate_average_message_length(self, history: List[Dict[str, str]]) -> float:
        """
        Calculate average message length.
        
        Args:
            history: Conversation history
            
        Returns:
            float: Average message length
        """
        try:
            if not history:
                return 0.0
            
            total_length = sum(len(entry.get('content', '')) for entry in history)
            return total_length / len(history)
            
        except Exception as e:
            logger.error(f"Error calculating average message length: {e}")
            return 0.0
    
    def _extract_conversation_topics(self, history: List[Dict[str, str]]) -> List[str]:
        """
        Extract conversation topics.
        
        Args:
            history: Conversation history
            
        Returns:
            List[str]: List of topics
        """
        try:
            # Simple topic extraction based on keywords
            topics = []
            keywords = {
                'job': ['job', 'work', 'position', 'career', 'employment'],
                'resume': ['resume', 'cv', 'curriculum', 'profile'],
                'interview': ['interview', 'meeting', 'conversation'],
                'application': ['application', 'apply', 'submit'],
                'company': ['company', 'organization', 'firm'],
                'salary': ['salary', 'compensation', 'pay', 'benefits']
            }
            
            for entry in history:
                content = entry.get('content', '').lower()
                for topic, topic_keywords in keywords.items():
                    if any(keyword in content for keyword in topic_keywords):
                        if topic not in topics:
                            topics.append(topic)
                        break
            
            return topics
            
        except Exception as e:
            logger.error(f"Error extracting conversation topics: {e}")
            return []
    
    def _get_candidate_suggestions(self, session, context: Dict[str, Any] = None) -> List[str]:
        """
        Get suggestions for candidates.
        
        Args:
            session: Session object
            context: Additional context
            
        Returns:
            List[str]: List of suggestions
        """
        suggestions = []
        
        # Check if profile is complete
        if not session.get_context('profile_complete', False):
            suggestions.append("Complete your profile to get better job matches")
        
        # Check if user has applied to jobs
        if not session.get_context('applications_count', 0):
            suggestions.append("Browse and apply to jobs that match your skills")
        
        # Check if user has uploaded resume
        if not session.get_context('resume_uploaded', False):
            suggestions.append("Upload your resume to showcase your experience")
        
        return suggestions
    
    def _get_recruiter_suggestions(self, session, context: Dict[str, Any] = None) -> List[str]:
        """
        Get suggestions for recruiters.
        
        Args:
            session: Session object
            context: Additional context
            
        Returns:
            List[str]: List of suggestions
        """
        suggestions = []
        
        # Check if recruiter has posted jobs
        if not session.get_context('jobs_posted', 0):
            suggestions.append("Create a job posting to attract candidates")
        
        # Check if recruiter has reviewed applications
        if not session.get_context('applications_reviewed', 0):
            suggestions.append("Review applications from qualified candidates")
        
        # Check if recruiter has shortlisted candidates
        if not session.get_context('candidates_shortlisted', 0):
            suggestions.append("Shortlist promising candidates for your positions")
        
        return suggestions
    
    def _get_general_suggestions(self, session, context: Dict[str, Any] = None) -> List[str]:
        """
        Get general suggestions.
        
        Args:
            session: Session object
            context: Additional context
            
        Returns:
            List[str]: List of suggestions
        """
        suggestions = []
        
        # Check if user needs help
        if session.get_context('needs_help', False):
            suggestions.append("Type 'help' to see what I can assist you with")
        
        # Check if user wants to explore features
        if session.get_context('wants_to_explore', False):
            suggestions.append("Explore our features to make the most of your experience")
        
        return suggestions
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Create error response.
        
        Args:
            error_message: Error message
            
        Returns:
            Dict[str, Any]: Error response
        """
        return {
            'text': "I'm sorry, I encountered an error. Please try again.",
            'intent': 'error',
            'confidence': 0.0,
            'error': error_message,
            'timestamp': datetime.utcnow().isoformat(),
            'skill_used': 'copilot_service'
        }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """
        Get service statistics.
        
        Returns:
            Dict[str, Any]: Service statistics
        """
        try:
            # Get routing stats
            routing_stats = self.message_router.get_routing_stats()
            
            # Get skill registry stats
            skill_stats = self.skill_registry.get_all_execution_stats()
            
            # Get cache stats
            cache_stats = self.llm_service.get_cache_stats()
            
            return {
                'service_name': 'copilot_service',
                'routing_stats': routing_stats,
                'skill_stats': skill_stats,
                'cache_stats': cache_stats,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting service stats: {e}")
            return {}
    
    def reset_conversation(self, sid: str) -> bool:
        """
        Reset conversation for a session.
        
        Args:
            sid: Session ID
            
        Returns:
            bool: True if reset successfully
        """
        try:
            session = self.sid_service.get_by_sid(sid)
            if not session:
                return False
            
            # Reset session state
            from ..models.conversation_state import ConversationState
            self.sid_service.update_session_state(sid, ConversationState.ONBOARDING)
            
            # Clear context
            self.sid_service.update_context(sid, 'reset_conversation', True)
            
            logger.info(f"Reset conversation for session {sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting conversation: {e}")
            return False