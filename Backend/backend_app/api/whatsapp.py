from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging
import hmac
import hashlib
import json

from ..db.base import get_db
from ..models.users import User
from ..repositories.user_repo import UserRepository
from ..security.otp_service import OTPService
from ..security.token_manager import TokenManager
from ..shared.schemas import (
    WhatsAppWebhook, WhatsAppMessage,
    SuccessResponse, ErrorResponse
)
from ..file_intake.whatsapp_intake import handle_whatsapp_document, handle_whatsapp_text

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

# WhatsApp webhook verification token (should match your Meta for Developers app)
VERIFY_TOKEN = "your_verify_token_here"

# Initialize services
token_manager = TokenManager()

def verify_whatsapp_signature(request: Request, payload: str) -> bool:
    """Verify webhook signature using HMAC-SHA256"""
    try:
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not signature:
            return False
        
        # Extract signature method and hash
        if not signature.startswith("sha256="):
            return False
        
        received_hash = signature[7:]  # Remove "sha256=" prefix
        
        # Compute expected hash
        expected_hash = hmac.new(
            b"your_webhook_secret",  # Should match your Meta for Developers app secret
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(received_hash, expected_hash)
        
    except Exception as e:
        logger.error(f"Error verifying WhatsApp signature: {str(e)}")
        return False

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str,
    challenge: str,
    hub_verify_token: str,
    request: Request
):
    """
    Verify webhook subscription (Meta for Developers requirement)
    """
    try:
        if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
            logger.info("WhatsApp webhook verified successfully")
            return JSONResponse(content=challenge, status_code=200)
        else:
            logger.warning("Invalid webhook verification attempt")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid verification token"
            )
            
    except Exception as e:
        logger.error(f"Webhook verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/webhook")
