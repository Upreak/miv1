import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from ..models.users import User
from ..repositories.user_repo import UserRepository
from ..security.otp_service import OTPService
from ..security.video_otp_service import VideoOTPService
from ..security.token_manager import TokenManager
from ..security.rate_limiter import RateLimiter
from ..security.social_auth import SocialAuthService
from ..security.totp_service import TOTPService
from ..security.email_service import EmailService
from ..shared.exceptions import AuthenticationError, RateLimitError, SecurityError

logger = logging.getLogger(__name__)

class EnhancedAuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.otp_service = OTPService(self.user_repo)
        self.video_otp_service = VideoOTPService()
        self.token_manager = TokenManager()
        self.rate_limiter = RateLimiter()
        self.social_auth = SocialAuthService()
        self.totp_service = TOTPService()
        self.email_service = EmailService()
        
        # Security settings
        self.max_login_attempts = 5
        self.lockout_duration = 15  # minutes
        self.session_timeout = 1800  # seconds (30 minutes)
        self.mfa_required = False
        
    async def authenticate_user(self, identifier: str, auth_method: str = "phone", **kwargs) -> Dict[str, Any]:
        """
        Authenticate user using specified method
        
        Args:
            identifier: Phone number, email, or social ID
            auth_method: Authentication method (phone, email, video_otp, social, totp)
            **kwargs: Additional authentication parameters
            
        Returns:
            Authentication result with tokens and user info
        """
        try:
            # Rate limiting check
            if await self.rate_limiter.is_rate_limited(identifier, "auth"):
                raise RateLimitError("Too many authentication attempts")
            
            # Get user by identifier
            user = await self._get_user_by_identifier(identifier, auth_method)
            if not user:
                # Auto-create user for phone and email
                if auth_method in ["phone", "email"]:
                    user = await self._create_user(identifier, auth_method, **kwargs)
                else:
                    raise AuthenticationError("User not found")
            
            # Check if account is locked
            if user.is_account_locked():
                raise SecurityError("Account is temporarily locked")
            
            # Authenticate based on method
            if auth_method == "phone":
                return await self._authenticate_by_phone(user, kwargs.get("otp_code"))
            elif auth_method == "email":
                return await self._authenticate_by_email(user, kwargs.get("otp_code"))
            elif auth_method == "video_otp":
                return await self._authenticate_by_video_otp(user, kwargs.get("session_id"), kwargs.get("user_otp"))
            elif auth_method == "social":
                return await self._authenticate_by_social(user, kwargs.get("provider"), kwargs.get("access_token"))
            elif auth_method == "totp":
                return await self._authenticate_by_totp(user, kwargs.get("totp_code"))
            else:
                raise AuthenticationError("Unsupported authentication method")
                
        except Exception as e:
            logger.error(f"Authentication error for {identifier}: {str(e)}")
            raise
    
    async def _get_user_by_identifier(self, identifier: str, auth_method: str) -> Optional[User]:
        """Get user by identifier based on authentication method"""
        try:
            if auth_method == "phone":
                return self.user_repo.get_by_phone(identifier)
            elif auth_method == "email":
                return self.user_repo.get_by_email(identifier)
            elif auth_method == "social":
                provider = identifier.split("_")[0] if "_" in identifier else identifier
                social_id = identifier.split("_")[1] if "_" in identifier else identifier
                return self.user_repo.get_by_social_login(provider, social_id)
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting user by {auth_method} {identifier}: {str(e)}")
            return None
    
    async def _create_user(self, identifier: str, auth_method: str, **kwargs) -> User:
        """Create new user"""
        try:
            user_data = {
                "role": kwargs.get("role", "CANDIDATE"),
                "full_name": kwargs.get("full_name"),
                "preferred_auth_method": auth_method
            }
            
            if auth_method == "phone":
                user = self.user_repo.get_by_phone_or_create(identifier, **user_data)
            elif auth_method == "email":
                user = self.user_repo.get_by_email_or_create(identifier, **user_data)
            else:
                raise AuthenticationError("Unsupported authentication method for user creation")
            
            logger.info(f"Created new user with {auth_method}: {identifier}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user with {auth_method} {identifier}: {str(e)}")
            raise
    
    async def _authenticate_by_phone(self, user: User, otp_code: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate user by phone with OTP"""
        try:
            if not otp_code:
                # Send OTP
                otp_code = self.otp_service.send_otp(user)
                return {
                    "status": "otp_sent",
                    "message": "OTP sent to your phone",
                    "otp_code": otp_code,  # Remove in production
                    "user_id": user.id,
                    "auth_method": "phone"
                }
            
            # Verify OTP
            if not self.otp_service.verify_otp(user, otp_code):
                # Increment failed attempts
                user.increment_login_attempts()
                self.user_repo.save(user)
                raise AuthenticationError("Invalid OTP")
            
            # Reset failed attempts
            user.reset_login_attempts()
            user.mark_verified()
            user.update_last_login()
            self.user_repo.save(user)
            
            # Generate tokens
            tokens = self.token_manager.create_tokens_for_user(user.id, user.role)
            
            # Check if MFA is required
            if user.require_mfa or user.totp_enabled:
                return {
                    "status": "mfa_required",
                    "message": "Multi-factor authentication required",
                    "user_id": user.id,
                    "auth_method": "phone",
                    "tokens": tokens
                }
            
            return {
                "status": "authenticated",
                "message": "Authentication successful",
                "user": user.to_dict(),
                "tokens": tokens,
                "auth_method": "phone"
            }
            
        except Exception as e:
            logger.error(f"Phone authentication error: {str(e)}")
            raise
    
    async def _authenticate_by_email(self, user: User, otp_code: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate user by email with OTP"""
        try:
            if not otp_code:
                # Send OTP via email
                otp_code = self.email_service.send_otp(user.email)
                user.update_otp(otp_code, datetime.utcnow() + timedelta(minutes=5))
                self.user_repo.save(user)
                
                return {
                    "status": "otp_sent",
                    "message": "OTP sent to your email",
                    "user_id": user.id,
                    "auth_method": "email"
                }
            
            # Verify OTP
            if not user.is_otp_valid(otp_code):
                user.increment_login_attempts()
                self.user_repo.save(user)
                raise AuthenticationError("Invalid OTP")
            
            # Reset failed attempts
            user.reset_login_attempts()
            user.mark_verified()
            user.email_verified = True
            user.update_last_login()
            user.clear_otp()
            self.user_repo.save(user)
            
            # Generate tokens
            tokens = self.token_manager.create_tokens_for_user(user.id, user.role)
            
            return {
                "status": "authenticated",
                "message": "Authentication successful",
                "user": user.to_dict(),
                "tokens": tokens,
                "auth_method": "email"
            }
            
        except Exception as e:
            logger.error(f"Email authentication error: {str(e)}")
            raise
    
    async def _authenticate_by_video_otp(self, user: User, session_id: Optional[str] = None, user_otp: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate user by video OTP"""
        try:
            if not session_id or not user_otp:
                # Create video OTP session
                session_id, video_data = self.video_otp_service.create_video_otp_session(user.id)
                
                return {
                    "status": "video_otp_created",
                    "message": "Video OTP session created",
                    "session_id": session_id,
                    "video_data": video_data,
                    "user_id": user.id,
                    "auth_method": "video_otp"
                }
            
            # Verify video OTP
            if not self.video_otp_service.verify_video_otp_session(session_id, user_otp):
                user.increment_login_attempts()
                self.user_repo.save(user)
                raise AuthenticationError("Invalid video OTP")
            
            # Reset failed attempts
            user.reset_login_attempts()
            user.mark_verified()
            user.update_last_login()
            self.user_repo.save(user)
            
            # Generate tokens
            tokens = self.token_manager.create_tokens_for_user(user.id, user.role)
            
            return {
                "status": "authenticated",
                "message": "Authentication successful",
                "user": user.to_dict(),
                "tokens": tokens,
                "auth_method": "video_otp"
            }
            
        except Exception as e:
            logger.error(f"Video OTP authentication error: {str(e)}")
            raise
    
    async def _authenticate_by_social(self, user: User, provider: str, access_token: str) -> Dict[str, Any]:
        """Authenticate user by social login"""
        try:
            # Verify social token
            social_user = await self.social_auth.verify_token(provider, access_token)
            if not social_user:
                raise AuthenticationError("Invalid social token")
            
            # Link social account if not already linked
            if not user.has_social_login(provider):
                user.set_social_login_id(provider, social_user["id"])
                self.user_repo.save(user)
            
            # Mark user as verified
            user.mark_verified()
            user.update_last_login()
            self.user_repo.save(user)
            
            # Generate tokens
            tokens = self.token_manager.create_tokens_for_user(user.id, user.role)
            
            return {
                "status": "authenticated",
                "message": "Authentication successful",
                "user": user.to_dict(),
                "tokens": tokens,
                "auth_method": "social"
            }
            
        except Exception as e:
            logger.error(f"Social authentication error: {str(e)}")
            raise
    
    async def _authenticate_by_totp(self, user: User, totp_code: str) -> Dict[str, Any]:
        """Authenticate user by TOTP"""
        try:
            if not user.totp_enabled:
                raise AuthenticationError("TOTP not enabled for this user")
            
            # Verify TOTP
            if not self.totp_service.verify_totp(user, totp_code):
                # Try backup codes
                if user.is_backup_code_valid(totp_code):
                    logger.info("User authenticated with backup code")
                else:
                    user.increment_login_attempts()
                    self.user_repo.save(user)
                    raise AuthenticationError("Invalid TOTP code")
            
            # Reset failed attempts
            user.reset_login_attempts()
            user.update_last_login()
            self.user_repo.save(user)
            
            # Generate tokens
            tokens = self.token_manager.create_tokens_for_user(user.id, user.role)
            
            return {
                "status": "authenticated",
                "message": "Authentication successful",
                "user": user.to_dict(),
                "tokens": tokens,
                "auth_method": "totp"
            }
            
        except Exception as e:
            logger.error(f"TOTP authentication error: {str(e)}")
            raise
    
    async def verify_mfa(self, user: User, mfa_code: str, mfa_method: str = "totp") -> Dict[str, Any]:
        """Verify multi-factor authentication"""
        try:
            if mfa_method == "totp":
                if not self.totp_service.verify_totp(user, mfa_code):
                    # Try backup codes
                    if user.is_backup_code_valid(mfa_code):
                        logger.info("MFA verified with backup code")
                    else:
                        raise AuthenticationError("Invalid MFA code")
            elif mfa_method == "sms":
                if not self.otp_service.verify_otp(user, mfa_code):
                    raise AuthenticationError("Invalid SMS code")
            elif mfa_method == "email":
                if not user.is_otp_valid(mfa_code):
                    raise AuthenticationError("Invalid email code")
            else:
                raise AuthenticationError("Unsupported MFA method")
            
            # Generate final tokens
            tokens = self.token_manager.create_tokens_for_user(user.id, user.role)
            
            return {
                "status": "authenticated",
                "message": "MFA verification successful",
                "user": user.to_dict(),
                "tokens": tokens
            }
            
        except Exception as e:
            logger.error(f"MFA verification error: {str(e)}")
            raise
    
    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            if not self.token_manager.is_refresh_token(refresh_token):
                raise AuthenticationError("Invalid refresh token")
            
            payload = self.token_manager.verify_token(refresh_token)
            if not payload:
                raise AuthenticationError("Invalid refresh token")
            
            user_id = payload.get("sub")
            user = self.user_repo.get_by_id(user_id)
            
            if not user:
                raise AuthenticationError("User not found")
            
            # Check if refresh token is valid
            if user.current_refresh_token != refresh_token:
                raise AuthenticationError("Refresh token revoked")
            
            # Generate new tokens
            tokens = self.token_manager.create_tokens_for_user(user.id, user.role)
            
            # Update user's refresh token
            user.current_refresh_token = tokens["refresh_token"]
            user.rotate_refresh_token()
            user.update_last_login()
            self.user_repo.save(user)
            
            return {
                "status": "tokens_refreshed",
                "message": "Tokens refreshed successfully",
                "tokens": tokens
            }
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise
    
    async def logout(self, user: User, refresh_token: str = None) -> Dict[str, Any]:
        """Logout user"""
        try:
            # Invalidate refresh token
            if refresh_token:
                user.current_refresh_token = None
                user.rotate_refresh_token()
                self.user_repo.save(user)
            
            # Update last activity
            user.update_last_active()
            self.user_repo.save(user)
            
            return {
                "status": "logged_out",
                "message": "Successfully logged out"
            }
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            raise
    
    async def revoke_all_tokens(self, user: User) -> Dict[str, Any]:
        """Revoke all user tokens"""
        try:
            user.current_refresh_token = None
            user.rotate_refresh_token()
            self.user_repo.save(user)
            
            return {
                "status": "tokens_revoked",
                "message": "All tokens revoked successfully"
            }
            
        except Exception as e:
            logger.error(f"Token revocation error: {str(e)}")
            raise
    
    async def setup_totp(self, user: User) -> Dict[str, Any]:
        """Setup TOTP for user"""
        try:
            # Generate TOTP secret
            secret = self.totp_service.generate_secret()
            
            # Generate provisioning URI
            provisioning_uri = self.totp_service.generate_provisioning_uri(user.email, secret)
            
            # Generate backup codes
            backup_codes = self.totp_service.generate_backup_codes()
            
            # Store backup codes
            for code in backup_codes:
                user.add_backup_code(code)
            
            # Store secret temporarily (don't enable yet)
            user.set_totp_secret(secret)
            self.user_repo.save(user)
            
            return {
                "status": "totp_setup",
                "message": "TOTP setup initiated",
                "provisioning_uri": provisioning_uri,
                "backup_codes": backup_codes,
                "secret": secret  # Remove in production
            }
            
        except Exception as e:
            logger.error(f"TOTP setup error: {str(e)}")
            raise
    
    async def enable_totp(self, user: User, totp_code: str) -> Dict[str, Any]:
        """Enable TOTP for user"""
        try:
            if not user.totp_secret:
                raise AuthenticationError("TOTP not set up")
            
            # Verify TOTP code
            if not self.totp_service.verify_totp(user, totp_code):
                raise AuthenticationError("Invalid TOTP code")
            
            # Enable TOTP
            user.enable_totp()
            self.user_repo.save(user)
            
            return {
                "status": "totp_enabled",
                "message": "TOTP enabled successfully"
            }
            
        except Exception as e:
            logger.error(f"TOTP enable error: {str(e)}")
            raise
    
    async def disable_totp(self, user: User, totp_code: str) -> Dict[str, Any]:
        """Disable TOTP for user"""
        try:
            if not user.totp_enabled:
                raise AuthenticationError("TOTP not enabled")
            
            # Verify TOTP code
            if not self.totp_service.verify_totp(user, totp_code):
                raise AuthenticationError("Invalid TOTP code")
            
            # Disable TOTP
            user.disable_totp()
            self.user_repo.save(user)
            
            return {
                "status": "totp_disabled",
                "message": "TOTP disabled successfully"
            }
            
        except Exception as e:
            logger.error(f"TOTP disable error: {str(e)}")
            raise
    
    async def get_user_security_info(self, user: User) -> Dict[str, Any]:
        """Get user security information"""
        try:
            return {
                "user_id": user.id,
                "is_verified": user.is_verified,
                "email_verified": user.email_verified,
                "phone_verified": user.phone_verified,
                "totp_enabled": user.totp_enabled,
                "require_mfa": user.require_mfa,
                "login_attempts": user.login_attempts,
                "locked_until": user.locked_until.isoformat() if user.locked_until else None,
                "preferred_auth_method": user.preferred_auth_method,
                "social_logins": {
                    "google": user.has_social_login("google"),
                    "facebook": user.has_social_login("facebook"),
                    "linkedin": user.has_social_login("linkedin")
                },
                "backup_codes_remaining": len(user.backup_codes) if user.backup_codes else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting user security info: {str(e)}")
            raise