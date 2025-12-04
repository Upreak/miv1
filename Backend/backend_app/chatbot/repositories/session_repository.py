"""
Session Repository for Chatbot/Co-Pilot Module

Handles database operations for chatbot sessions.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from ..models.session_model import Session, UserRole, ConversationState
from ..utils.sid_generator import SIDGenerator


class SessionRepository:
    """
    Repository for chatbot session operations.
    
    Handles CRUD operations and session management queries.
    """
    
    def __init__(self, db: Session):
        """
        Initialize session repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create(self, sid: str, channel: str, channel_user_id: str, 
               user_id: Optional[str] = None, role: UserRole = UserRole.UNKNOWN,
               state: ConversationState = ConversationState.ONBOARDING,
               context: Dict[str, Any] = None) -> Session:
        """
        Create a new session.
        
        Args:
            sid: Session ID
            channel: Platform channel
            channel_user_id: Platform-specific user ID
            user_id: User ID from main system
            role: User role
            state: Conversation state
            context: Session context
            
        Returns:
            Session: Created session
        """
        session = Session(
            sid=sid,
            user_id=user_id,
            channel=channel,
            channel_user_id=channel_user_id,
            role=role,
            state=state,
            context=context or {}
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def get_by_sid(self, sid: str) -> Optional[Session]:
        """
        Get session by SID.
        
        Args:
            sid: Session ID
            
        Returns:
            Optional[Session]: Session or None
        """
        return self.db.query(Session).filter(Session.sid == sid).first()
    
    def get_by_channel_user(self, channel: str, channel_user_id: str) -> Optional[Session]:
        """
        Get session by channel and channel user ID.
        
        Args:
            channel: Platform channel
            channel_user_id: Platform-specific user ID
            
        Returns:
            Optional[Session]: Session or None
        """
        return self.db.query(Session).filter(
            and_(Session.channel == channel, Session.channel_user_id == channel_user_id)
        ).first()
    
    def get_by_user_id(self, user_id: str) -> Optional[Session]:
        """
        Get session by user ID.
        
        Args:
            user_id: User ID from main system
            
        Returns:
            Optional[Session]: Session or None
        """
        return self.db.query(Session).filter(Session.user_id == user_id).first()
    
    def get_active_sessions(self, limit: int = 100) -> List[Session]:
        """
        Get active sessions (recently updated).
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List[Session]: List of active sessions
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=24)  # Last 24 hours
        
        return self.db.query(Session).filter(
            Session.updated_at >= cutoff_time
        ).order_by(desc(Session.updated_at)).limit(limit).all()
    
    def get_sessions_by_channel(self, channel: str, limit: int = 100) -> List[Session]:
        """
        Get sessions by channel.
        
        Args:
            channel: Platform channel
            limit: Maximum number of sessions to return
            
        Returns:
            List[Session]: List of sessions
        """
        return self.db.query(Session).filter(Session.channel == channel).limit(limit).all()
    
    def get_sessions_by_role(self, role: UserRole, limit: int = 100) -> List[Session]:
        """
        Get sessions by user role.
        
        Args:
            role: User role
            limit: Maximum number of sessions to return
            
        Returns:
            List[Session]: List of sessions
        """
        return self.db.query(Session).filter(Session.role == role).limit(limit).all()
    
    def get_sessions_by_state(self, state: ConversationState, limit: int = 100) -> List[Session]:
        """
        Get sessions by conversation state.
        
        Args:
            state: Conversation state
            limit: Maximum number of sessions to return
            
        Returns:
            List[Session]: List of sessions
        """
        return self.db.query(Session).filter(Session.state == state).limit(limit).all()
    
    def update(self, sid: str, **kwargs) -> Optional[Session]:
        """
        Update session.
        
        Args:
            sid: Session ID
            **kwargs: Fields to update
            
        Returns:
            Optional[Session]: Updated session or None
        """
        session = self.get_by_sid(sid)
        if not session:
            return None
        
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        session.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def update_context(self, sid: str, context: Dict[str, Any]) -> Optional[Session]:
        """
        Update session context.
        
        Args:
            sid: Session ID
            context: Context data
            
        Returns:
            Optional[Session]: Updated session or None
        """
        session = self.get_by_sid(sid)
        if not session:
            return None
        
        session.context = context
        session.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def update_state(self, sid: str, state: ConversationState) -> Optional[Session]:
        """
        Update session state.
        
        Args:
            sid: Session ID
            state: New conversation state
            
        Returns:
            Optional[Session]: Updated session or None
        """
        return self.update(sid, state=state)
    
    def update_role(self, sid: str, role: UserRole) -> Optional[Session]:
        """
        Update session role.
        
        Args:
            sid: Session ID
            role: New user role
            
        Returns:
            Optional[Session]: Updated session or None
        """
        return self.update(sid, role=role)
    
    def increment_message_count(self, sid: str) -> Optional[Session]:
        """
        Increment message count for session.
        
        Args:
            sid: Session ID
            
        Returns:
            Optional[Session]: Updated session or None
        """
        session = self.get_by_sid(sid)
        if not session:
            return None
        
        session.message_count += 1
        session.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def set_last_message(self, sid: str, message: str) -> Optional[Session]:
        """
        Set last message for session.
        
        Args:
            sid: Session ID
            message: Last message content
            
        Returns:
            Optional[Session]: Updated session or None
        """
        return self.update(sid, last_message=message)
    
    def delete(self, sid: str) -> bool:
        """
        Delete session.
        
        Args:
            sid: Session ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        session = self.get_by_sid(sid)
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        
        return True
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up old sessions.
        
        Args:
            days_old: Sessions older than this many days will be deleted
            
        Returns:
            int: Number of sessions deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        sessions_to_delete = self.db.query(Session).filter(
            Session.updated_at < cutoff_date
        ).all()
        
        count = len(sessions_to_delete)
        
        for session in sessions_to_delete:
            self.db.delete(session)
        
        self.db.commit()
        
        return count
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get session statistics.
        
        Returns:
            Dict[str, Any]: Session statistics
        """
        total_sessions = self.db.query(Session).count()
        
        # Count by channel
        channel_counts = {}
        for channel in ['whatsapp', 'telegram', 'web']:
            count = self.db.query(Session).filter(Session.channel == channel).count()
            channel_counts[channel] = count
        
        # Count by role
        role_counts = {}
        for role in UserRole:
            count = self.db.query(Session).filter(Session.role == role).count()
            role_counts[role.value] = count
        
        # Count by state
        state_counts = {}
        for state in ConversationState:
            count = self.db.query(Session).filter(Session.state == state).count()
            state_counts[state.value] = count
        
        # Get average message count
        avg_messages = self.db.query(
            Session.message_count
        ).all()
        
        avg_message_count = sum(msg_count[0] for msg_count in avg_messages) / len(avg_messages) if avg_messages else 0
        
        return {
            'total_sessions': total_sessions,
            'channel_distribution': channel_counts,
            'role_distribution': role_counts,
            'state_distribution': state_counts,
            'average_messages_per_session': avg_message_count
        }
    
    def get_recent_activity(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent session activity.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List[Dict[str, Any]]: Recent activity
        """
        sessions = self.db.query(Session).order_by(
            desc(Session.updated_at)
        ).limit(limit).all()
        
        activity = []
        for session in sessions:
            activity.append({
                'sid': session.sid,
                'channel': session.channel,
                'channel_user_id': session.channel_user_id,
                'role': session.role.value,
                'state': session.state.value,
                'message_count': session.message_count,
                'last_message': session.last_message,
                'updated_at': session.updated_at.isoformat()
            })
        
        return activity
    
    def search_sessions(self, query: str, limit: int = 100) -> List[Session]:
        """
        Search sessions by various criteria.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[Session]: Matching sessions
        """
        # Search by channel_user_id, user_id, or last_message
        return self.db.query(Session).filter(
            or_(
                Session.channel_user_id.ilike(f'%{query}%'),
                Session.user_id.ilike(f'%{query}%'),
                Session.last_message.ilike(f'%{query}%')
            )
        ).limit(limit).all()
    
    def validate_sid(self, sid: str) -> bool:
        """
        Validate SID format and existence.
        
        Args:
            sid: Session ID to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Check format
        if not SIDGenerator.validate_sid(sid):
            return False
        
        # Check existence
        session = self.get_by_sid(sid)
        return session is not None
    
    def get_or_create(self, channel: str, channel_user_id: str, 
                     user_id: Optional[str] = None) -> Session:
        """
        Get existing session or create new one.
        
        Args:
            channel: Platform channel
            channel_user_id: Platform-specific user ID
            user_id: User ID from main system
            
        Returns:
            Session: Existing or new session
        """
        session = self.get_by_channel_user(channel, channel_user_id)
        
        if session:
            return session
        
        # Generate new SID
        sid = SIDGenerator.generate_sid_for_user(
            user_id or channel_user_id,
            channel
        )
        
        # Create new session
        return self.create(
            sid=sid,
            channel=channel,
            channel_user_id=channel_user_id,
            user_id=user_id
        )
    
    def bulk_update_state(self, session_sids: List[str], state: ConversationState) -> int:
        """
        Update state for multiple sessions.
        
        Args:
            session_sids: List of session IDs
            state: New conversation state
            
        Returns:
            int: Number of sessions updated
        """
        result = self.db.query(Session).filter(
            Session.sid.in_(session_sids)
        ).update({'state': state, 'updated_at': datetime.utcnow()})
        
        self.db.commit()
        
        return result
    
    def get_sessions_needing_attention(self, hours: int = 1) -> List[Session]:
        """
        Get sessions that haven't been updated recently.
        
        Args:
            hours: Sessions not updated in this many hours
            
        Returns:
            List[Session]: Sessions needing attention
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return self.db.query(Session).filter(
            Session.updated_at < cutoff_time,
            Session.state != ConversationState.IDLE
        ).all()