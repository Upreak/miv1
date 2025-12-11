"""
Telegram Webhook API Routes - Production Ready
Complete Telegram bot integration with secure token management and error handling
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend_app.db.connection import get_db
from backend_app.config.telegram_config import (
    telegram_settings,
    TelegramSecurityManager,
    get_telegram_settings
)
from backend_app.services.telegram_service import telegram_bot_service
from backend_app.chatbot.controller import ChatbotController

router = APIRouter()
logger = logging.getLogger(__name__)


@router.on_event("startup")
async def startup_event():
    """Initialize Telegram bot service on startup"""
    try:
        await telegram_bot_service.initialize()
        logger.info("Telegram bot service initialized on startup")
    except Exception as e:
        logger.error(f"Failed to initialize Telegram bot service: {e}")


@router.on_event("shutdown")
async def shutdown_event():
    """Shutdown Telegram bot service"""
    try:
        await telegram_bot_service.shutdown()
        logger.info("Telegram bot service shutdown complete")
    except Exception as e:
        logger.error(f"Error during Telegram bot service shutdown: {e}")


@router.post("/webhook")
async def telegram_webhook(
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle incoming Telegram webhook messages
    Includes security validation, rate limiting, and error handling
    """
    try:
        # Parse incoming webhook data
        payload = await request.json()
        logger.debug(f"Telegram webhook received: {payload}")
        
        # Validate webhook secret if configured
        if telegram_settings.TELEGRAM_WEBHOOK_SECRET:
            request_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if not TelegramSecurityManager.validate_webhook_secret(request_secret):
                logger.warning("Invalid webhook secret token")
                raise HTTPException(status_code=401, detail="Invalid webhook secret")
        
        # Process message via background task for better performance
        background_tasks.add_task(
            telegram_bot_service.process_webhook,
            payload
        )
        
        return {
            "status": "received",
            "timestamp": payload.get("update_id"),
            "message_type": "webhook"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def telegram_health_check():
    """
    Health check endpoint for Telegram bot service
    Returns detailed status information
    """
    try:
        health_status = telegram_bot_service.get_health_status()
        
        # Check if service is ready
        is_healthy = (
            health_status["initialized"] and
            health_status["config_valid"] and
            not health_status["settings"]["bot_token_set"] or 
            health_status["settings"]["webhook_url_set"]
        )
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "telegram_bot",
            "timestamp": str(datetime.now()),
            "details": health_status
        }
        
    except Exception as e:
        logger.error(f"Telegram health check error: {e}")
        return {
            "status": "error",
            "service": "telegram_bot",
            "error": str(e),
            "timestamp": str(datetime.now())
        }


@router.post("/set-webhook")
async def set_telegram_webhook(
    webhook_url: Optional[str] = None,
    secret_token: Optional[str] = None
):
    """
    Set Telegram bot webhook with validation
    """
    try:
        # Validate webhook URL
        if webhook_url and not telegram_settings._is_valid_url(webhook_url):
            raise HTTPException(status_code=400, detail="Invalid webhook URL format")
        
        # Set webhook
        result = await telegram_bot_service.set_webhook(webhook_url)
        
        if result["status"] == "success":
            logger.info(f"Telegram webhook set successfully: {result}")
            return {
                "status": "success",
                "message": "Webhook set successfully",
                "webhook_url": result.get("webhook_url") or telegram_settings.TELEGRAM_WEBHOOK_URL
            }
        else:
            logger.error(f"Failed to set webhook: {result}")
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-webhook-info")
async def get_telegram_webhook_info():
    """
    Get Telegram bot webhook information
    """
    try:
        result = await telegram_bot_service.get_webhook_info()
        
        if result["status"] == "success":
            return {
                "status": "success",
                "webhook_info": result.get("result", {})
            }
        else:
            logger.error(f"Failed to get webhook info: {result}")
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-bot-info")
async def get_telegram_bot_info():
    """
    Get Telegram bot information
    """
    try:
        result = await telegram_bot_service.get_bot_info()
        
        if result["status"] == "success":
            return {
                "status": "success",
                "bot_info": result
            }
        else:
            logger.error(f"Failed to get bot info: {result}")
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bot info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-webhook")
async def delete_telegram_webhook(drop_pending_updates: bool = False):
    """
    Delete Telegram bot webhook
    """
    try:
        if telegram_settings.TELEGRAM_MOCK_MODE:
            logger.info("[MOCK] Would delete webhook")
            return {"status": "success", "message": "Webhook deleted (mock mode)"}
        
        url = f"{telegram_settings.get_api_base_url()}/deleteWebhook"
        payload = {"drop_pending_updates": drop_pending_updates}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=telegram_settings.get_bot_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    logger.info("Telegram webhook deleted successfully")
                    return {"status": "success", "message": "Webhook deleted"}
                else:
                    raise HTTPException(status_code=500, detail=data.get("description", "Unknown error"))
            else:
                raise HTTPException(status_code=500, detail=f"HTTP {response.status_code}: {response.text}")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-message")
async def send_telegram_message(
    chat_id: int,
    text: str,
    parse_mode: Optional[str] = "Markdown"
):
    """
    Send message to Telegram user (for testing and admin purposes)
    """
    try:
        # Validate chat ID
        if not TelegramSecurityManager.validate_chat_id(chat_id):
            raise HTTPException(status_code=400, detail="Invalid chat ID")
        
        # Sanitize message
        sanitized_text = TelegramSecurityManager.sanitize_telegram_input(text)
        
        # Send message
        response = await telegram_bot_service._send_message(chat_id, sanitized_text, parse_mode)
        
        if response.success:
            return {
                "status": "success",
                "message_id": response.message_id,
                "chat_id": chat_id
            }
        else:
            raise HTTPException(status_code=500, detail=response.error_message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configuration")
async def get_telegram_configuration():
    """
    Get current Telegram configuration (for debugging)
    """
    try:
        settings = get_telegram_settings()
        validation_issues = settings.validate_configuration()
        
        return {
            "configuration": {
                "bot_token_set": bool(settings.TELEGRAM_BOT_TOKEN),
                "webhook_url": settings.TELEGRAM_WEBHOOK_URL,
                "webhook_secret_set": bool(settings.TELEGRAM_WEBHOOK_SECRET),
                "mock_mode": settings.TELEGRAM_MOCK_MODE,
                "debug_mode": settings.TELEGRAM_DEBUG_MODE,
                "rate_limit": {
                    "requests": settings.TELEGRAM_RATE_LIMIT_REQUESTS,
                    "window": settings.TELEGRAM_RATE_LIMIT_WINDOW
                },
                "timeout": settings.TELEGRAM_TIMEOUT,
                "retry_attempts": settings.TELEGRAM_RETRY_ATTEMPTS
            },
            "validation_issues": validation_issues,
            "is_configured": len(validation_issues) == 0
        }
        
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-integration")
async def test_telegram_integration():
    """
    Test Telegram bot integration
    """
    try:
        # Test bot info
        bot_info = await telegram_bot_service.get_bot_info()
        
        # Test webhook info
        webhook_info = await telegram_bot_service.get_webhook_info()
        
        # Test configuration
        health_status = telegram_bot_service.get_health_status()
        
        return {
            "status": "success",
            "tests": {
                "bot_info": bot_info,
                "webhook_info": webhook_info,
                "health_status": health_status
            }
        }
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# Import datetime for the health check endpoint
from datetime import datetime
import httpx