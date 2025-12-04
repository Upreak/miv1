"""
Chatbot Models Module

This module contains all database models and conversation state management
classes for the Chatbot/Co-Pilot system.
"""

from .session_model import Session, UserRole, ConversationState
from .message_log_model import MessageLog, MessageType, MessageDirection
from .conversation_state import (
    ConversationContext,
    ConversationStateManager,
    SkillContext,
    UserRole as ConversationUserRole,
    ConversationState as ConversationStateEnum
)

__all__ = [
    # Session Model
    'Session',
    'UserRole',
    'ConversationState',
    
    # Message Log Model
    'MessageLog',
    'MessageType',
    'MessageDirection',
    
    # Conversation State
    'ConversationContext',
    'ConversationStateManager',
    'SkillContext',
    'ConversationUserRole',
    'ConversationStateEnum'
]