"""
Production-Ready Telegram Bot Service
Complete Telegram bot integration with error handling, rate limiting, and monitoring
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from collections import defaultdict, deque
from datetime import datetime, timedelta
import aiohttp
import httpx
from fastapi import HTTPException

from backend_app.config.telegram_config import (
    telegram_settings, 
    TelegramSecurityManager
)
from backend_app.chatbot.controller import ChatbotController
from backend_app.chatbot.models.session_model import UserRole

logger = logging.getLogger(__name__)


@dataclass
class TelegramMessage:
    """Telegram message data structure"""
    chat_id: int
    message_id: int
    text: str
    message_type: str
    user_id: Optional[int] = None
    username: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = None


@dataclass
class TelegramResponse:
    """Telegram API response structure"""
    success: bool
    message_id: Optional[int] = None
    error_message: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None


class RateLimiter:
    """Rate limiter for Telegram API requests"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for the given key"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Remove old requests
        if key in self.requests:
            while self.requests[key] and self.requests[key][0] < window_start:
                self.requests[key].popleft()
        
        # Check if under limit
        return len(self.requests[key]) < self.max_requests
    
    def record_request(self, key: str):
        """Record a request for the given key"""
        self.requests[key].append(time.time())


class TelegramBotService:
    """Production-ready Telegram bot service"""
    
    def __init__(self):
        self.session = None
        self.rate_limiter = RateLimiter(
            telegram_settings.TELEGRAM_RATE_LIMIT_REQUESTS,
            telegram_settings.TELEGRAM_RATE_LIMIT_WINDOW
        )
        self.chatbot_controller = None
        self.message_handlers: List[Callable] = []
        self._initialized = False
    
    async def initialize(self):
        """Initialize the Telegram bot service"""
        if self._initialized:
            return
        
        try:
            # Validate configuration
            validation_issues = telegram_settings.validate_configuration()
            if validation_issues:
                raise ValueError(f"Configuration issues: {validation_issues}")
            
            # Create HTTP session
            if not telegram_settings.TELEGRAM_MOCK_MODE:
                self.session = httpx.AsyncClient(
                    timeout=httpx.Timeout(telegram_settings.TELEGRAM_TIMEOUT),
                    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
                )
            
            # Initialize chatbot controller
            self.chatbot_controller = ChatbotController()
            
            logger.info("Telegram bot service initialized successfully")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot service: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the Telegram bot service"""
        if self.session:
            await self.session.aclose()
        self._initialized = False
        logger.info("Telegram bot service shutdown complete")
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming Telegram webhook"""
        try:
            # Secret validation is already done in telegram.py endpoint
            # No need to validate again here
            
            # Process message
            message_data = payload.get("message") or payload.get("edited_message")

            
            # Handle Callback Query (Buttons)
            if not message_data:
                callback_data = payload.get("callback_query")
                if callback_data:
                    return await self._handle_callback_query(callback_data)
                return {"status": "ignored", "reason": "no_message"}
            
            # Parse message
            telegram_message = self._parse_telegram_message(message_data)
            
            # Rate limiting
            if not self.rate_limiter.is_allowed(f"user:{telegram_message.user_id}"):
                await self._send_rate_limit_message(telegram_message.chat_id)
                return {"status": "rate_limited"}
            
            # Record request
            self.rate_limiter.record_request(f"user:{telegram_message.user_id}")
            
            # Process message
            response = await self._handle_message(telegram_message)
            
            return {
                "status": "processed",
                "message_id": telegram_message.message_id,
                "response_sent": response.success
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return {"status": "error", "error": str(e)}
    
    def _parse_telegram_message(self, message_data: Dict[str, Any]) -> TelegramMessage:
        """Parse Telegram message data into TelegramMessage object"""
        chat = message_data.get("chat", {})
        from_user = message_data.get("from", {})
        
        # Determine message type and content
        message_type = "text"
        text_content = ""
        metadata = {}
        
        if "text" in message_data:
            text_content = message_data["text"]
            message_type = "text"
        elif "photo" in message_data:
            message_type = "photo"
            metadata["photos"] = message_data["photo"]
        elif "document" in message_data:
            message_type = "document"
            metadata["document"] = message_data["document"]
        elif "voice" in message_data:
            message_type = "voice"
            metadata["voice"] = message_data["voice"]
        elif "video" in message_data:
            message_type = "video"
            metadata["video"] = message_data["video"]
        elif "location" in message_data:
            message_type = "location"
            metadata["location"] = message_data["location"]
        elif "contact" in message_data:
            message_type = "contact"
            metadata["contact"] = message_data["contact"]
        
        return TelegramMessage(
            chat_id=chat.get("id"),
            message_id=message_data.get("message_id"),
            text=TelegramSecurityManager.sanitize_telegram_input(text_content),
            message_type=message_type,
            user_id=from_user.get("id"),
            username=from_user.get("username"),
            timestamp=datetime.fromtimestamp(message_data.get("date", 0)) if message_data.get("date") else None,
            metadata=metadata
        )
    
    async def _handle_message(self, message: TelegramMessage) -> TelegramResponse:
        """Handle incoming message and generate response"""
        try:
            # Handle special commands
            if message.text.startswith("/"):
                return await self._handle_command(message)
            
            # Handle regular messages
            return await self._handle_text_message(message)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return await self._send_error_message(message.chat_id)
    
    async def _handle_command(self, message: TelegramMessage) -> TelegramResponse:
        """Handle Telegram commands"""
        command = message.text.strip().lower()
        
        if command == "/start":
            return await self._send_welcome_message(message.chat_id, message.username)
        elif command == "/help":
            return await self._send_help_message(message.chat_id)
        elif command == "/high":
            return await self._send_high_response(message.chat_id)
        else:
            return await self._send_unknown_command(message.chat_id)
    
    async def _handle_text_message(self, message: TelegramMessage) -> TelegramResponse:
        """Handle regular text messages"""
        try:
            logger.info(f"Processing text message: '{message.text}' from user {message.user_id}")
            
            # --- CHATBOT ENGINE INTEGRATION ---
            
            # 1. Initialize Engine (Lazy Load)
            if not hasattr(self, "chatbot_engine"):
                 from backend_app.chatbot.skill_registry import get_sid_service
                 from backend_app.chatbot.engine.flow_manager import FlowManager
                 from backend_app.chatbot.engine.chatbot_engine import ChatbotEngine
                 
                 # Initialize FlowManager
                 flow_path = "Backend/backend_app/chatbot/engine/candidate_flow.json"
                 flow_manager = FlowManager(flow_path)
                 
                 # Get Session Service (SID Service)
                 session_service = get_sid_service()
                 
                 self.chatbot_engine = ChatbotEngine(flow_manager, session_service)

            # 2. Process with Engine
            # Use 'input_text' for text messages
            sid = f"telegram:{message.chat_id}"
            response_messages = await self.chatbot_engine.process_message(
                user_id=str(message.user_id),
                input_text=message.text,
                platform="telegram",
                metadata=message.metadata
            )

            # 3. Send Responses
            last_response = None
            for resp in response_messages:
                reply_markup = None
                if resp.buttons:
                    # Convert buttons to InlineKeyboardMarkup
                    inline_keyboard = [
                        [{"text": btn.text, "callback_data": btn.payload}] 
                        for btn in resp.buttons
                    ]
                    reply_markup = {"inline_keyboard": inline_keyboard}

                last_response = await self._send_message(
                    chat_id=message.chat_id,
                    text=resp.text,
                    reply_markup=reply_markup
                )
            
            # Return the result of the last message sent (or success if list was empty but processed)
            if last_response:
                return last_response
            else:
                # No response generated (maybe internal state update only)
                return TelegramResponse(success=True)
            
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            return await self._send_error_message(message.chat_id)
    
    def _generate_intelligent_response(self, text: str) -> str:
        """Generate intelligent response based on message content"""
        text_lower = text.lower().strip()
        
        # Job-related queries
        if any(word in text_lower for word in ["job", "position", "career", "opportunity"]):
            return (
                "I can help you with job opportunities! 📋\n\n"
                "Please share your resume or tell me:\n"
                "• Your preferred job roles\n"
                "• Skills and experience\n"
                "• Location preferences\n\n"
                "I'll find matching positions for you!"
            )
        
        # Resume-related queries
        elif any(word in text_lower for word in ["resume", "cv", "curriculum", "experience"]):
            return (
                "Great! Please upload your resume (PDF/DOCX) and I'll:\n"
                "✅ Analyze your qualifications\n"
                "✅ Match with suitable positions\n"
                "✅ Provide feedback\n"
                "✅ Help with job applications\n\n"
                "You can also tell me about your skills and experience!"
            )
        
        # Company information
        elif any(word in text_lower for word in ["company", "about us", "us", "organization"]):
            return (
                "We are a leading recruitment platform connecting talented professionals with great opportunities! 🚀\n\n"
                "Our services include:\n"
                "• Job matching and recommendations\n"
                "• Resume analysis and optimization\n"
                "• Career guidance and advice\n"
                "• Direct application assistance\n\n"
                "How can I help you today?"
            )
        
        # Greetings
        elif any(word in text_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            return (
                "Hello! 👋 Welcome to our recruitment bot!\n\n"
                "I can help you with:\n"
                "• Finding job opportunities\n"
                "• Resume analysis\n"
                "• Career advice\n"
                "• Application guidance\n\n"
                "Type /help for more options or start by telling me what you're looking for!"
            )
        
        # Thank you responses
        elif any(word in text_lower for word in ["thank", "thanks"]):
            return (
                "You're very welcome! 😊\n\n"
                "If you need any more help with:\n"
                "• Job search\n"
                "• Resume review\n"
                "• Career advice\n\n"
                "Just let me know! I'm here to help."
            )
        
        # Default response
        else:
            return (
                "Thank you for your message! 📩\n\n"
                "I understand you're looking for assistance. Let me help you:\n\n"
                "Please tell me:\n"
                "• Are you looking for job opportunities?\n"
                "• Do you need help with your resume?\n"
                "• Would you like career advice?\n"
                "• Something else?\n\n"
                "I'll provide the best assistance based on your needs!"
            )
    
    async def _send_welcome_message(self, chat_id: int, username: Optional[str]) -> TelegramResponse:
        """Send welcome message to new user"""
        welcome_text = (
            f"Welcome to our recruitment bot, {username or 'there'}! 🎉\n\n"
            "I'm here to help you with your job search. Here's what I can do:\n\n"
            "📋 *Job Search*: Find matching positions\n"
            "📄 *Resume Analysis*: Upload and get feedback\n"
            "💡 *Career Advice*: Get guidance\n"
            "🚀 *Application Help*: Direct assistance\n\n"
            "Type /help to see all options or start by telling me what you're looking for!"
        )
        return await self._send_message(chat_id, welcome_text)
    
    async def _send_help_message(self, chat_id: int) -> TelegramResponse:
        """Send help message"""
        help_text = (
            "Here are the commands I understand:\n\n"
            "/start - Start conversation\n"
            "/help - Show this help\n"
            "/high - Special response\n\n"
            "You can also:\n"
            "• Upload your resume (PDF/DOCX)\n"
            "• Ask about job opportunities\n"
            "• Request career advice\n"
            "• Search for specific positions\n\n"
            "How can I help you today?"
        )
        return await self._send_message(chat_id, help_text)
    
    async def _send_high_response(self, chat_id: int) -> TelegramResponse:
        """Send response to 'high' command"""
        response_text = (
            "Hey there! 🌟 I'm here and ready to help!\n\n"
            "Whether you're looking for:\n"
            "• Exciting job opportunities\n"
            "• Resume improvements\n"
            "• Career guidance\n"
            "• Or just have questions\n\n"
            "I've got you covered! What can I help you with today?"
        )
        return await self._send_message(chat_id, response_text)
    
    async def _send_unknown_command(self, chat_id: int) -> TelegramResponse:
        """Send unknown command response"""
        response_text = (
            "I didn't understand that command. 😅\n\n"
            "Try one of these:\n"
            "/start - Start over\n"
            "/help - Get help\n"
            "/high - Special greeting\n\n"
            "Or just type your question!"
        )
        return await self._send_message(chat_id, response_text)
    
    async def _send_rate_limit_message(self, chat_id: int) -> TelegramResponse:
        """Send rate limit warning"""
        response_text = (
            "Whoa there! 🛑 You're sending messages too quickly.\n\n"
            "Please wait a moment before sending another message.\n"
            "This helps ensure everyone gets timely responses!"
        )
        return await self._send_message(chat_id, response_text)
    
    async def _send_error_message(self, chat_id: int) -> TelegramResponse:
        """Send error message to user"""
        response_text = (
            "Oops! Something went wrong on my end. 😓\n\n"
            "Don't worry, our team has been notified.\n"
            "Please try again in a moment, or type /help for assistance."
        )
        return await self._send_message(chat_id, response_text)
    
    async def _send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown", **kwargs) -> TelegramResponse:
        """Send message via Telegram Bot API"""
        try:
            if not TelegramSecurityManager.validate_chat_id(chat_id):
                return TelegramResponse(success=False, error_message="Invalid chat ID")
            
            # Rate limiting for outgoing messages
            if not self.rate_limiter.is_allowed(f"outgoing:{chat_id}"):
                logger.warning(f"Rate limit exceeded for outgoing messages to chat {chat_id}")
                return TelegramResponse(success=False, error_message="Rate limit exceeded")
            
            if telegram_settings.TELEGRAM_MOCK_MODE:
                # Mock mode - just log the message
                logger.info(f"[MOCK] Would send to {chat_id}: {text}")
                return TelegramResponse(success=True, message_id=12345)
            
            # Real API call
            url = f"{telegram_settings.get_api_base_url()}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": False
            }
            
            if kwargs.get("reply_markup"):
                payload["reply_markup"] = kwargs.get("reply_markup")
            
            response = await self.session.post(
                url,
                json=payload,
                headers=telegram_settings.get_bot_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    return TelegramResponse(
                        success=True,
                        message_id=data.get("result", {}).get("message_id")
                    )
                else:
                    return TelegramResponse(
                        success=False,
                        error_message=data.get("description", "Unknown error")
                    )
            else:
                return TelegramResponse(
                    success=False,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return TelegramResponse(success=False, error_message=str(e))
    
    async def set_webhook(self, webhook_url: Optional[str] = None) -> Dict[str, Any]:
        """Set Telegram bot webhook"""
        try:
            if telegram_settings.TELEGRAM_MOCK_MODE:
                logger.info(f"[MOCK] Would set webhook to: {webhook_url or telegram_settings.TELEGRAM_WEBHOOK_URL}")
                return {"status": "success", "webhook_url": webhook_url or telegram_settings.TELEGRAM_WEBHOOK_URL}
            
            url = f"{telegram_settings.get_api_base_url()}/setWebhook"
            payload = {
                "url": webhook_url or telegram_settings.TELEGRAM_WEBHOOK_URL,
                "secret_token": telegram_settings.TELEGRAM_WEBHOOK_SECRET,
                "allowed_updates": ["message", "edited_message"]
            }
            
            response = await self.session.post(
                url,
                json=payload,
                headers=telegram_settings.get_bot_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success" if data.get("ok") else "error",
                    "result": data
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_webhook_info(self) -> Dict[str, Any]:
        """Get Telegram bot webhook information"""
        try:
            if telegram_settings.TELEGRAM_MOCK_MODE:
                return {
                    "status": "success",
                    "webhook_url": telegram_settings.TELEGRAM_WEBHOOK_URL,
                    "has_custom_certificate": False,
                    "pending_update_count": 0,
                    "max_connections": 40
                }
            
            url = f"{telegram_settings.get_api_base_url()}/getWebhookInfo"
            response = await self.session.get(
                url,
                headers=telegram_settings.get_bot_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success" if data.get("ok") else "error",
                    "result": data
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error getting webhook info: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_bot_info(self) -> Dict[str, Any]:
        """Get Telegram bot information"""
        try:
            if telegram_settings.TELEGRAM_MOCK_MODE:
                return {
                    "status": "success",
                    "username": "RecruitmentBot",
                    "first_name": "Recruitment",
                    "is_bot": True
                }
            
            url = f"{telegram_settings.get_api_base_url()}/getMe"
            response = await self.session.get(
                url,
                headers=telegram_settings.get_bot_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    bot_info = data.get("result", {})
                    return {
                        "status": "success",
                        "username": bot_info.get("username"),
                        "first_name": bot_info.get("first_name"),
                        "is_bot": bot_info.get("is_bot")
                    }
                else:
                    return {"status": "error", "error": data.get("description")}
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the Telegram bot service"""
        return {
            "initialized": self._initialized,
            "config_valid": len(telegram_settings.validate_configuration()) == 0,
            "mock_mode": telegram_settings.TELEGRAM_MOCK_MODE,
            "rate_limiter_stats": {
                "active_users": len(self.rate_limiter.requests),
                "max_requests": telegram_settings.TELEGRAM_RATE_LIMIT_REQUESTS,
                "window_seconds": telegram_settings.TELEGRAM_RATE_LIMIT_WINDOW
            },
            "settings": {
                "bot_token_set": bool(telegram_settings.TELEGRAM_BOT_TOKEN),
                "webhook_url_set": bool(telegram_settings.TELEGRAM_WEBHOOK_URL),
                "webhook_secret_set": bool(telegram_settings.TELEGRAM_WEBHOOK_SECRET)
            }
        }


    async def _handle_callback_query(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Telegram callback queries (button clicks)"""
        try:
            query_id = callback_data.get("id")
            user_id = callback_data.get("from", {}).get("id")
            data = callback_data.get("data")
            message = callback_data.get("message", {})
            chat_id = message.get("chat", {}).get("id")

            logger.info(f"Processing callback: {data} from user {user_id}")

            # 1. Answer the callback query (stop spinner)
            url = f"{telegram_settings.get_api_base_url()}/answerCallbackQuery"
            await self.session.post(url, json={"callback_query_id": query_id})
            
            # 2. Integrate with Chatbot Engine
            # Lazy load Engine to avoid circular imports / init issues
            if not hasattr(self, "chatbot_engine"):
                 # Initialize Engine (Need to solve Dependency Injection properly)
                 # For now, we assume the global registry has what we need
                 from backend_app.chatbot.skill_registry import get_sid_service
                 from backend_app.chatbot.engine.flow_manager import FlowManager
                 from backend_app.chatbot.engine.chatbot_engine import ChatbotEngine
                 
                 # Initialize FlowManager
                 flow_path = "Backend/backend_app/chatbot/engine/candidate_flow.json"
                 flow_manager = FlowManager(flow_path)
                 
                 # Get Session Service (SID Service)
                 session_service = get_sid_service()
                 
                 self.chatbot_engine = ChatbotEngine(flow_manager, session_service)

            # 3. Process with Engine
            sid = f"telegram:{chat_id}"
            response_messages = await self.chatbot_engine.process_message(
                user_id=str(user_id),
                input_payload=data,
                platform="telegram"
            )

            # 4. Send Responses
            success = True
            for resp in response_messages:
                reply_markup = None
                if resp.buttons:
                    # Convert buttons to InlineKeyboardMarkup
                    inline_keyboard = [
                        [{"text": btn.text, "callback_data": btn.payload}] 
                        for btn in resp.buttons
                    ]
                    reply_markup = {"inline_keyboard": inline_keyboard}

                result = await self._send_message(
                    chat_id=chat_id,
                    text=resp.text,
                    reply_markup=reply_markup
                )
                success = success and result.success

            return {"status": "processed", "success": success}

        except Exception as e:
            logger.error(f"Error handling callback query: {e}")
            return {"status": "error", "error": str(e)}


# Global Telegram bot service instance
telegram_bot_service = TelegramBotService()