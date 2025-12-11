import random
import string
from datetime import datetime, timedelta
from typing import Optional
from ..models.users import User
from ..repositories.user_repo import UserRepository
from ..config_settings import settings
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class OTPService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.otp_length = int(os.getenv("OTP_LENGTH", "6"))
        self.otp_expiry_minutes = int(os.getenv("OTP_EXPIRY_MINUTES", "5"))
        self.send_otp_via_sms = os.getenv("SEND_OTP_VIA_SMS", "false").lower() == "true"
        
        # Twilio configuration
        self.twilio_enabled = os.getenv("SMS_PROVIDER", "").lower() == "twilio"
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Validate Twilio configuration
        if self.twilio_enabled:
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
                logger.error("Twilio is enabled but required configuration is missing")
                self.twilio_enabled = False
            else:
                try:
                    from twilio.rest import Client
                    self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
                    logger.info("Twilio client initialized successfully")
                except ImportError:
                    logger.error("Twilio package not installed. Install with: pip install twilio")
                    self.twilio_enabled = False
                except Exception as e:
                    logger.error(f"Failed to initialize Twilio client: {str(e)}")
                    self.twilio_enabled = False
    
    def generate_otp(self) -> str:
        """Generate a random OTP based on configured length"""
        digits = string.digits
        return ''.join(random.choice(digits) for _ in range(self.otp_length))
    
    def send_otp(self, user: User, send_via_sms: Optional[bool] = None) -> str:
        """
        Generate and send OTP to user
        
        Args:
            user: User object
            send_via_sms: Override default SMS sending behavior
            
        Returns:
            Generated OTP code
            
        Raises:
            Exception: If OTP sending fails
        """
        try:
            # Generate OTP
            otp_code = self.generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=self.otp_expiry_minutes)
            
            # Update user with OTP
            user.update_otp(otp_code, expires_at)
            self.user_repository.save(user)
            
            # Determine if we should send SMS
            should_send_sms = send_via_sms if send_via_sms is not None else self.send_otp_via_sms
            
            if should_send_sms:
                self._send_sms(user.phone, otp_code)
            else:
                # For demo purposes, log the OTP
                logger.info(f"OTP for {user.phone}: {otp_code}")
            
            logger.info(f"OTP sent to {user.phone}")
            return otp_code
            
        except Exception as e:
            logger.error(f"Failed to send OTP to {user.phone}: {str(e)}")
            raise
    
    def verify_otp(self, user: User, otp_code: str) -> bool:
        """
        Verify OTP for user
        
        Args:
            user: User object
            otp_code: OTP code to verify
            
        Returns:
            True if OTP is valid, False otherwise
        """
        try:
            if user.is_otp_valid(otp_code):
                # Clear OTP after successful verification
                user.clear_otp()
                self.user_repository.save(user)
                logger.info(f"OTP verified for {user.phone}")
                return True
            else:
                logger.warning(f"Invalid OTP attempt for {user.phone}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify OTP for {user.phone}: {str(e)}")
            return False
    
    def _send_sms(self, phone: str, otp_code: str) -> bool:
        """
        Send SMS via Twilio
        
        Args:
            phone: Phone number to send SMS to
            otp_code: OTP code to send
            
        Returns:
            True if SMS sent successfully, False otherwise
        """
        if not self.twilio_enabled:
            logger.warning(f"SMS sending disabled for {phone}")
            return False
        
        try:
            # Format phone number to E.164 format
            formatted_phone = self._format_phone_number(phone)
            
            # Create and send SMS message
            message = self.twilio_client.messages.create(
                body=f"Your OTP is: {otp_code}. This code will expire in {self.otp_expiry_minutes} minutes.",
                from_=self.twilio_phone_number,
                to=formatted_phone
            )
            
            logger.info(f"SMS sent via Twilio to {phone}, SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone}: {str(e)}")
            return False
    
    def _format_phone_number(self, phone: str) -> str:
        """
        Format phone number to E.164 format
        
        Args:
            phone: Phone number to format
            
        Returns:
            Formatted phone number in E.164 format
        """
        # Remove all non-digit characters
        digits_only = ''.join(c for c in phone if c.isdigit())
        
        # If the number doesn't start with +, assume it's a local number
        if not digits_only.startswith('+'):
            # For Indian numbers, add +91 prefix
            if len(digits_only) == 10 and digits_only.startswith('9'):
                return f"+91{digits_only}"
            # For US numbers, add +1 prefix
            elif len(digits_only) == 10 and digits_only.startswith('1'):
                return f"+1{digits_only}"
            # For other numbers, add + prefix (assuming international format)
            else:
                return f"+{digits_only}"
        
        return digits_only
    
    def cleanup_expired_otps(self):
        """Clean up expired OTP codes (optional maintenance task)"""
        try:
            # This would typically be a background job
            # For now, we'll handle it during verification
            logger.info("OTP cleanup task would run here")
        except Exception as e:
            logger.error(f"Failed to cleanup expired OTPs: {str(e)}")
    
    def get_otp_status(self, user: User) -> dict:
        """
        Get OTP status for a user
        
        Args:
            user: User object
            
        Returns:
            Dictionary with OTP status information
        """
        return {
            "has_otp": user.otp_code is not None,
            "otp_expires_at": user.otp_expires_at,
            "is_expired": user.otp_expires_at and datetime.utcnow() > user.otp_expires_at,
            "otp_length": self.otp_length,
            "otp_expiry_minutes": self.otp_expiry_minutes,
            "sms_enabled": self.twilio_enabled
        }
    
    def resend_otp(self, user: User) -> str:
        """
        Resend OTP to an existing user
        
        Args:
            user: User object
            
        Returns:
            New OTP code
        """
        try:
            # Clear existing OTP
            user.clear_otp()
            self.user_repository.save(user)
            
            # Generate and send new OTP
            return self.send_otp(user)
            
        except Exception as e:
            logger.error(f"Failed to resend OTP to {user.phone}: {str(e)}")
            raise