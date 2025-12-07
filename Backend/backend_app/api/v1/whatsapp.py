"""
WhatsApp Webhook API Routes
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from typing import Dict, Any, Optional
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/webhooks/whatsapp")
async def whatsapp_verify(request: Request):
    """Verify WhatsApp webhook"""
    try:
        # Get verification parameters
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        # Verify token (this should match your WhatsApp Business API settings)
        if mode == "subscribe" and token == "your_verify_token_here":
            return challenge
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
    except Exception as e:
        logger.error(f"WhatsApp verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(
    background_tasks: BackgroundTasks,
    request: Request
):
    """Handle incoming WhatsApp messages"""
    try:
        # Parse incoming webhook data
        payload = await request.json()
        logger.info(f"WhatsApp webhook received: {payload}")
        
        # Process messages
        if "entry" in payload:
            for entry in payload["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if change.get("field") == "messages":
                            message_data = change.get("value", {})
                            await process_whatsapp_message(message_data, background_tasks)
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_whatsapp_message(message_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Process individual WhatsApp message"""
    try:
        # Extract message details
        messages = message_data.get("messages", [])
        if not messages:
            return
        
        message = messages[0]
        from_number = message.get("from")  # WhatsApp user number
        message_type = message.get("type", "text")
        message_id = message.get("id")
        
        # Handle different message types
        if message_type == "text":
            text_content = message.get("text", {}).get("body", "")
            await handle_whatsapp_text_message(from_number, text_content, message_id, background_tasks)
        elif message_type == "image":
            await handle_whatsapp_media_message(from_number, message_type, message, background_tasks)
        elif message_type == "document":
            await handle_whatsapp_media_message(from_number, message_type, message, background_tasks)
        # Add more message types as needed
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {e}")


async def handle_whatsapp_text_message(
    from_number: str, 
    text_content: str, 
    message_id: str, 
    background_tasks: BackgroundTasks
):
    """Handle text messages from WhatsApp"""
    try:
        # This would integrate with your chatbot system
        # For now, just log the message
        logger.info(f"WhatsApp text message from {from_number}: {text_content}")
        
        # TODO: Integrate with chatbot controller
        # controller = ChatbotController()
        # response = await controller.process_message(session_id, text_content, "text")
        # await send_whatsapp_message(from_number, response["text"])
        
    except Exception as e:
        logger.error(f"Error handling WhatsApp text message: {e}")


async def handle_whatsapp_media_message(
    from_number: str,
    message_type: str,
    message: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Handle media messages from WhatsApp"""
    try:
        # Extract media information
        media_id = message.get(message_type, {}).get("id")
        media_caption = message.get(message_type, {}).get("caption", "")
        
        logger.info(f"WhatsApp {message_type} message from {from_number}: {media_id}")
        
        # TODO: Download media and process with chatbot
        # This would involve downloading the media file and sending it to your chatbot
        
    except Exception as e:
        logger.error(f"Error handling WhatsApp media message: {e}")


@router.post("/send-message")
async def send_whatsapp_message(
    to: str,
    message: str
):
    """Send message via WhatsApp (placeholder for actual WhatsApp API integration)"""
    try:
        # TODO: Integrate with actual WhatsApp Business API
        logger.info(f"Sending WhatsApp message to {to}: {message}")
        
        # Placeholder response
        return {
            "status": "success",
            "message_id": "placeholder_id",
            "to": to
        }
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        raise HTTPException(status_code=500, detail=str(e))