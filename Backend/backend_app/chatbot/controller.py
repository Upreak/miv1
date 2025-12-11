"""
Chatbot Controller
High-level orchestration for chatbot functionality
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException
from backend_app.chatbot.services.sid_service import SIDService
from backend_app.chatbot.services.message_router import MessageRouter
from backend_app.chatbot.services.llm_service import LLMService
from backend_app.chatbot.models.session_model import UserRole
from backend_app.chatbot.skill_registry import (
    get_skill_registry,
    get_message_router,
    get_sid_service,
    get_llm_service,
    initialize_chatbot_system
)
import logging

logger = logging.getLogger(__name__)


class ChatbotController:
    """Main controller for chatbot operations"""
    
    def __init__(self, db_session=None):
        # Initialize the chatbot system if not already done
        initialize_chatbot_system(db_session)
        
        # Get services from the global registry
        self.sid_service = get_sid_service()
        self.message_router = get_message_router()
        self.llm_service = get_llm_service()
        self.skill_registry = get_skill_registry()
        
        if not all([self.sid_service, self.message_router, self.llm_service, self.skill_registry]):
            logger.error("Failed to initialize chatbot controller services")
            raise HTTPException(status_code=500, detail="Chatbot system initialization failed")
    
    async def start_session(
        self, 
        user_id: str, 
        platform: str, 
        platform_user_id: str,
        user_role: UserRole
    ) -> Dict[str, Any]:
        """Start a new chatbot session"""
        try:
            session = await self.sid_service.create_session(
                user_id=user_id,
                platform=platform,
                platform_user_id=platform_user_id,
                user_role=user_role
            )
            return {
                "session_id": session.id,
                "user_id": session.user_id,
                "platform": session.platform,
                "user_role": session.user_role.value,
                "created_at": session.created_at
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")
    
    async def process_message(
        self,
        session_id: str,
        message: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """Process an incoming message"""
        try:
            session = await self.sid_service.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Route message to appropriate skill
            response = await self.message_router.route_with_context(
                sid=session_id,
                message=message,
                context={'message_type': message_type}
            )
            
            return response
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session details"""
        try:
            session = await self.sid_service.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            return {
                "session_id": session.id,
                "user_id": session.user_id,
                "platform": session.platform,
                "user_role": session.user_role.value,
                "state": session.state.value,
                "context": session.context,
                "created_at": session.created_at,
                "updated_at": session.updated_at
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")
    
    async def update_session_state(
        self,
        session_id: str,
        state: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update session state and context"""
        try:
            session = await self.sid_service.update_session(
                session_id=session_id,
                state=state,
                context=context
            )
            
            return {
                "session_id": session.id,
                "state": session.state.value,
                "context": session.context,
                "updated_at": session.updated_at
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")