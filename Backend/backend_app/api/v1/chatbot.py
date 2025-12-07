"""
Chatbot API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend_app.db.connection import get_db
from backend_app.chatbot.controller import ChatbotController
from backend_app.chatbot.models.session_model import UserRole, ConversationState

router = APIRouter()


@router.post("/start-session")
async def start_session(
    user_id: str,
    platform: str,
    platform_user_id: str,
    user_role: UserRole,
    db: AsyncSession = Depends(get_db)
):
    """Start a new chatbot session"""
    try:
        controller = ChatbotController()
        result = await controller.start_session(user_id, platform, platform_user_id, user_role)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message")
async def process_message(
    session_id: str,
    message: str,
    message_type: str = "text",
    db: AsyncSession = Depends(get_db)
):
    """Process an incoming message"""
    try:
        controller = ChatbotController()
        result = await controller.process_message(session_id, message, message_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get session details"""
    try:
        controller = ChatbotController()
        result = await controller.get_session(session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/session/{session_id}/state")
async def update_session_state(
    session_id: str,
    state: ConversationState,
    context: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db)
):
    """Update session state and context"""
    try:
        controller = ChatbotController()
        result = await controller.update_session_state(session_id, state, context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
