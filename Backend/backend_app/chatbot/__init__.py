"""
Chatbot / Co-Pilot Module

This module provides a modular, pluggable framework for AI-powered conversations
across WhatsApp, Telegram, and Web platforms. It orchestrates candidate onboarding,
recruiter workflows, and serves as the AI interface layer connecting all systems.

Key Components:
- SID (Session Manager) for persistent conversation state
- Message Router for skill-based message handling
- Modular AI Skills (Onboarding, Resume Intake, Matching, etc.)
- Webhook endpoints for WhatsApp/Telegram
- LLM Service for AI responses
- Celery workers for long-running tasks
"""

from .services.sid_service import SIDService
from .services.message_router import MessageRouter
from .services.skill_registry import SkillRegistry
from .services.copilot_service import CoPilotService
from .services.llm_service import LLMService

__all__ = [
    'SIDService',
    'MessageRouter', 
    'SkillRegistry',
    'CoPilotService',
    'LLMService'
]