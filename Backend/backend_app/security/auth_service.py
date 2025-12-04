from typing import Optional, Dict, Any
from datetime import datetime
import logging

from ..models.users import User
from ..repositories.user_repo import UserRepository
from ..security.otp_service import OTPService
from ..security.token_manager import TokenManager

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, user_repository: UserRepository, otp_service: OTPService, token_manager: TokenManager):
        self.user_repository = user_repository
        self.otp_service = otp_service
        self.token_manager = token_manager
    
    def start_login(self, phone: str, send_via_sms: bool = True) -> Dict[str, Any]:
        """
        Start login process by sending OTP
        
        Args:
            phone: User's phone number
            send_via_sms: Whether to send via SMS (for demo, set to False)
            
        Returns:
            Dictionary with login status and message
        """
        try:
            # Get or create user
            user = self.user_repository.get_by_phone_or_create(phone)
            
            # Send OTP
            otp_code = self.otp_service.send_otp(user, send_via_sms)
            
            logger.info(f"Login initiated for phone {phone}")
            
            return {
                "success": True,
                "message": f"OTP sent to {phone}",
                "phone": phone,
                "otp_code": otp_code if not send_via_sms else None  # Remove in production
            }
            
        except Exception as e:
            logger.error(f"Login initiation failed for {phone}: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "phone": phone
            }
    
    def complete_login(self, phone: str, otp_code: str) -> Optional[Dict[str, Any]]:
        """
        Complete login process by verifying OTP
        
        Args:
            phone: User's phone number
            otp_code: OTP code to verify
            
        Returns:
            Dictionary with tokens and user info, or None if failed
        """
        try:
            # Get user
            user = self.user_repository.get_by_phone(phone)
            if not user:
                logger.warning(f"User not found for phone {phone}")
                return None
            
            # Verify OTP
            if not self.otp_service.verify_otp(user, otp_code):
                logger.warning(f"Invalid OTP attempt for {phone}")
                return None
            
            # Mark user as verified if not already
            if not user.is_verified:
                user = self.user_repository.set_verified(user)
            
            # Update last login
            user = self.user_repository.update_last_login(user)
            
            # Generate tokens
            tokens = self.token_manager.create_tokens_for_user(user.id, user.role)
            
            logger.info(f"Login completed successfully for {phone}")
            
            return {
                "success": True,
                "tokens": tokens,
                "user": {
                    "id": user.id,
                    "phone": user.phone,
                    "whatsapp_number": user.whatsapp_number,
                    "telegram_id": user.telegram_id,
                    "role": user.role,
                    "full_name": user.full_name,
                    "is_verified": user.is_verified,
                    "status": user.status,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
            }
            
        except Exception as e:
            logger.error(f"Login completion failed for {phone}: {str(e)}")
            return None
    
    def social_login(self, platform: str, identifier: str, phone: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Handle social login (WhatsApp or Telegram)
        
        Args:
            platform: "whatsapp" or "telegram"
            identifier: Platform-specific identifier (phone number for WhatsApp, chat_id for Telegram)
            phone: Optional phone number to associate
            
        Returns:
            Dictionary with tokens and user info, or None if failed
        """
        try:
            # Get or create user based on platform
            if platform == "whatsapp":
                user = self.user_repository.get_by_whatsapp_or_create(identifier)
            elif platform == "telegram":
                user = self.user_repository.get_by_telegram_or_create(identifier)
            else:
                logger.error(f"Unsupported platform: {platform}")
                return None
            
            # Update phone if provided
            if phone and not user.phone:
                user.phone = phone
                user = self.user_repository.update(user)
            
            # Mark user as verified (social login users are automatically verified)
            if not user.is_verified:
                user = self.user_repository.set_verified(user)
            
            # Update last login
            user = self.user_repository.update_last_login(user)
            
            # Generate tokens
            tokens = self.token_manager.create_tokens_for_user(user.id, user.role)
            
            logger.info(f"Social login completed for {platform} user {identifier}")
            
            return {
                "success": True,
                "tokens": tokens,
                "user": {
                    "id": user.id,
                    "phone": user.phone,
                    "whatsapp_number": user.whatsapp_number,
                    "telegram_id": user.telegram_id,
                    "role": user.role,
                    "full_name": user.full_name,
                    "is_verified": user.is_verified,
                    "status": user.status,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
            }
            
        except Exception as e:
            logger.error(f"Social login failed for {platform} user {identifier}: {str(e)}")
            return None
    
    def refresh_tokens(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token to validate
            
        Returns:
            Dictionary with new tokens, or None if failed
        """
        try:
            # Verify refresh token
            if not self.token_manager.is_refresh_token(refresh_token):
                logger.warning("Invalid refresh token format")
                return None
            
            payload = self.token_manager.verify_token(refresh_token)
            if not payload:
                logger.warning("Invalid refresh token")
                return None
            
            user_id = payload.get("sub")
            role = payload.get("role")
            
            # Get user
            user = self.user_repository.get_by_id(user_id)
            if not user:
                logger.warning(f"User not found for refresh token: {user_id}")
                return None
            
            # Generate new tokens
            tokens = self.token_manager.create_tokens_for_user(user.id, user.role)
            
            logger.info(f"Token refreshed for user {user_id}")
            
            return {
                "success": True,
                "tokens": tokens
            }
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return None
    
    def logout(self, user_id: str) -> Dict[str, Any]:
        """
        Logout user (invalidate token)
        
        Args:
            user_id: User ID to logout
            
        Returns:
            Dictionary with logout status
        """
        try:
            # In production, you might want to add the token to a blacklist
            logger.info(f"User {user_id} logged out")
            
            return {
                "success": True,
                "message": "Successfully logged out"
            }
            
        except Exception as e:
            logger.error(f"Logout failed for user {user_id}: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            Dictionary with user info, or None if not found
        """
        try:
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return None
            
            # Update last active timestamp
            self.user_repository.update_last_active(user)
            
            return {
                "id": user.id,
                "phone": user.phone,
                "whatsapp_number": user.whatsapp_number,
                "telegram_id": user.telegram_id,
                "role": user.role,
                "full_name": user.full_name,
                "is_verified": user.is_verified,
                "status": user.status,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "last_active": user.last_active.isoformat() if user.last_active else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get user info for {user_id}: {str(e)}")
            return None
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user profile information
        
        Args:
            user_id: User ID to update
            updates: Dictionary with fields to update
            
        Returns:
            Dictionary with updated user info, or None if failed
        """
        try:
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return None
            
            # Update allowed fields
            allowed_fields = ["full_name", "role", "status"]
            for field in allowed_fields:
                if field in updates:
                    setattr(user, field, updates[field])
            
            # Save changes
            user = self.user_repository.update(user)
            
            logger.info(f"User profile updated for {user_id}")
            
            return {
                "id": user.id,
                "phone": user.phone,
                "whatsapp_number": user.whatsapp_number,
                "telegram_id": user.telegram_id,
                "role": user.role,
                "full_name": user.full_name,
                "is_verified": user.is_verified,
                "status": user.status,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "last_active": user.last_active.isoformat() if user.last_active else None
            }
            
        except Exception as e:
            logger.error(f"Failed to update user profile for {user_id}: {str(e)}")
            return None