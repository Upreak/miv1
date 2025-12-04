import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import secrets

logger = logging.getLogger(__name__)

class SocialAuthService:
    def __init__(self):
        self.google_client_id = None
        self.google_client_secret = None
        self.google_redirect_uri = None
        
        self.facebook_app_id = None
        self.facebook_app_secret = None
        self.facebook_redirect_uri = None
        
        self.linkedin_client_id = None
        self.linkedin_client_secret = None
        self.linkedin_redirect_uri = None
        
        # Initialize from environment
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables"""
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Google OAuth
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
        
        # Facebook OAuth
        self.facebook_app_id = os.getenv("FACEBOOK_APP_ID")
        self.facebook_app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self.facebook_redirect_uri = os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:8000/auth/facebook/callback")
        
        # LinkedIn OAuth
        self.linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.linkedin_redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/auth/linkedin/callback")
    
    def get_google_auth_url(self, state: str = None) -> str:
        """Generate Google OAuth URL"""
        try:
            if not self.google_client_id:
                raise ValueError("Google Client ID not configured")
            
            if not state:
                state = secrets.token_urlsafe(16)
            
            params = {
                "client_id": self.google_client_id,
                "redirect_uri": self.google_redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state,
                "access_type": "offline",
                "prompt": "consent"
            }
            
            import urllib.parse
            query_string = urllib.parse.urlencode(params)
            auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
            
            logger.info(f"Generated Google auth URL with state: {state}")
            return auth_url, state
            
        except Exception as e:
            logger.error(f"Failed to generate Google auth URL: {str(e)}")
            raise
    
    def get_facebook_auth_url(self, state: str = None) -> str:
        """Generate Facebook OAuth URL"""
        try:
            if not self.facebook_app_id:
                raise ValueError("Facebook App ID not configured")
            
            if not state:
                state = secrets.token_urlsafe(16)
            
            params = {
                "client_id": self.facebook_app_id,
                "redirect_uri": self.facebook_redirect_uri,
                "response_type": "code",
                "scope": "email,public_profile",
                "state": state
            }
            
            import urllib.parse
            query_string = urllib.parse.urlencode(params)
            auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{query_string}"
            
            logger.info(f"Generated Facebook auth URL with state: {state}")
            return auth_url, state
            
        except Exception as e:
            logger.error(f"Failed to generate Facebook auth URL: {str(e)}")
            raise
    
    def get_linkedin_auth_url(self, state: str = None) -> str:
        """Generate LinkedIn OAuth URL"""
        try:
            if not self.linkedin_client_id:
                raise ValueError("LinkedIn Client ID not configured")
            
            if not state:
                state = secrets.token_urlsafe(16)
            
            params = {
                "client_id": self.linkedin_client_id,
                "redirect_uri": self.linkedin_redirect_uri,
                "response_type": "code",
                "scope": "r_liteprofile r_emailaddress",
                "state": state
            }
            
            import urllib.parse
            query_string = urllib.parse.urlencode(params)
            auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{query_string}"
            
            logger.info(f"Generated LinkedIn auth URL with state: {state}")
            return auth_url, state
            
        except Exception as e:
            logger.error(f"Failed to generate LinkedIn auth URL: {str(e)}")
            raise
    
    async def exchange_code_for_token(self, provider: str, code: str, state: str = None) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            if provider == "google":
                return await self._exchange_google_code(code, state)
            elif provider == "facebook":
                return await self._exchange_facebook_code(code, state)
            elif provider == "linkedin":
                return await self._exchange_linkedin_code(code, state)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {str(e)}")
            raise
    
    async def _exchange_google_code(self, code: str, state: str = None) -> Dict[str, Any]:
        """Exchange Google authorization code for access token"""
        try:
            token_url = "https://oauth2.googleapis.com/token"
            
            data = {
                "client_id": self.google_client_id,
                "client_secret": self.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.google_redirect_uri
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Get user info
            user_info = await self._get_google_user_info(token_data["access_token"])
            
            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data["expires_in"],
                "token_type": token_data["token_type"],
                "provider": "google",
                "user": user_info
            }
            
        except Exception as e:
            logger.error(f"Failed to exchange Google code: {str(e)}")
            raise
    
    async def _exchange_facebook_code(self, code: str, state: str = None) -> Dict[str, Any]:
        """Exchange Facebook authorization code for access token"""
        try:
            token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            
            data = {
                "client_id": self.facebook_app_id,
                "client_secret": self.facebook_app_secret,
                "code": code,
                "redirect_uri": self.facebook_redirect_uri
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Get user info
            user_info = await self._get_facebook_user_info(token_data["access_token"])
            
            return {
                "access_token": token_data["access_token"],
                "expires_in": token_data["expires_in"],
                "token_type": token_data["token_type"],
                "provider": "facebook",
                "user": user_info
            }
            
        except Exception as e:
            logger.error(f"Failed to exchange Facebook code: {str(e)}")
            raise
    
    async def _exchange_linkedin_code(self, code: str, state: str = None) -> Dict[str, Any]:
        """Exchange LinkedIn authorization code for access token"""
        try:
            token_url = "https://www.linkedin.com/oauth/v2/accessToken"
            
            data = {
                "client_id": self.linkedin_client_id,
                "client_secret": self.linkedin_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.linkedin_redirect_uri
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Get user info
            user_info = await self._get_linkedin_user_info(token_data["access_token"])
            
            return {
                "access_token": token_data["access_token"],
                "expires_in": token_data["expires_in"],
                "token_type": token_data["token_type"],
                "provider": "linkedin",
                "user": user_info
            }
            
        except Exception as e:
            logger.error(f"Failed to exchange LinkedIn code: {str(e)}")
            raise
    
    async def _get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get Google user information"""
        try:
            user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response = requests.get(user_info_url, headers=headers)
            response.raise_for_status()
            
            user_data = response.json()
            
            return {
                "id": user_data["id"],
                "email": user_data["email"],
                "name": user_data["name"],
                "first_name": user_data.get("given_name"),
                "last_name": user_data.get("family_name"),
                "picture": user_data.get("picture"),
                "verified_email": user_data.get("verified_email", False)
            }
            
        except Exception as e:
            logger.error(f"Failed to get Google user info: {str(e)}")
            raise
    
    async def _get_facebook_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get Facebook user information"""
        try:
            user_info_url = "https://graph.facebook.com/v18.0/me"
            
            params = {
                "access_token": access_token,
                "fields": "id,name,email,first_name,last_name,picture"
            }
            
            response = requests.get(user_info_url, params=params)
            response.raise_for_status()
            
            user_data = response.json()
            
            return {
                "id": user_data["id"],
                "email": user_data.get("email"),
                "name": user_data["name"],
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
                "picture": user_data.get("picture", {}).get("data", {}).get("url"),
                "verified_email": user_data.get("email") is not None
            }
            
        except Exception as e:
            logger.error(f"Failed to get Facebook user info: {str(e)}")
            raise
    
    async def _get_linkedin_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get LinkedIn user information"""
        try:
            # Get user profile
            profile_url = "https://api.linkedin.com/v2/me"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-RestLi-Protocol-Version": "2.0.0"
            }
            
            response = requests.get(profile_url, headers=headers)
            response.raise_for_status()
            
            profile_data = response.json()
            
            # Get user email
            email_url = "https://api.linkedin.com/v2/emailAddress"
            
            email_params = {
                "q": "members",
                "projection": "(elements*(handle~))"
            }
            
            email_response = requests.get(email_url, headers=headers, params=email_params)
            email_response.raise_for_status()
            
            email_data = email_response.json()
            
            # Extract email
            email = None
            if "elements" in email_data and len(email_data["elements"]) > 0:
                email = email_data["elements"][0].get("handle~", {}).get("emailAddress")
            
            return {
                "id": profile_data["id"],
                "email": email,
                "name": f"{profile_data.get('firstName', '')} {profile_data.get('lastName', '')}".strip(),
                "first_name": profile_data.get("firstName"),
                "last_name": profile_data.get("lastName"),
                "picture": None,  # LinkedIn doesn't provide profile picture in basic API
                "verified_email": email is not None
            }
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn user info: {str(e)}")
            raise
    
    async def verify_token(self, provider: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Verify social token and get user info"""
        try:
            if provider == "google":
                return await self._get_google_user_info(access_token)
            elif provider == "facebook":
                return await self._get_facebook_user_info(access_token)
            elif provider == "linkedin":
                return await self._get_linkedin_user_info(access_token)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Failed to verify {provider} token: {str(e)}")
            return None
    
    async def refresh_token(self, provider: str, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh social token"""
        try:
            if provider == "google":
                return await self._refresh_google_token(refresh_token)
            elif provider == "facebook":
                # Facebook doesn't support token refresh in the same way
                return None
            elif provider == "linkedin":
                # LinkedIn doesn't support token refresh in the same way
                return None
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Failed to refresh {provider} token: {str(e)}")
            return None
    
    async def _refresh_google_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh Google token"""
        try:
            token_url = "https://oauth2.googleapis.com/token"
            
            data = {
                "client_id": self.google_client_id,
                "client_secret": self.google_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            return {
                "access_token": token_data["access_token"],
                "expires_in": token_data["expires_in"],
                "token_type": token_data["token_type"]
            }
            
        except Exception as e:
            logger.error(f"Failed to refresh Google token: {str(e)}")
            return None
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get provider configuration"""
        configs = {
            "google": {
                "client_id": self.google_client_id,
                "redirect_uri": self.google_redirect_uri,
                "scopes": ["openid", "email", "profile"],
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth"
            },
            "facebook": {
                "app_id": self.facebook_app_id,
                "redirect_uri": self.facebook_redirect_uri,
                "scopes": ["email", "public_profile"],
                "auth_url": "https://www.facebook.com/v18.0/dialog/oauth"
            },
            "linkedin": {
                "client_id": self.linkedin_client_id,
                "redirect_uri": self.linkedin_redirect_uri,
                "scopes": ["r_liteprofile", "r_emailaddress"],
                "auth_url": "https://www.linkedin.com/oauth/v2/authorization"
            }
        }
        
        return configs.get(provider, {})
    
    def is_provider_configured(self, provider: str) -> bool:
        """Check if provider is configured"""
        configs = {
            "google": self.google_client_id and self.google_client_secret,
            "facebook": self.facebook_app_id and self.facebook_app_secret,
            "linkedin": self.linkedin_client_id and self.linkedin_client_secret
        }
        
        return configs.get(provider, False)
    
    def get_configured_providers(self) -> list:
        """Get list of configured providers"""
        providers = []
        
        if self.is_provider_configured("google"):
            providers.append("google")
        if self.is_provider_configured("facebook"):
            providers.append("facebook")
        if self.is_provider_configured("linkedin"):
            providers.append("linkedin")
        
        return providers