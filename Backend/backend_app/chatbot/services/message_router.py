"""
Message Router for Chatbot/Co-Pilot Module

Routes incoming messages to appropriate skills based on conversation state
and message content. This is the core routing engine for the chatbot system.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .skill_registry import SkillRegistry
from .sid_service import SIDService
from ..models.conversation_state import ConversationState, UserRole
from ..utils.skill_context import SkillContext

logger = logging.getLogger(__name__)


class MessageRouter:
    """
    Message Router for routing messages to appropriate skills.
    
    This router is responsible for:
    - Receiving incoming messages from different platforms
    - Identifying the appropriate skill to handle the message
    - Managing conversation state and context
    - Coordinating skill execution
    - Handling errors and fallback responses
    """
    
    def __init__(self, skill_registry: SkillRegistry, sid_service: SIDService):
        """
        Initialize Message Router.
        
        Args:
            skill_registry: Skill registry instance
            sid_service: SID service instance
        """
        self.skill_registry = skill_registry
        self.sid_service = sid_service
        self.route_history = []
        self.error_count = 0
        self.total_messages = 0
    
    async def route(self, channel: str, channel_user_id: str, message: str, 
             message_type: str = "text", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route a message to the appropriate skill.
        
        Args:
            channel: Platform channel (whatsapp/telegram/web)
            channel_user_id: Platform-specific user ID
            message: User message
            message_type: Type of message (text, image, document, etc.)
            metadata: Additional message metadata
            
        Returns:
            Dict[str, Any]: Response from the skill
        """
        try:
            start_time = datetime.utcnow()
            self.total_messages += 1
            
            # Get or create session
            session = self.sid_service.get_or_create(channel, channel_user_id)
            
            # Prepare context
            context = self._prepare_context(session, message, message_type, metadata)
            
            # Log incoming message
            self._log_message(session.sid, message, "inbound", message_type, metadata)
            
            # Select appropriate skill
            skill = self._select_skill(session, message, context)
            
            if not skill:
                # Fallback response
                response = self._create_fallback_response(message, context)
                logger.warning(f"No skill found for message: {message}")
            else:
                # Execute skill
                response = await self._execute_skill(skill, session.sid, message, context)
                
                # Update execution stats
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                success = response.get('intent') != 'error'
                self.skill_registry.update_execution_stats(skill.name, success, execution_time)
            
            # Update session with response
            self._update_session_with_response(session, response)
            
            # Log outgoing message
            self._log_message(session.sid, response.get('text', ''), "outbound", "text", response)
            
            # Log routing decision
            self._log_routing_decision(session.sid, message, skill, response, execution_time if 'skill' in locals() else 0)
            
            return response
            
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            self.error_count += 1
            return self._create_error_response(str(e))
    
    async def route_with_context(self, sid: str, message: str, 
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route a message with existing context.
        
        Args:
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Response from the skill
        """
        try:
            start_time = datetime.utcnow()
            
            # Get session
            session = self.sid_service.get_by_sid(sid)
            if not session:
                return self._create_error_response("Session not found")
            
            # Prepare context
            if context is None:
                context = {}
            
            context.update({
                'sid': sid,
                'session_state': session.state,
                'user_role': session.role.value if session.role else 'unknown',
                'metadata': context.get('metadata', {})
            })
            
            # Select appropriate skill
            skill = self._select_skill(session, message, context)
            
            if not skill:
                response = self._create_fallback_response(message, context)
            else:
                response = await self._execute_skill(skill, sid, message, context)
                
                # Update execution stats
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                success = response.get('intent') != 'error'
                self.skill_registry.update_execution_stats(skill.name, success, execution_time)
            
            # Update session with response
            self._update_session_with_response(session, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error routing message with context: {e}")
            return self._create_error_response(str(e))
    
    def _prepare_context(self, session, message: str, message_type: str, 
                        metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Prepare context for skill execution.
        
        Args:
            session: Session object
            message: User message
            message_type: Type of message
            metadata: Additional metadata
            
        Returns:
            Dict[str, Any]: Prepared context
        """
        context = {
            'sid': session.sid,
            'session_state': session.state,
            'user_role': session.role.value if session.role else 'unknown',
            'message': message,
            'message_type': message_type,
            'channel': session.channel,
            'channel_user_id': session.channel_user_id,
            'user_id': session.user_id,
            'metadata': metadata or {}
        }
        
        # Add context from session
        if session.context:
            context['session_context'] = session.context
        
        # Add timestamp
        context['timestamp'] = datetime.utcnow().isoformat()
        
        return context
    
    def _select_skill(self, session, message: str, context: Dict[str, Any]) -> Optional[Any]:
        """
        Select the most appropriate skill for the message.
        
        Args:
            session: Session object
            message: User message
            context: Additional context
            
        Returns:
            Optional[Any]: Selected skill or None
        """
        try:
            # Try to select skill based on state and message
            skill = self.skill_registry.select_skill(session.state, message, context)
            
            if skill:
                return skill
            
            # If no skill found, try fallback skills
            fallback_skills = self.skill_registry.get_by_priority(0, 5)  # Low priority fallbacks
            for fallback_skill in fallback_skills:
                if fallback_skill.can_handle(session.state, message, context):
                    logger.info(f"Using fallback skill: {fallback_skill.name}")
                    return fallback_skill
            
            return None
            
        except Exception as e:
            logger.error(f"Error selecting skill: {e}")
            return None
    
    async def _execute_skill(self, skill, sid: str, message: str, 
                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a skill and return response.
        
        Args:
            skill: Skill to execute
            sid: Session ID
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Skill response
        """
        try:
            # Validate context
            if not skill.validate_context(context):
                logger.warning(f"Invalid context for skill {skill.name}")
                return self._create_error_response("Invalid context for skill")
            
            # Execute skill
            response = await skill.handle(sid, message, context)
            
            # Ensure response has required fields
            if not isinstance(response, dict):
                response = {'text': str(response)}
            
            # Add default fields if missing
            response.setdefault('intent', 'unknown')
            response.setdefault('confidence', 0.5)
            response.setdefault('timestamp', datetime.utcnow().isoformat())
            response.setdefault('skill_used', skill.name)
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing skill {skill.name}: {e}")
            return self._create_error_response(f"Skill execution error: {str(e)}")
    
    def _update_session_with_response(self, session, response: Dict[str, Any]) -> None:
        """
        Update session with skill response.
        
        Args:
            session: Session object
            response: Skill response
        """
        try:
            # Update last message
            if response.get('text'):
                self.sid_service.update_last_message(session.sid, response['text'])
            
            # Update message count
            self.sid_service.increment_message_count(session.sid)
            
            # Update state if specified in response
            if 'next_state' in response:
                from ..models.conversation_state import ConversationState
                if isinstance(response['next_state'], ConversationState):
                    self.sid_service.update_session_state(session.sid, response['next_state'])
            
            # Update context if specified in response
            if 'metadata' in response:
                for key, value in response['metadata'].items():
                    self.sid_service.update_context(session.sid, key, value)
            
        except Exception as e:
            logger.error(f"Error updating session with response: {e}")
    
    def _create_fallback_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create fallback response when no skill can handle the message.
        
        Args:
            message: User message
            context: Additional context
            
        Returns:
            Dict[str, Any]: Fallback response
        """
        return {
            'text': "I didn't understand that. Please try again or type 'help' for assistance.",
            'intent': 'fallback',
            'confidence': 0.1,
            'timestamp': datetime.utcnow().isoformat(),
            'skill_used': 'fallback',
            'metadata': {
                'fallback_reason': 'no_skill_found',
                'original_message': message,
                'context': context
            }
        }
    
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
            'skill_used': 'error_handler'
        }
    
    def _log_message(self, sid: str, content: str, direction: str, 
                    message_type: str, metadata: Dict[str, Any] = None) -> None:
        """
        Log message to message repository.
        
        Args:
            sid: Session ID
            content: Message content
            direction: Message direction (inbound/outbound)
            message_type: Type of message
            metadata: Additional metadata
        """
        try:
            # Log to repository via SID Service
            if hasattr(self.sid_service, 'log_message'):
                self.sid_service.log_message(sid, content, direction, message_type, metadata)
            
            # Keep console logging for debugging
            logger.info(f"Message logged - SID: {sid}, Direction: {direction}, Type: {message_type}")
            
        except Exception as e:
            logger.error(f"Error logging message: {e}")
    
    def _log_routing_decision(self, sid: str, message: str, skill, 
                             response: Dict[str, Any], execution_time: float) -> None:
        """
        Log routing decision.
        
        Args:
            sid: Session ID
            message: User message
            skill: Selected skill
            response: Skill response
            execution_time: Execution time
        """
        try:
            routing_entry = {
                'sid': sid,
                'timestamp': datetime.utcnow().isoformat(),
                'message': message,
                'skill_used': skill.name if skill else 'none',
                'response_intent': response.get('intent', 'unknown'),
                'execution_time': execution_time,
                'success': response.get('intent') != 'error'
            }
            
            self.route_history.append(routing_entry)
            
            # Keep only last 1000 entries
            if len(self.route_history) > 1000:
                self.route_history = self.route_history[-1000:]
            
        except Exception as e:
            logger.error(f"Error logging routing decision: {e}")
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """
        Get routing statistics.
        
        Returns:
            Dict[str, Any]: Routing statistics
        """
        try:
            total_routes = len(self.route_history)
            successful_routes = sum(1 for entry in self.route_history if entry.get('success', False))
            failed_routes = total_routes - successful_routes
            
            # Calculate average execution time
            execution_times = [entry.get('execution_time', 0) for entry in self.route_history]
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            # Get skill usage stats
            skill_usage = {}
            for entry in self.route_history:
                skill_name = entry.get('skill_used', 'unknown')
                skill_usage[skill_name] = skill_usage.get(skill_name, 0) + 1
            
            return {
                'total_messages': self.total_messages,
                'total_routes': total_routes,
                'successful_routes': successful_routes,
                'failed_routes': failed_routes,
                'success_rate': (successful_routes / total_routes * 100) if total_routes > 0 else 0,
                'average_execution_time': avg_execution_time,
                'error_count': self.error_count,
                'skill_usage': skill_usage,
                'recent_routes': self.route_history[-10:] if self.route_history else []
            }
            
        except Exception as e:
            logger.error(f"Error getting routing stats: {e}")
            return {}
    
    def get_session_routing_history(self, sid: str) -> List[Dict[str, Any]]:
        """
        Get routing history for a specific session.
        
        Args:
            sid: Session ID
            
        Returns:
            List[Dict[str, Any]]: Session routing history
        """
        try:
            return [entry for entry in self.route_history if entry.get('sid') == sid]
        except Exception as e:
            logger.error(f"Error getting session routing history: {e}")
            return []
    
    def get_skill_performance(self, skill_name: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific skill.
        
        Args:
            skill_name: Name of skill
            
        Returns:
            Dict[str, Any]: Skill performance metrics
        """
        try:
            skill_routes = [entry for entry in self.route_history if entry.get('skill_used') == skill_name]
            
            if not skill_routes:
                return {'usage_count': 0}
            
            successful_routes = sum(1 for entry in skill_routes if entry.get('success', False))
            execution_times = [entry.get('execution_time', 0) for entry in skill_routes]
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            return {
                'usage_count': len(skill_routes),
                'success_rate': (successful_routes / len(skill_routes)) * 100,
                'average_execution_time': avg_execution_time,
                'recent_usage': skill_routes[-5:] if skill_routes else []
            }
            
        except Exception as e:
            logger.error(f"Error getting skill performance: {e}")
            return {}
    
    def reset_stats(self) -> None:
        """
        Reset routing statistics.
        """
        try:
            self.route_history = []
            self.error_count = 0
            self.total_messages = 0
            logger.info("Routing statistics reset")
        except Exception as e:
            logger.error(f"Error resetting stats: {e}")
    
    def export_routing_data(self) -> Dict[str, Any]:
        """
        Export routing data for analysis.
        
        Returns:
            Dict[str, Any]: Exported routing data
        """
        try:
            return {
                'route_history': self.route_history,
                'stats': self.get_routing_stats(),
                'exported_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error exporting routing data: {e}")
            return {}