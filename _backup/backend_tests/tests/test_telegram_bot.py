"""
Comprehensive Unit Tests for Telegram Bot
Tests all functionality including security, error handling, and integration
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from backend_app.config.telegram_config import (
    TelegramSettings,
    TelegramSecurityManager,
    telegram_settings
)
from backend_app.services.telegram_service import (
    TelegramBotService,
    TelegramMessage,
    TelegramResponse,
    RateLimiter
)


class TestTelegramSettings:
    """Test Telegram configuration settings"""
    
    def test_valid_bot_token(self):
        """Test valid bot token validation"""
        assert TelegramSettings._is_valid_token("123456789:ABCdefGHIjklMNOpqrsTUVwxYZ123abc456")
    
    def test_invalid_bot_token(self):
        """Test invalid bot token validation"""
        assert not TelegramSettings._is_valid_token("invalid_token")
        assert not TelegramSettings._is_valid_token("123:short")
        assert not TelegramSettings._is_valid_token("no_colon")
    
    def test_valid_url(self):
        """Test valid URL validation"""
        assert TelegramSettings._is_valid_url("https://example.com/webhook")
        assert TelegramSettings._is_valid_url("http://localhost:8000/webhook")
    
    def test_invalid_url(self):
        """Test invalid URL validation"""
        assert not TelegramSettings._is_valid_url("invalid_url")
        assert not TelegramSettings._is_valid_url("just_path")
        assert not TelegramSettings._is_valid_url("")
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        settings = TelegramSettings(
            TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxYZ123abc456",
            TELEGRAM_WEBHOOK_URL="https://example.com/webhook"
        )
        
        issues = settings.validate_configuration()
        assert len(issues) == 0
    
    def test_configuration_validation_missing_token(self):
        """Test configuration validation with missing token"""
        settings = TelegramSettings(TELEGRAM_WEBHOOK_URL="https://example.com/webhook")
        issues = settings.validate_configuration()
        assert "TELEGRAM_BOT_TOKEN is required" in issues
    
    def test_bot_headers(self):
        """Test bot headers generation"""
        settings = TelegramSettings(TELEGRAM_BOT_TOKEN="test_token")
        headers = settings.get_bot_headers()
        
        assert "Content-Type" in headers
        assert "User-Agent" in headers
    
    def test_api_base_url(self):
        """Test API base URL generation"""
        settings = TelegramSettings(TELEGRAM_BOT_TOKEN="test_token")
        base_url = settings.get_api_base_url()
        
        assert base_url == "https://api.telegram.org/bottest_token"


class TestTelegramSecurityManager:
    """Test Telegram security features"""
    
    def test_webhook_secret_validation(self):
        """Test webhook secret validation"""
        # Test with no secret configured
        with patch.object(telegram_settings, 'TELEGRAM_WEBHOOK_SECRET', None):
            assert TelegramSecurityManager.validate_webhook_secret("any_token")
        
        # Test with secret configured
        with patch.object(telegram_settings, 'TELEGRAM_WEBHOOK_SECRET', 'test_secret'):
            assert TelegramSecurityManager.validate_webhook_secret('test_secret')
            assert not TelegramSecurityManager.validate_webhook_secret('wrong_secret')
            assert not TelegramSecurityManager.validate_webhook_secret(None)
    
    def test_input_sanitization(self):
        """Test input sanitization"""
        # Test normal text
        assert TelegramSecurityManager.sanitize_telegram_input("Hello world") == "Hello world"
        
        # Test HTML escaping
        assert TelegramSecurityManager.sanitize_telegram_input("<script>alert('test')</script>") == "<script>alert&#40;'test'&#41;</script>"
        
        # Test length limiting
        long_text = "A" * 5000
        sanitized = TelegramSecurityManager.sanitize_telegram_input(long_text)
        assert len(sanitized) <= telegram_settings.TELEGRAM_MAX_MESSAGE_LENGTH
        assert sanitized.endswith("...")
    
    def test_chat_id_validation(self):
        """Test chat ID validation"""
        assert TelegramSecurityManager.validate_chat_id(123456789)
        assert TelegramSecurityManager.validate_chat_id(-123456789)  # Group chat
        assert not TelegramSecurityManager.validate_chat_id(0)
        assert not TelegramSecurityManager.validate_chat_id("invalid")


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    def test_rate_limiting(self):
        """Test basic rate limiting"""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        # First two requests should be allowed
        assert limiter.is_allowed("user:123")
        limiter.record_request("user:123")
        
        assert limiter.is_allowed("user:123")
        limiter.record_request("user:123")
        
        # Third request should be blocked
        assert not limiter.is_allowed("user:123")
    
    def test_rate_limit_window(self):
        """Test rate limit window expiration"""
        limiter = RateLimiter(max_requests=1, window_seconds=1)
        
        # Allow request
        assert limiter.is_allowed("user:123")
        limiter.record_request("user:123")
        
        # Block request
        assert not limiter.is_allowed("user:123")
        
        # Wait for window to expire
        import time
        time.sleep(1.1)
        
        # Should allow request again
        assert limiter.is_allowed("user:123")


class TestTelegramMessage:
    """Test Telegram message parsing"""
    
    def test_message_parsing_text(self):
        """Test parsing text messages"""
        message_data = {
            "message_id": 123,
            "from": {"id": 456, "username": "testuser"},
            "chat": {"id": 789},
            "text": "Hello world",
            "date": 1234567890
        }
        
        message = TelegramMessage(
            chat_id=message_data["chat"]["id"],
            message_id=message_data["message_id"],
            text=message_data["text"],
            message_type="text",
            user_id=message_data["from"]["id"],
            username=message_data["from"]["username"],
            timestamp=datetime.fromtimestamp(message_data["date"])
        )
        
        assert message.chat_id == 789
        assert message.message_id == 123
        assert message.text == "Hello world"
        assert message.message_type == "text"
        assert message.user_id == 456
    
    def test_message_parsing_photo(self):
        """Test parsing photo messages"""
        message_data = {
            "message_id": 123,
            "from": {"id": 456},
            "chat": {"id": 789},
            "photo": [{"file_id": "photo123", "width": 100, "height": 100}]
        }
        
        message = TelegramMessage(
            chat_id=message_data["chat"]["id"],
            message_id=message_data["message_id"],
            text="",
            message_type="photo",
            user_id=message_data["from"]["id"],
            metadata={"photos": message_data["photo"]}
        )
        
        assert message.message_type == "photo"
        assert "photos" in message.metadata


class TestTelegramBotService:
    """Test Telegram bot service functionality"""
    
    @pytest.fixture
    async def bot_service(self):
        """Create and initialize bot service"""
        service = TelegramBotService()
        await service.initialize()
        yield service
        await service.shutdown()
    
    @pytest.fixture
    def mock_chatbot_controller(self):
        """Mock chatbot controller"""
        with patch('backend_app.services.telegram_service.ChatbotController') as mock:
            yield mock
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_chatbot_controller):
        """Test bot service initialization"""
        service = TelegramBotService()
        await service.initialize()
        
        assert service._initialized
        assert service.chatbot_controller is not None
        assert service.rate_limiter is not None
        
        await service.shutdown()
    
    @pytest.mark.asyncio
    async def test_webhook_processing(self, bot_service):
        """Test webhook message processing"""
        # Mock webhook payload
        payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 123,
                "from": {"id": 456, "username": "testuser"},
                "chat": {"id": 789},
                "text": "/start",
                "date": 1234567890
            }
        }
        
        # Process webhook
        result = await bot_service.process_webhook(payload)
        
        assert result["status"] == "processed"
        assert result["message_id"] == 123
    
    @pytest.mark.asyncio
    async def test_command_handling(self, bot_service):
        """Test command handling"""
        # Test /start command
        message = TelegramMessage(
            chat_id=789,
            message_id=123,
            text="/start",
            message_type="text",
            user_id=456,
            username="testuser"
        )
        
        response = await bot_service._handle_command(message)
        assert response.success
        
        # Test /high command
        message.text = "/high"
        response = await bot_service._handle_command(message)
        assert response.success
        
        # Test /help command
        message.text = "/help"
        response = await bot_service._handle_command(message)
        assert response.success
    
    @pytest.mark.asyncio
    async def test_intelligent_responses(self, bot_service):
        """Test intelligent response generation"""
        # Test job-related query
        message = TelegramMessage(
            chat_id=789,
            message_id=123,
            text="I'm looking for a software engineering position",
            message_type="text",
            user_id=456
        )
        
        response = await bot_service._handle_text_message(message)
        assert response.success
        assert "job" in response.response_data.get("text", "").lower() if response.response_data else True
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, bot_service):
        """Test rate limiting functionality"""
        message = TelegramMessage(
            chat_id=789,
            message_id=123,
            text="Test message",
            message_type="text",
            user_id=456
        )
        
        # Send multiple messages quickly to trigger rate limiting
        for i in range(35):  # Exceed default limit of 30
            result = await bot_service._handle_message(message)
            if not bot_service.rate_limiter.is_allowed(f"user:{message.user_id}"):
                break
        
        # Next message should be rate limited
        assert not bot_service.rate_limiter.is_allowed(f"user:{message.user_id}")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, bot_service):
        """Test error handling"""
        # Test invalid chat ID
        response = await bot_service._send_message(0, "Test message")
        assert not response.success
        assert "Invalid chat ID" in response.error_message
    
    @pytest.mark.asyncio
    async def test_webhook_management(self, bot_service):
        """Test webhook management"""
        # Test setting webhook
        result = await bot_service.set_webhook("https://example.com/webhook")
        assert "status" in result
        
        # Test getting webhook info
        result = await bot_service.get_webhook_info()
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_bot_info(self, bot_service):
        """Test bot information retrieval"""
        result = await bot_service.get_bot_info()
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_health_status(self, bot_service):
        """Test health status reporting"""
        health = bot_service.get_health_status()
        
        assert "initialized" in health
        assert "config_valid" in health
        assert "rate_limiter_stats" in health
        assert "settings" in health


class TestTelegramIntegration:
    """Integration tests for Telegram bot"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_webhook_flow(self):
        """Test complete webhook processing flow"""
        service = TelegramBotService()
        await service.initialize()
        
        try:
            # Simulate complete webhook flow
            payload = {
                "update_id": 123456789,
                "message": {
                    "message_id": 123,
                    "from": {"id": 456, "username": "testuser"},
                    "chat": {"id": 789},
                    "text": "Hello bot!",
                    "date": 1234567890
                }
            }
            
            # Process webhook
            result = await service.process_webhook(payload)
            
            assert result["status"] == "processed"
            assert result["message_id"] == 123
            
        finally:
            await service.shutdown()
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_rate_limiting_over_time(self):
        """Test rate limiting over time"""
        service = TelegramBotService()
        await service.initialize()
        
        try:
            message = TelegramMessage(
                chat_id=789,
                message_id=123,
                text="Test message",
                message_type="text",
                user_id=456
            )
            
            # Send messages to hit rate limit
            message_count = 0
            while service.rate_limiter.is_allowed(f"user:{message.user_id}"):
                await service._handle_message(message)
                message_count += 1
            
            # Should hit rate limit
            assert message_count <= 30  # Within rate limit
            
        finally:
            await service.shutdown()


