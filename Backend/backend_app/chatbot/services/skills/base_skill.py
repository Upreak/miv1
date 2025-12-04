"""
Base Skill Class for Chatbot/Co-Pilot Module

Abstract base class that all chatbot skills must inherit from.
Provides common functionality and interface for skills.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List

from ...models.conversation_state import ConversationState

logger = logging.getLogger(__name__)


class BaseSkill(ABC):
    """
    Abstract base class for all chatbot skills.
    
    All skills must implement the following methods:
    - can_handle(state, message, context): Check if skill can handle the current state
    - handle(sid, message, context): Handle the message and return response
    
    Skills can optionally override:
    - get_handled_states(): List of states this skill can handle
    - get_required_fields(): List of required context fields
    - get_validation_rules(): Validation rules for context fields
    - get_response_templates(): Response templates for different scenarios
    - get_execution_stats(): Execution statistics
    """
    
    def __init__(self, name: str, description: str, priority: int = 10):
        """
        Initialize skill.
        
        Args:
            name: Skill name
            description: Skill description
            priority: Skill priority (higher numbers = higher priority)
        """
        self.name = name
        self.description = description
        self.priority = priority
        self.created_at = datetime.utcnow()
        
        # Execution statistics
        self.execution_count = 0
        self.success_count = 0
        self.error_count = 0
        
        logger.info(f"Initialized skill: {name} with priority {priority}")
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    def get_handled_states(self) -> List[ConversationState]:
        """
        Get list of states this skill can handle.
        
        Returns:
            List[ConversationState]: List of handled states
        """
        return []
    
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
        return {}
    
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
    
    def validate_context(self, context: Dict[str, Any]) -> bool:
        """
        Validate context against required fields and rules.
        
        Args:
            context: Context dictionary
            
        Returns:
            bool: True if context is valid, False otherwise
        """
        try:
            # Check required fields
            required_fields = self.get_required_fields()
            for field in required_fields:
                if field not in context:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Check validation rules
            validation_rules = self.get_validation_rules()
            for field, rule in validation_rules.items():
                if field in context:
                    try:
                        if not rule(context[field]):
                            logger.error(f"Validation failed for field: {field}")
                            return False
                    except Exception as e:
                        logger.error(f"Error validating field {field}: {e}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating context: {e}")
            return False
    
    def create_response(self, text: str, intent: str = "success", 
                       confidence: float = 0.9, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a standardized response.
        
        Args:
            text: Response text
            intent: Response intent
            confidence: Confidence score (0.0 to 1.0)
            metadata: Additional metadata
            
        Returns:
            Dict[str, Any]: Standardized response
        """
        response = {
            'text': text,
            'intent': intent,
            'confidence': confidence,
            'timestamp': datetime.utcnow().isoformat(),
            'skill_used': self.name,
            'metadata': metadata or {}
        }
        
        return response
    
    def log_execution(self, sid: str, message: str, success: bool, 
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
    
    def get_skill_info(self) -> Dict[str, Any]:
        """
        Get skill information.
        
        Returns:
            Dict[str, Any]: Skill information
        """
        return {
            'name': self.name,
            'description': self.description,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'handled_states': [state.value for state in self.get_handled_states()],
            'required_fields': self.get_required_fields(),
            'validation_rules': self.get_validation_rules(),
            'response_templates': self.get_response_templates(),
            'execution_stats': self.get_execution_stats()
        }
    
    def __str__(self) -> str:
        """String representation of the skill."""
        return f"Skill(name='{self.name}', priority={self.priority})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the skill."""
        return (f"BaseSkill(name='{self.name}', description='{self.description}', "
                f"priority={self.priority}, created_at='{self.created_at.isoformat()}')")
    
    def __eq__(self, other) -> bool:
        """Check if two skills are equal."""
        if not isinstance(other, BaseSkill):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int:
        """Hash of the skill."""
        return hash(self.name)
    
    def __lt__(self, other) -> bool:
        """Compare skills by priority."""
        if not isinstance(other, BaseSkill):
            return NotImplemented
        return self.priority > other.priority  # Higher priority = "less than" for sorting
    
    def __le__(self, other) -> bool:
        """Compare skills by priority."""
        if not isinstance(other, BaseSkill):
            return NotImplemented
        return self.priority >= other.priority
    
    def __gt__(self, other) -> bool:
        """Compare skills by priority."""
        if not isinstance(other, BaseSkill):
            return NotImplemented
        return self.priority < other.priority
    
    def __ge__(self, other) -> bool:
        """Compare skills by priority."""
        if not isinstance(other, BaseSkill):
            return NotImplemented
        return self.priority <= other.priority