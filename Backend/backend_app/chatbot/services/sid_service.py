"""
SID Service for Chatbot/Co-Pilot Module

Manages session identification and persistence for users across
WhatsApp, Telegram, and Web platforms.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any

from ..models.session_model import Session, UserRole, ConversationState
from ..repositories.session_repository import SessionRepository
from ..repositories.message_repository import MessageRepository
from ..models.message_log_model import MessageLog, MessageType, MessageDirection
from ..utils.sid_generator import SIDGenerator
from datetime import timedelta

logger = logging.getLogger(__name__)


class SIDService:
    """
    SID Service for managing session identification and persistence.
    
    This service is responsible for:
    - Creating new sessions for users
    - Retrieving existing sessions
    - Updating session state and context
    - Managing user roles and conversation states
    """
    
    def __init__(self, db):
        """
        Initialize SID Service.
        
        Args:
            db: Database session
        """
        self.repo = SessionRepository(db)
        self.message_repo = MessageRepository(db)
    
    def get_or_create(self, channel: str, channel_user_id: str, 
                     user_id: Optional[str] = None) -> Session:
        """
        Get existing session or create new one.
        
        Args:
            channel: Platform channel (whatsapp/telegram/web)
            channel_user_id: Platform-specific user ID
            user_id: Optional user ID from main system
            
        Returns:
            Session: Session object
        """
        try:
            # Try to get existing session
            session = self.repo.get_by_channel_user(channel, channel_user_id)
            
            if session:
                # Update last activity
                session.updated_at = datetime.utcnow()
                session.increment_message_count()
                self.repo.update(session)
                logger.info(f"Retrieved existing session: {session.sid}")
                return session
            
            # Create new session
            new_sid = SIDGenerator.generate_sid_for_user(channel_user_id, channel)
            session = self.repo.create(
                sid=new_sid,
                channel=channel,
                channel_user_id=channel_user_id,
                user_id=user_id
            )
            
            logger.info(f"Created new session: {new_sid} for {channel}:{channel_user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error in get_or_create: {e}")
            raise
    
    def get_by_sid(self, sid: str) -> Optional[Session]:
        """
        Get session by SID.
        
        Args:
            sid: Session ID
            
        Returns:
            Optional[Session]: Session object or None
        """
        try:
            return self.repo.get_by_sid(sid)
        except Exception as e:
            logger.error(f"Error getting session by SID {sid}: {e}")
            return None
    
    def update_session_state(self, sid: str, state: ConversationState) -> bool:
        """
        Update session state.
        
        Args:
            sid: Session ID
            state: New conversation state
            
        Returns:
            bool: True if updated successfully
        """
        try:
            session = self.repo.get_by_sid(sid)
            if session:
                session.set_state(state)
                self.repo.update(session)
                logger.info(f"Updated session {sid} state to {state}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating session state: {e}")
            return False
    
    def update_user_role(self, sid: str, role: UserRole) -> bool:
        """
        Update user role in session.
        
        Args:
            sid: Session ID
            role: User role
            
        Returns:
            bool: True if updated successfully
        """
        try:
            session = self.repo.get_by_sid(sid)
            if session:
                session.set_role(role)
                self.repo.update(session)
                logger.info(f"Updated session {sid} role to {role}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            return False
    
    def update_context(self, sid: str, key: str, value: Any) -> bool:
        """
        Update session context.
        
        Args:
            sid: Session ID
            key: Context key
            value: Context value
            
        Returns:
            bool: True if updated successfully
        """
        try:
            session = self.repo.get_by_sid(sid)
            if session:
                session.update_context(key, value)
                self.repo.update(session)
                logger.info(f"Updated session {sid} context: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating context: {e}")
            return False
    
    def get_context(self, sid: str, key: str, default: Any = None) -> Any:
        """
        Get context value from session.
        
        Args:
            sid: Session ID
            key: Context key
            default: Default value if key not found
            
        Returns:
            Any: Context value or default
        """
        try:
            session = self.repo.get_by_sid(sid)
            if session:
                return session.get_context(key, default)
            return default
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return default
    
    def increment_message_count(self, sid: str) -> bool:
        """
        Increment message count for session.
        
        Args:
            sid: Session ID
            
        Returns:
            bool: True if incremented successfully
        """
        try:
            session = self.repo.get_by_sid(sid)
            if session:
                session.increment_message_count()
                self.repo.update(session)
                return True
            return False
        except Exception as e:
            logger.error(f"Error incrementing message count: {e}")
            return False
    
    def update_last_message(self, sid: str, message: str) -> bool:
        """
        Update last message for session.
        
        Args:
            sid: Session ID
            message: Last message content
            
        Returns:
            bool: True if updated successfully
        """
        try:
            session = self.repo.get_by_sid(sid)
            if session:
                session.last_message = message
                session.updated_at = datetime.utcnow()
                self.repo.update(session)
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating last message: {e}")
            return False
    
    def get_session_stats(self, sid: str) -> Dict[str, Any]:
        """
        Get session statistics.
        
        Args:
            sid: Session ID
            
        Returns:
            Dict[str, Any]: Session statistics
        """
        try:
            session = self.repo.get_by_sid(sid)
            if session:
                return {
                    'sid': session.sid,
                    'channel': session.channel,
                    'channel_user_id': session.channel_user_id,
                    'user_id': session.user_id,
                    'role': session.role.value if session.role else None,
                    'state': session.state.value if session.state else None,
                    'message_count': session.message_count,
                    'created_at': session.created_at.isoformat(),
                    'updated_at': session.updated_at.isoformat(),
                    'last_message': session.last_message,
                    'context_size': len(session.context) if session.context else 0
                }
            return {}
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return {}
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up old sessions.
        
        Args:
            days_old: Age threshold in days
            
        Returns:
            int: Number of sessions cleaned up
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            count = self.repo.delete_old_sessions(cutoff_date)
            logger.info(f"Cleaned up {count} old sessions")
            return count
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
            return 0
    
    def get_active_sessions(self, channel: Optional[str] = None) -> list:
        """
        Get active sessions.
        
        Args:
            channel: Optional channel filter
            
        Returns:
            list: List of active sessions
        """
        try:
            return self.repo.get_active_sessions(channel)
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return []
    
    def get_sessions_by_role(self, role: UserRole) -> list:
        """
        Get sessions by user role.
        
        Args:
            role: User role
            
        Returns:
            list: List of sessions
        """
        try:
            return self.repo.get_sessions_by_role(role)
        except Exception as e:
            logger.error(f"Error getting sessions by role: {e}")
            return []
    
    def get_sessions_by_state(self, state: ConversationState) -> list:
        """
        Get sessions by conversation state.
        
        Args:
            state: Conversation state
            
        Returns:
            list: List of sessions
        """
        try:
            return self.repo.get_sessions_by_state(state)
        except Exception as e:
            logger.error(f"Error getting sessions by state: {e}")
            return []
    
    def transfer_session(self, sid: str, new_user_id: str) -> bool:
        """
        Transfer session to different user.
        
        Args:
            sid: Session ID
            new_user_id: New user ID
            
        Returns:
            bool: True if transferred successfully
        """
        try:
            session = self.repo.get_by_sid(sid)
            if session:
                session.user_id = new_user_id
                session.updated_at = datetime.utcnow()
                self.repo.update(session)
                logger.info(f"Transferred session {sid} to user {new_user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error transferring session: {e}")
            return False
    
    def clone_session(self, sid: str, new_channel_user_id: str) -> Optional[str]:
        """
        Clone session for different user.
        
        Args:
            sid: Original session ID
            new_channel_user_id: New channel user ID
            
        Returns:
            Optional[str]: New session ID or None
        """
        try:
            original_session = self.repo.get_by_sid(sid)
            if not original_session:
                return None
            
            # Create new session with same context
            new_sid = SIDGenerator.generate_sid_for_user(new_channel_user_id, original_session.channel)
            new_session = self.repo.create(
                sid=new_sid,
                channel=original_session.channel,
                channel_user_id=new_channel_user_id,
                user_id=original_session.user_id,
                role=original_session.role,
                state=original_session.state,
                context=original_session.context.copy()
            )
            
            logger.info(f"Cloned session {sid} to {new_sid}")
            return new_sid
        except Exception as e:
            logger.error(f"Error cloning session: {e}")
            return None
    
    def validate_session(self, sid: str) -> bool:
        """
        Validate session exists and is active.
        
        Args:
            sid: Session ID
            
        Returns:
            bool: True if session is valid
        """
        try:
            session = self.repo.get_by_sid(sid)
            if not session:
                return False
            
            # Check if session is too old (e.g., 30 days)
            if datetime.utcnow() - session.updated_at > timedelta(days=30):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return False
    
    def get_session_history(self, sid: str, limit: int = 10) -> list:
        """
        Get session message history.
        
        Args:
            sid: Session ID
            limit: Maximum number of messages to return
            
        Returns:
            list: List of message logs
        """
        try:
            return self.message_repo.get_conversation_history(sid, limit)
        except Exception as e:
            logger.error(f"Error getting session history: {e}")
            return []
            
    def log_message(self, sid: str, content: str, direction: str, 
                   message_type: str = "text", metadata: Dict[str, Any] = None) -> Optional[MessageLog]:
        """
        Log a message to the repository.
        
        Args:
            sid: Session ID
            content: Message content
            direction: Message direction (inbound/outbound/system)
            message_type: Type of message
            metadata: Additional metadata
            
        Returns:
            Optional[MessageLog]: Created message log
        """
        try:
            # Convert string direction to enum if needed
            dir_enum = MessageDirection.INBOUND
            if isinstance(direction, str):
                if direction.lower() == 'outbound':
                    dir_enum = MessageDirection.OUTBOUND
                elif direction.lower() == 'system':
                    dir_enum = MessageDirection.SYSTEM
            elif isinstance(direction, MessageDirection):
                dir_enum = direction
                
            # Convert string type to enum if needed
            type_enum = MessageType.TEXT
            if isinstance(message_type, str):
                try:
                    type_enum = MessageType(message_type.lower())
                except ValueError:
                    type_enum = MessageType.TEXT
            elif isinstance(message_type, MessageType):
                type_enum = message_type
                
            return self.message_repo.create(
                sid=sid,
                message_id=None,  # Auto-generated or provided by platform
                message_type=type_enum,
                direction=dir_enum,
                content=content,
                platform=metadata.get('platform', 'unknown') if metadata else 'unknown',
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Error logging message: {e}")
            return None
    
    def export_session_data(self, sid: str) -> Dict[str, Any]:
        """
        Export session data.
        
        Args:
            sid: Session ID
            
        Returns:
            Dict[str, Any]: Exported session data
        """
        try:
            session = self.repo.get_by_sid(sid)
            if not session:
                return {}
            
            return {
                'session': session.to_dict(),
                'history': self.get_session_history(sid),
                'exported_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error exporting session data: {e}")
            return {}