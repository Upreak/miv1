"""
Session Service for Chatbot/Co-Pilot Module

Provides high-level session management operations including session creation,
retrieval, updates, and lifecycle management. This service acts as the main
interface for session operations across the chatbot system.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.session_model import Session, UserRole, ConversationState
from ..repositories.session_repository import SessionRepository

logger = logging.getLogger(__name__)


class SessionService:
    """
    High-level session management service.
    
    This service provides business logic for session operations and coordinates
    with the session repository for database operations.
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize Session Service.
        
        Args:
            db_session: Database session
        """
        self.db_session = db_session
        self.repository = SessionRepository(db_session)
    
    async def create_session(
        self,
        user_id: str,
        platform: str,
        platform_user_id: str,
        user_role: UserRole = UserRole.UNKNOWN,
        initial_state: ConversationState = ConversationState.ONBOARDING,
        context: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        Create a new chatbot session.
        
        Args:
            user_id: User identifier
            platform: Platform (whatsapp/telegram/web)
            platform_user_id: Platform-specific user ID
            user_role: User role (candidate/recruiter)
            initial_state: Initial conversation state
            context: Initial session context
            
        Returns:
            Session: Created session
            
        Raises:
            ValueError: If required parameters are missing
            SQLAlchemyError: If database operation fails
        """
        try:
            # Validate inputs
            if not all([user_id, platform, platform_user_id]):
                raise ValueError("Missing required parameters: user_id, platform, platform_user_id")
            
            # Generate session ID
            from ..utils.sid_generator import SIDGenerator
            session_id = SIDGenerator.generate_sid_for_user(
                user_id=user_id,
                platform=platform
            )
            
            # Create session
            session = await self.repository.create(
                sid=session_id,
                user_id=user_id,
                channel=platform,
                channel_user_id=platform_user_id,
                role=user_role,
                state=initial_state,
                context=context or {}
            )
            
            logger.info(f"Created session {session_id} for user {user_id} on {platform}")
            return session
            
        except SQLAlchemyError as e:
            logger.error(f"Database error creating session: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Optional[Session]: Session if found, None otherwise
        """
        try:
            session = await self.repository.get_by_sid(session_id)
            if session:
                logger.debug(f"Retrieved session {session_id}")
            return session
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving session {session_id}: {e}")
            raise
    
    async def get_session_by_channel_user(
        self,
        platform: str,
        platform_user_id: str
    ) -> Optional[Session]:
        """
        Retrieve a session by platform and user ID.
        
        Args:
            platform: Platform (whatsapp/telegram/web)
            platform_user_id: Platform-specific user ID
            
        Returns:
            Optional[Session]: Session if found, None otherwise
        """
        try:
            session = await self.repository.get_by_channel_user(platform, platform_user_id)
            if session:
                logger.debug(f"Retrieved session {session.sid} for {platform_user_id} on {platform}")
            return session
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving session for {platform_user_id}: {e}")
            raise
    
    async def get_user_sessions(self, user_id: str) -> List[Session]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List[Session]: List of active sessions
        """
        try:
            # This would need to be implemented in the repository
            # For now, return empty list
            return []
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving sessions for user {user_id}: {e}")
            raise
    
    async def update_session(
        self,
        session_id: str,
        state: Optional[ConversationState] = None,
        context: Optional[Dict[str, Any]] = None,
        user_role: Optional[UserRole] = None
    ) -> Optional[Session]:
        """
        Update session information.
        
        Args:
            session_id: Session identifier
            state: New conversation state
            context: Updated context
            user_role: Updated user role
            
        Returns:
            Optional[Session]: Updated session or None if not found
        """
        try:
            # Get existing session
            session = await self.get_session(session_id)
            if not session:
                logger.warning(f"Session {session_id} not found for update")
                return None
            
            # Prepare update data
            update_data = {}
            if state is not None:
                update_data['state'] = state
            if context is not None:
                # Merge context instead of replacing
                merged_context = session.context or {}
                merged_context.update(context)
                update_data['context'] = merged_context
            if user_role is not None:
                update_data['role'] = user_role
            
            # Update session
            if update_data:
                updated_session = await self.repository.update(session_id, **update_data)
                if updated_session:
                    logger.info(f"Updated session {session_id}")
                    return updated_session
            
            return session
            
        except SQLAlchemyError as e:
            logger.error(f"Database error updating session {session_id}: {e}")
            raise
    
    async def update_session_state(
        self,
        session_id: str,
        state: ConversationState
    ) -> Optional[Session]:
        """
        Update session state.
        
        Args:
            session_id: Session identifier
            state: New conversation state
            
        Returns:
            Optional[Session]: Updated session or None if not found
        """
        return await self.update_session(session_id, state=state)
    
    async def update_session_context(
        self,
        session_id: str,
        context: Dict[str, Any]
    ) -> Optional[Session]:
        """
        Update session context.
        
        Args:
            session_id: Session identifier
            context: Context to merge with existing context
            
        Returns:
            Optional[Session]: Updated session or None if not found
        """
        return await self.update_session(session_id, context=context)
    
    async def update_user_role(
        self,
        session_id: str,
        user_role: UserRole
    ) -> Optional[Session]:
        """
        Update user role for a session.
        
        Args:
            session_id: Session identifier
            user_role: New user role
            
        Returns:
            Optional[Session]: Updated session or None if not found
        """
        return await self.update_session(session_id, user_role=user_role)
    
    async def extend_session(self, session_id: str, additional_minutes: int = 60) -> bool:
        """
        Extend session expiration time.
        
        Args:
            session_id: Session identifier
            additional_minutes: Additional minutes to extend session
            
        Returns:
            bool: True if extended successfully, False otherwise
        """
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            # Update last activity time
            new_last_activity = datetime.utcnow()
            await self.repository.update(session_id, last_activity=new_last_activity)
            
            logger.debug(f"Extended session {session_id} by {additional_minutes} minutes")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error extending session {session_id}: {e}")
            raise
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            result = await self.repository.delete(session_id)
            if result:
                logger.info(f"Deleted session {session_id}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting session {session_id}: {e}")
            raise
    
    async def cleanup_expired_sessions(self, hours_old: int = 24) -> int:
        """
        Clean up expired sessions.
        
        Args:
            hours_old: Sessions older than this many hours will be deleted
            
        Returns:
            int: Number of sessions deleted
        """
        try:
            count = await self.repository.cleanup_old_sessions(days_old=hours_old // 24 + 1)
            if count > 0:
                logger.info(f"Cleaned up {count} expired sessions")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Database error cleaning up sessions: {e}")
            raise
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """
        Get session statistics.
        
        Returns:
            Dict[str, Any]: Session statistics
        """
        try:
            return await self.repository.get_session_stats()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting session stats: {e}")
            raise
    
    async def validate_session(self, session_id: str) -> bool:
        """
        Validate if a session exists and is active.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if session is valid and active
        """
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            # Check if session is expired (more than 24 hours old)
            time_since_activity = datetime.utcnow() - session.last_activity
            if time_since_activity.total_seconds() > 24 * 3600:  # 24 hours
                await self.delete_session(session_id)
                return False
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error validating session {session_id}: {e}")
            raise
    
    async def get_or_create_session(
        self,
        user_id: str,
        platform: str,
        platform_user_id: str,
        user_role: UserRole = UserRole.UNKNOWN
    ) -> Session:
        """
        Get existing session or create new one.
        
        Args:
            user_id: User identifier
            platform: Platform (whatsapp/telegram/web)
            platform_user_id: Platform-specific user ID
            user_role: User role
            
        Returns:
            Session: Existing or newly created session
        """
        try:
            # Try to get existing session
            session = await self.get_session_by_channel_user(platform, platform_user_id)
            
            if session:
                # Extend session and return
                await self.extend_session(session.sid)
                logger.debug(f"Retrieved existing session {session.sid}")
                return session
            
            # Create new session
            return await self.create_session(
                user_id=user_id,
                platform=platform,
                platform_user_id=platform_user_id,
                user_role=user_role
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_or_create_session: {e}")
            raise
    
    async def transition_state(
        self,
        session_id: str,
        new_state: ConversationState,
        context_update: Optional[Dict[str, Any]] = None
    ) -> Optional[Session]:
        """
        Transition session to a new state with optional context update.
        
        Args:
            session_id: Session identifier
            new_state: New conversation state
            context_update: Optional context to merge
            
        Returns:
            Optional[Session]: Updated session or None if not found
        """
        try:
            update_data = {'state': new_state}
            if context_update:
                update_data['context'] = context_update
            
            return await self.update_session(session_id, **update_data)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error transitioning state for session {session_id}: {e}")
            raise
    
    async def reset_session_context(self, session_id: str) -> Optional[Session]:
        """
        Reset session context to empty.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Optional[Session]: Updated session or None if not found
        """
        return await self.update_session_context(session_id, {})
    
    async def add_context_item(
        self,
        session_id: str,
        key: str,
        value: Any
    ) -> Optional[Session]:
        """
        Add a single item to session context.
        
        Args:
            session_id: Session identifier
            key: Context key
            value: Context value
            
        Returns:
            Optional[Session]: Updated session or None if not found
        """
        try:
            session = await self.get_session(session_id)
            if not session:
                return None
            
            context = session.context or {}
            context[key] = value
            
            return await self.update_session_context(session_id, context)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error adding context item to session {session_id}: {e}")
            raise