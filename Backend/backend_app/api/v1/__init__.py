"""
API v1 module initialization
"""

# Import all API routers
from . import auth, whatsapp, telegram, extraction, brain, chatbot

# Export routers for easy inclusion in main app
__all__ = ["auth", "whatsapp", "telegram", "extraction", "brain", "chatbot"]