from fastapi import APIRouter, HTTPException, status, Request, Depends
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging
import json

from ..db.base import get_db
from ..models.users import User
from ..repositories.user_repo import UserRepository
from ..security.otp_service import OTPService
from ..security.token_manager import TokenManager
from ..shared.schemas import (
    TelegramUpdate, TelegramMessage,
    SuccessResponse, ErrorResponse
)
from ..file_intake.telegram_intake import handle_telegram_document, handle_telegram_text, handle_telegram_photo

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["Telegram"])

# Initialize services
token_manager = TokenManager()

@router.post("/webhook")
async def receive_telegram_webhook(
    request: Request,
    payload: str,
    db: Session = Depends(get_db)
):
    """
    Receive and process Telegram webhook updates
    """
    try:
        # Parse webhook data
        update_data = json.loads(payload)
        
        logger.info(f"Received Telegram webhook: {json.dumps(update_data, indent=2)}")
        
        # Process the update
        process_telegram_update(update_data, db)
        
        logger.info("Telegram webhook processed successfully")
        return SuccessResponse(
            message="Webhook processed successfully",
            data={"update_id": update_data.get("update_id")}
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON payload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        logger.error(f"Telegram webhook processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def process_telegram_update(update_data: Dict[str, Any], db: Session):
    """Process individual Telegram update"""
    try:
        update_id = update_data.get("update_id")
        
        # Handle message
        if "message" in update_data:
            message = update_data["message"]
            process_telegram_message(message, db)
        
        # Handle callback query (button clicks)
        elif "callback_query" in update_data:
            callback_query = update_data["callback_query"]
            process_callback_query(callback_query, db)
            
    except Exception as e:
        logger.error(f"Error processing Telegram update: {str(e)}")

def process_telegram_message(message: Dict[str, Any], db: Session):
    """Process Telegram message"""
    try:
        chat_id = str(message.get("chat", {}).get("id"))
        text = message.get("text", "").strip().lower()
        from_user = message.get("from", {})
        
        logger.info(f"Received Telegram message from {chat_id}: {text}")
        
        # Handle different message types
        if "document" in message:
            # Handle document intake
            result = handle_telegram_document(message, db)
            logger.info(f"Document intake result: {result}")
        elif "photo" in message:
            # Handle photo intake (resume images)
            result = handle_telegram_photo(message, db)
            logger.info(f"Photo intake result: {result}")
        elif text and len(text) > 100:  # Assume long text might be resume content
            # Handle as text intake for resume processing
            result = handle_telegram_text(message, db)
            logger.info(f"Text intake result: {result}")
        else:
            # Get or create user for regular messages
            user_repo = UserRepository(db)
            user = user_repo.get_by_telegram_or_create(chat_id, from_user)
            
            # Handle different message types
            if text in ["/start", "hi", "hello", "hey"]:
                handle_welcome_message(user, db)
            elif text in ["/help", "help"]:
                handle_help_message(user, db)
            elif text.startswith("/otp"):
                handle_otp_request(user, text, db)
            elif text.startswith("/verify"):
                handle_verification(user, text, db)
            else:
                handle_general_message(user, text, db)
            
    except Exception as e:
        logger.error(f"Error processing Telegram message: {str(e)}")

def process_callback_query(callback_query: Dict[str, Any], db: Session):
    """Process Telegram callback query (button clicks)"""
    try:
        chat_id = str(callback_query.get("message", {}).get("chat", {}).get("id"))
        data = callback_query.get("data", "")
        from_user = callback_query.get("from", {})
        
        logger.info(f"Received Telegram callback from {chat_id}: {data}")
        
        # Get or create user
        user_repo = UserRepository(db)
        user = user_repo.get_by_telegram_or_create(chat_id, from_user)
        
        # Handle different callback data
        if data == "get_otp":
            handle_otp_request(user, "/otp", db)
        elif data == "verify_account":
            handle_verification(user, "/verify", db)
        elif data == "show_help":
            handle_help_message(user, db)
            
    except Exception as e:
        logger.error(f"Error processing Telegram callback query: {str(e)}")

def send_telegram_message(chat_id: str, text: str, keyboard: Optional[Dict] = None):
    """
    Send message to Telegram user (placeholder for actual Telegram API call)
    In production, this would make an API call to Telegram's sendMessage endpoint
    """
    try:
        message_data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        if keyboard:
            message_data["reply_markup"] = keyboard
        
        logger.info(f"Would send Telegram message to {chat_id}: {text[:100]}...")
        
        # In production, you would make the actual API call:
        # response = requests.post(
        #     f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        #     json=message_data
        # )
        
    except Exception as e:
        logger.error(f"Error sending Telegram message: {str(e)}")

def create_main_keyboard():
    """Create main keyboard for Telegram bot"""
    return {
        "inline_keyboard": [
            [
                {"text": "🔢 Get OTP", "callback_data": "get_otp"},
                {"text": "✅ Verify Account", "callback_data": "verify_account"}
            ],
            [
                {"text": "❓ Help", "callback_data": "show_help"}
            ]
        ]
    }

def handle_welcome_message(user: User, db: Session):
    """Handle welcome message from Telegram user"""
    try:
        welcome_text = f"""
👋 **Welcome to our service!**

I'm here to help you get started. Here's what you can do:

🔢 **Get OTP** - Receive a verification code
✅ **Verify Account** - Verify your Telegram account
❓ **Help** - Get help with any questions

Use the buttons below or type commands:
• `/otp` - Get verification code
• `/verify [code]` - Verify your account
• `/help` - Show available commands
        """
        
        # Send welcome message with keyboard
        keyboard = create_main_keyboard()
        send_telegram_message(user.telegram_id, welcome_text, keyboard)
        
        # Update user last active
        user_repo = UserRepository(db)
        user_repo.update_last_active(user)
        
        logger.info(f"Sent welcome message to {user.telegram_id}")
        
    except Exception as e:
        logger.error(f"Error handling welcome message: {str(e)}")

def handle_help_message(user: User, db: Session):
    """Handle help message from Telegram user"""
    try:
        help_text = """
📚 **Help & Commands**

Here are the available commands:

🔢 **/otp** - Get a verification code
✅ **/verify [code]** - Verify your account
👋 **/start** - Welcome message
❓ **/help** - Show this help message

**Quick Actions:**
Use the buttons below for easy access to common features.

Need more help? Contact our support team.
        """
        
        # Send help message with keyboard
        keyboard = create_main_keyboard()
        send_telegram_message(user.telegram_id, help_text, keyboard)
        
        # Update user last active
        user_repo = UserRepository(db)
        user_repo.update_last_active(user)
        
        logger.info(f"Sent help message to {user.telegram_id}")
        
    except Exception as e:
        logger.error(f"Error handling help message: {str(e)}")

def handle_otp_request(user: User, message: str, db: Session):
    """Handle OTP request from Telegram user"""
    try:
        otp_service = OTPService(UserRepository(db))
        
        # Send OTP
        otp_code = otp_service.send_otp(user, send_via_telegram=True)
        
        # Send confirmation message
        confirmation_text = f"""
🔢 **Your verification code is:**

`{otp_code}`

⏰ This code will expire in 5 minutes.

To verify your account, send:
`/verify {otp_code}`

Example: `/verify 123456`

Need help? Just reply with `/help`
        """
        
        # Send confirmation message
        keyboard = create_main_keyboard()
        send_telegram_message(user.telegram_id, confirmation_text, keyboard)
        
        logger.info(f"Sent OTP to {user.telegram_id}")
        
        # Update user last active
        user_repo = UserRepository(db)
        user_repo.update_last_active(user)
        
    except Exception as e:
        logger.error(f"Error handling OTP request: {str(e)}")
        error_text = "❌ Sorry, I couldn't send an OTP. Please try again later."
        send_telegram_message(user.telegram_id, error_text)

def handle_verification(user: User, message: str, db: Session):
    """Handle verification request from Telegram user"""
    try:
        # Extract OTP from message if provided
        if message == "/verify":
            verification_text = """
🔐 **Please provide your verification code.**

Send:
`/verify [your OTP code]`

Example: `/verify 123456`

Need help? Just reply with `/help`
            """
            
            # Send verification request
            keyboard = create_main_keyboard()
            send_telegram_message(user.telegram_id, verification_text, keyboard)
            
            logger.info(f"Requested verification code from {user.telegram_id}")
        else:
            # Extract OTP from message
            parts = message.split()
            if len(parts) >= 2 and parts[0].lower() == "/verify":
                otp_code = parts[1]
                
                # Verify OTP
                otp_service = OTPService(UserRepository(db))
                if otp_service.verify_otp(user, otp_code):
                    # Mark user as verified
                    user_repo = UserRepository(db)
                    user = user_repo.set_verified(user)
                    
                    success_text = f"""
✅ **Account Verified Successfully!**

Your Telegram account has been verified and linked to your profile.

🎉 **You can now:**
• Access all features
• Receive notifications
• Use our full service

Welcome aboard! 🚀
                    """
                    
                    # Send success message
                    keyboard = create_main_keyboard()
                    send_telegram_message(user.telegram_id, success_text, keyboard)
                    
                    logger.info(f"Successfully verified Telegram account for {user.telegram_id}")
                else:
                    error_text = """
❌ **Invalid Verification Code**

The code you provided is incorrect or has expired.

Please send:
`/verify [your OTP code]`

Example: `/verify 123456`

Need help? Just reply with `/help`
                    """
                    
                    # Send error message
                    keyboard = create_main_keyboard()
                    send_telegram_message(user.telegram_id, error_text, keyboard)
                    
                    logger.warning(f"Failed verification attempt for {user.telegram_id}")
            else:
                error_text = """
❌ **Invalid Format**

Please use the correct format:
`/verify [your OTP code]`

Example: `/verify 123456`
                """
                
                # Send error message
                keyboard = create_main_keyboard()
                send_telegram_message(user.telegram_id, error_text, keyboard)
        
        # Update user last active
        user_repo = UserRepository(db)
        user_repo.update_last_active(user)
        
    except Exception as e:
        logger.error(f"Error handling verification: {str(e)}")
        error_text = "❌ Sorry, there was an error with verification. Please try again."
        send_telegram_message(user.telegram_id, error_text)

def handle_general_message(user: User, message: str, db: Session):
    """Handle general message from Telegram user"""
    try:
        # Default response for unrecognized commands
        default_text = f"""
🤔 **I'm not sure what you mean.**

Try these commands:
• `/otp` - Get verification code
• `/verify [code]` - Verify your account
• `/help` - Show available commands

Or use the buttons below for quick access.

Need help? Just reply with `/help`
        """
        
        # Send default response with keyboard
        keyboard = create_main_keyboard()
        send_telegram_message(user.telegram_id, default_text, keyboard)
        
        logger.info(f"Sent default response to {user.telegram_id}")
        
        # Update user last active
        user_repo = UserRepository(db)
        user_repo.update_last_active(user)
        
    except Exception as e:
        logger.error(f"Error handling general message: {str(e)}")