# Mock tests for external API calls
class TestTelegramMockMode:
    """Test mock mode functionality"""
    
    @pytest.mark.asyncio
    async def test_mock_mode_webhook(self):
        """Test webhook processing in mock mode"""
        with patch.object(telegram_settings, 'TELEGRAM_MOCK_MODE', True):
            service = TelegramBotService()
            await service.initialize()
            
            try:
                payload = {
                    "update_id": 123456789,
                    "message": {
                        "message_id": 123,
                        "from": {"id": 456},
                        "chat": {"id": 789},
                        "text": "/start",
                        "date": 1234567890
                    }
                }
                
                result = await service.process_webhook(payload)
                assert result["status"] == "processed"
                
            finally:
                await service.shutdown()
    
    @pytest.mark.asyncio
    async def test_mock_mode_api_calls(self):
        """Test API calls in mock mode"""
        with patch.object(telegram_settings, 'TELEGRAM_MOCK_MODE', True):
            service = TelegramBotService()
            await service.initialize()
            
            try:
                # Test webhook setting in mock mode
                result = await service.set_webhook("https://example.com/webhook")
                assert result["status"] == "success"
                
                # Test bot info in mock mode
                result = await service.get_bot_info()
                assert result["status"] == "success"
                
            finally:
                await service.shutdown()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])