async def receive_webhook(
    request: Request,
    payload: str,
    db: Session = Depends(get_db)
):
    """
    Receive and process WhatsApp webhook messages
    """
    try:
        # Verify signature
        if not verify_whatsapp_signature(request, payload):
            logger.warning("Invalid WhatsApp webhook signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
        
        # Parse webhook data
        webhook_data = json.loads(payload)
        
        # Process each entry
        for entry in webhook_data.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "messages":
                    process_message_change(change, db)
        
        logger.info("WhatsApp webhook processed successfully")
        return SuccessResponse(
            message="Webhook processed successfully",
            data={"processed_entries": len(webhook_data.get("entry", []))}
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON payload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def process_message_change(change: Dict[str, Any], db: Session):
    """Process individual message change from webhook"""
    try:
        messages = change.get("value", {}).get("messages", [])
        
        for message in messages:
            if message.get("type") == "text":
                process_text_message(message, db)
            elif message.get("type") == "document":
                # Handle document intake
                result = handle_whatsapp_document(change, db)
                logger.info(f"Document intake result: {result}")
            elif message.get("type") == "interactive":
                process_interactive_message(message, db)
                
    except Exception as e:
        logger.error(f"Error processing message change: {str(e)}")

def process_text_message(message: Dict[str, Any], db: Session):
    """Process text message from WhatsApp"""
    try:
        from_number = message.get("from")
        text_content = message.get("text", {}).get("body", "")
        
        logger.info(f"Received WhatsApp message from {from_number}: {text_content}")
        
        # Check if this is a document upload via text (could be a resume)
        if len(text_content) > 100:  # Assume long text might be resume content
            # Handle as text intake for resume processing
            result = handle_whatsapp_text(message, db)
            logger.info(f"Text intake result: {result}")
        else:
            # Get or create user
            user_repo = UserRepository(db)
            user = user_repo.get_by_whatsapp_or_create(from_number)
            
            # Handle different message types
            text_content = text_content.strip().lower()
            
            if text_content in ["start", "hi", "hello", "hey"]:
                handle_welcome_message(user, db)
            elif text_content.startswith("otp"):
                handle_otp_request(user, text_content, db)
            elif text_content.startswith("verify"):
                handle_verification(user, text_content, db)
            else:
                handle_general_message(user, text_content, db)
            
    except Exception as e:
        logger.error(f"Error processing text message: {str(e)}")

def process_interactive_message(message: Dict[str, Any], db: Session):
    """Process interactive message (buttons, lists) from WhatsApp"""
    try:
        from_number = message.get("from")
        interactive_content = message.get("interactive", {})
        button_text = interactive_content.get("button_reply", {}).get("title", "")
        
        logger.info(f"Received WhatsApp interactive message from {from_number}: {button_text}")
        
        # Get or create user
        user_repo = UserRepository(db)
        user = user_repo.get_by_whatsapp_or_create(from_number)
        
        # Handle button interactions
        if button_text.lower() in ["get otp", "request otp"]:
            handle_otp_request(user, "otp", db)
        elif button_text.lower() in ["verify", "confirm verification"]:
            handle_verification(user, "verify", db)
            
    except Exception as e:
        logger.error(f"Error processing interactive message: {str(e)}")

def handle_welcome_message(user: User, db: Session):
    """Handle welcome message from WhatsApp user"""
    try:
        # Send welcome message
        welcome_text = f"""
👋 Welcome to our service!

I'm here to help you get started. Here's what you can do:

🔢 **Get OTP**: Send "OTP" to receive a verification code
✅ **Verify**: Send "VERIFY" followed by your OTP to verify your account
❓ **Help**: Get help with any questions

How can I assist you today?
        """
        
        # In production, you would send this message back via WhatsApp API
        # For now, just log it
        logger.info(f"Sending welcome message to {user.whatsapp_number}")
        
        # Update user last active
        user_repo = UserRepository(db)
        user_repo.update_last_active(user)
        
    except Exception as e:
        logger.error(f"Error handling welcome message: {str(e)}")

def handle_otp_request(user: User, message: str, db: Session):
    """Handle OTP request from WhatsApp user"""
    try:
        otp_service = OTPService(UserRepository(db))
        
        # Send OTP
        otp_code = otp_service.send_otp(user, send_via_whatsapp=True)
        
        # Send confirmation message
        confirmation_text = f"""
🔢 Your verification code is: *{otp_code}*

This code will expire in 5 minutes.

To verify your account, send:
VERIFY {otp_code}

Need help? Just reply with "HELP"
        """
        
        logger.info(f"Sent OTP to {user.whatsapp_number}")
        
        # Update user last active
        user_repo = UserRepository(db)
        user_repo.update_last_active(user)
        
    except Exception as e:
        logger.error(f"Error handling OTP request: {str(e)}")
        error_text = "❌ Sorry, I couldn't send an OTP. Please try again later."
        # In production, send this error message back

def handle_verification(user: User, message: str, db: Session):
    """Handle verification request from WhatsApp user"""
    try:
        # Extract OTP from message if provided
        if message == "verify":
            verification_text = """
🔐 Please provide your verification code.

Send: VERIFY [your OTP code]

Example: VERIFY 123456
            """
            # In production, send this message back
            logger.info(f"Requested verification code from {user.whatsapp_number}")
        else:
            # Extract OTP from message
            parts = message.split()
            if len(parts) >= 2 and parts[0].lower() == "verify":
                otp_code = parts[1]
                
                # Verify OTP
                otp_service = OTPService(UserRepository(db))
                if otp_service.verify_otp(user, otp_code):
                    # Mark user as verified
                    user_repo = UserRepository(db)
                    user = user_repo.set_verified(user)
                    
                    success_text = f"""
✅ **Account Verified Successfully!**

Your WhatsApp account has been verified and linked to your profile.

You can now:
• Access all features
• Receive notifications
• Use our full service

Welcome aboard! 🎉
                    """
                    
                    logger.info(f"Successfully verified WhatsApp account for {user.whatsapp_number}")
                else:
                    error_text = """
❌ **Invalid Verification Code**

The code you provided is incorrect or has expired.

Please send: VERIFY [your OTP code]

Example: VERIFY 123456
                    """
                    # In production, send this error message back
                    logger.warning(f"Failed verification attempt for {user.whatsapp_number}")
            else:
                error_text = """
❌ **Invalid Format**

Please use the correct format:
VERIFY [your OTP code]

Example: VERIFY 123456
                """
                # In production, send this error message back
        
        # Update user last active
        user_repo = UserRepository(db)
        user_repo.update_last_active(user)
        
    except Exception as e:
        logger.error(f"Error handling verification: {str(e)}")
        error_text = "❌ Sorry, there was an error with verification. Please try again."
        # In production, send this error message back

def handle_general_message(user: User, message: str, db: Session):
    """Handle general message from WhatsApp user"""
    try:
        # Check for help command
        if message.lower() in ["help", "help me", "what can i do"]:
            help_text = """
📚 **Help & Commands**

Here are the available commands:

🔢 **OTP** - Get a verification code
✅ **VERIFY [code]** - Verify your account
👋 **Hi/Hello/Start** - Welcome message
❓ **Help** - Show this help message

Need more help? Contact our support team.
            """
            # In production, send this help message back
            logger.info(f"Sent help message to {user.whatsapp_number}")
        else:
            # Default response
            default_text = """
🤔 I'm not sure what you mean.

Try these commands:
• OTP - Get verification code
• VERIFY [code] - Verify your account
• HELP - Show available commands

Need help? Just reply with "HELP"
            """
            # In production, send this default response back
            logger.info(f"Sent default response to {user.whatsapp_number}")
        
        # Update user last active
        user_repo = UserRepository(db)
        user_repo.update_last_active(user)
        
    except Exception as e:
        logger.error(f"Error handling general message: {str(e)}")