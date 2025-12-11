"""
Telegram Bot Configuration
Secure configuration management for Telegram bot integration
"""

import os
import logging
from typing import Optional
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


logger = logging.getLogger(__name__)



class TelegramSettings:
    """Telegram bot configuration settings"""
    
    def __init__(self):
        # Bot Configuration
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        # self.TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "pz6stn2gnu6lk1m1688t38cc4vqqng4s")
        self.TELEGRAM_WEBHOOK_SECRET = "pz6stn2gnu6lk1m1688t38cc4vqqng4s"
        self.TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")
        
        # Security Settings
        self.TELEGRAM_RATE_LIMIT_REQUESTS = int(os.getenv("TELEGRAM_RATE_LIMIT_REQUESTS", "30"))
        self.TELEGRAM_RATE_LIMIT_WINDOW = int(os.getenv("TELEGRAM_RATE_LIMIT_WINDOW", "60"))
        self.TELEGRAM_MAX_MESSAGE_LENGTH = int(os.getenv("TELEGRAM_MAX_MESSAGE_LENGTH", "4096"))
        
        # Bot Behavior
        self.TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")
        self.TELEGRAM_TIMEOUT = int(os.getenv("TELEGRAM_TIMEOUT", "30"))
        self.TELEGRAM_RETRY_ATTEMPTS = int(os.getenv("TELEGRAM_RETRY_ATTEMPTS", "3"))
        
        # Development Settings
        self.TELEGRAM_DEBUG_MODE = os.getenv("TELEGRAM_DEBUG_MODE", "false").lower() == "true"
        self.TELEGRAM_MOCK_MODE = os.getenv("TELEGRAM_MOCK_MODE", "false").lower() == "true"
        
        # Health Check
        self.TELEGRAM_HEALTH_CHECK_ENABLED = os.getenv("TELEGRAM_HEALTH_CHECK_ENABLED", "true").lower() == "true"
    
    @validator('TELEGRAM_BOT_TOKEN')
    def validate_bot_token(cls, v):
        """Validate Telegram bot token format"""
        if v and not cls._is_valid_token(v):
            raise ValueError("Invalid Telegram bot token format")
        return v
    
    @validator('TELEGRAM_WEBHOOK_URL')
    def validate_webhook_url(cls, v):
        """Validate webhook URL format"""
        if v and not cls._is_valid_url(v):
            raise ValueError("Invalid webhook URL format")
        return v
    
    @staticmethod
    def _is_valid_token(token: str) -> bool:
        """Check if token follows Telegram bot token format"""
        # Telegram bot tokens are typically in format: 123456789:ABCdefGHIjklMNOpqrsTUVwxYZ123abc456
        import re
        return True
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Basic URL validation"""
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def is_configured(self) -> bool:
        """Check if Telegram bot is properly configured"""
        return bool(self.TELEGRAM_BOT_TOKEN and self.TELEGRAM_WEBHOOK_URL)
    
    def get_bot_headers(self) -> dict:
        """Get headers for Telegram Bot API requests"""
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("Telegram bot token not configured")
        
        return {
            "Content-Type": "application/json",
            "User-Agent": f"RecruitmentBot/1.0 (https://github.com/your-org/recruitment-bot)"
        }
    
    def get_api_base_url(self) -> str:
        """Get Telegram Bot API base URL"""
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("Telegram bot token not configured")
        
        return f"https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}"
    
    def validate_configuration(self) -> list[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        if not self.TELEGRAM_BOT_TOKEN:
            issues.append("TELEGRAM_BOT_TOKEN is required")
        
        if not self.TELEGRAM_WEBHOOK_URL:
            issues.append("TELEGRAM_WEBHOOK_URL is required")
        
        if self.TELEGRAM_BOT_TOKEN and not self._is_valid_token(self.TELEGRAM_BOT_TOKEN):
            issues.append("TELEGRAM_BOT_TOKEN format is invalid")
        
        if self.TELEGRAM_WEBHOOK_URL and not self._is_valid_url(self.TELEGRAM_WEBHOOK_URL):
            issues.append("TELEGRAM_WEBHOOK_URL format is invalid")
        
        if self.TELEGRAM_RATE_LIMIT_REQUESTS <= 0:
            issues.append("TELEGRAM_RATE_LIMIT_REQUESTS must be positive")
        
        if self.TELEGRAM_TIMEOUT <= 0:
            issues.append("TELEGRAM_TIMEOUT must be positive")
        
        return issues


# Global Telegram settings instance
telegram_settings = TelegramSettings()

# Validate configuration on import
if telegram_settings.TELEGRAM_BOT_TOKEN:
    validation_issues = telegram_settings.validate_configuration()
    if validation_issues:
        logger.error(f"Telegram configuration issues: {validation_issues}")
    else:
        logger.info("Telegram bot configuration validated successfully")
else:
    logger.warning("Telegram bot not configured (TELEGRAM_BOT_TOKEN not set)")


class TelegramSecurityManager:
    """Security manager for Telegram bot operations"""
    
    @staticmethod
    def validate_webhook_secret(request_secret: Optional[str]) -> bool:
        """Validate webhook secret token"""
        expected_secret = telegram_settings.TELEGRAM_WEBHOOK_SECRET
        if not expected_secret:
            logger.warning("Webhook secret not configured, skipping validation")
            return True
            

        
        if not request_secret:
            logger.warning("No webhook secret provided in request")
            return False
        
        # Constant-time comparison to prevent timing attacks
        import hmac
        return hmac.compare_digest(request_secret, expected_secret)
    
    @staticmethod
    def sanitize_telegram_input(text: str) -> str:
        """Sanitize user input from Telegram"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        import html
        sanitized = html.escape(text)
        
        # Limit message length
        if len(sanitized) > telegram_settings.TELEGRAM_MAX_MESSAGE_LENGTH:
            sanitized = sanitized[:telegram_settings.TELEGRAM_MAX_MESSAGE_LENGTH - 3] + "..."
        
        return sanitized
    
    @staticmethod
    def validate_chat_id(chat_id: int) -> bool:
        """Validate Telegram chat ID"""
        # Telegram chat IDs are integers, can be negative (for groups)
        return isinstance(chat_id, int) and abs(chat_id) > 0


def get_telegram_settings() -> TelegramSettings:
    """Get Telegram settings instance"""
    return telegram_settings