import base64
import json
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoOTPService:
    def __init__(self):
        self.video_otp_length = 8
        self.video_otp_expiry_minutes = 10
        self.session_timeout = 300  # 5 minutes
        self.video_storage_path = Path("storage/video_otps")
        self.video_storage_path.mkdir(parents=True, exist_ok=True)
        
        # WebRTC configuration
        self.webrtc_ice_servers = [
            "stun:stun.l.google.com:19302",
            "stun:stun1.l.google.com:19302"
        ]
        
        # Video OTP templates
        self.video_templates = {
            "default": {
                "background_color": "#1a1a1a",
                "text_color": "#ffffff",
                "font_size": 48,
                "duration": 10,
                "animation": "fade"
            },
            "secure": {
                "background_color": "#2c3e50",
                "text_color": "#ecf0f1",
                "font_size": 64,
                "duration": 15,
                "animation": "slide"
            }
        }
    
    def generate_video_otp_data(self, otp_code: str, template: str = "default") -> Dict[str, Any]:
        """
        Generate video OTP data including frames and metadata
        
        Args:
            otp_code: The OTP code to display in video
            template: Video template to use
            
        Returns:
            Dictionary containing video OTP data
        """
        try:
            template_config = self.video_templates.get(template, self.video_templates["default"])
            
            # Generate video frames
            frames = self._generate_video_frames(otp_code, template_config)
            
            # Generate WebRTC offer
            webrtc_offer = self._generate_webrtc_offer()
            
            # Create session data
            session_data = {
                "otp_code": otp_code,
                "template": template,
                "frames": frames,
                "webrtc_offer": webrtc_offer,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(minutes=self.video_otp_expiry_minutes)).isoformat(),
                "ice_servers": self.webrtc_ice_servers
            }
            
            logger.info(f"Generated video OTP data for code: {otp_code}")
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to generate video OTP data: {str(e)}")
            raise
    
    def _generate_video_frames(self, otp_code: str, template_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate video frames for the OTP display
        
        Args:
            otp_code: OTP code to display
            template_config: Template configuration
            
        Returns:
            List of frame data
        """
        frames = []
        
        # Generate background frame
        background_frame = {
            "type": "background",
            "color": template_config["background_color"],
            "width": 800,
            "height": 600
        }
        
        # Generate text frames for each digit
        for i, digit in enumerate(otp_code):
            frame = {
                "type": "text",
                "text": digit,
                "position": {
                    "x": 200 + (i * 80),
                    "y": 300
                },
                "color": template_config["text_color"],
                "font_size": template_config["font_size"],
                "duration": template_config["duration"],
                "animation": template_config["animation"]
            }
            frames.append(frame)
        
        # Add completion frame
        completion_frame = {
            "type": "completion",
            "message": "Video OTP Complete",
            "position": {"x": 400, "y": 500},
            "color": template_config["text_color"],
            "font_size": 24,
            "duration": 3
        }
        frames.append(completion_frame)
        
        return frames
    
    def _generate_webrtc_offer(self) -> Dict[str, Any]:
        """
        Generate WebRTC offer for video streaming
        
        Returns:
            WebRTC offer data
        """
        try:
            # Generate WebRTC session ID
            session_id = secrets.token_urlsafe(16)
            
            # Create WebRTC offer
            offer = {
                "type": "offer",
                "sdp": f"v=0\r\no=- {secrets.token_hex(8)} 1 IN IP4 127.0.0.1\r\ns=-\r\nc=IN IP4 0.0.0.0\r\nt=0 0\r\na=group:BUNDLE video\r\na=extmap:1 urn:ietf:params:rtp-hdrext:sdes:mid\r\na=msid-semantic: WMS {session_id}\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\nc=IN IP4 0.0.0.0\r\na=rtcp:9 IN IP4 0.0.0.0\r\na=ice-ufrag:{secrets.token_hex(4)}\r\na=ice-pwd:{secrets.token_hex(16)}\r\na=ice-options:trickle\r\na=fmtp:96 profile-level-id=42e01f;level-asymmetry-allowed=1;packetization-mode=1\r\na=rtcp-mux\r\na=rtcp-rsize\r\na=ssrc:{secrets.randint(1000000000, 2000000000)} cname:{secrets.token_hex(8)}\r\n",
                "session_id": session_id
            }
            
            return offer
            
        except Exception as e:
            logger.error(f"Failed to generate WebRTC offer: {str(e)}")
            raise
    
    def create_video_otp_session(self, user_id: str) -> Tuple[str, Dict[str, Any]]:
        """
        Create a new video OTP session
        
        Args:
            user_id: User ID for the session
            
        Returns:
            Tuple of (session_id, video_otp_data)
        """
        try:
            # Generate OTP code
            otp_code = self._generate_otp_code()
            
            # Generate video OTP data
            video_data = self.generate_video_otp_data(otp_code)
            
            # Create session ID
            session_id = secrets.token_urlsafe(32)
            
            # Store session data
            session_data = {
                "user_id": user_id,
                "otp_code": otp_code,
                "video_data": video_data,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(minutes=self.video_otp_expiry_minutes)).isoformat(),
                "status": "active"
            }
            
            # Save session to file (in production, use Redis or database)
            session_file = self.video_storage_path / f"{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            logger.info(f"Created video OTP session {session_id} for user {user_id}")
            return session_id, video_data
            
        except Exception as e:
            logger.error(f"Failed to create video OTP session: {str(e)}")
            raise
    
    def verify_video_otp_session(self, session_id: str, user_otp: str) -> bool:
        """
        Verify video OTP session
        
        Args:
            session_id: Session ID to verify
            user_otp: OTP code provided by user
            
        Returns:
            True if verification successful, False otherwise
        """
        try:
            # Load session data
            session_file = self.video_storage_path / f"{session_id}.json"
            
            if not session_file.exists():
                logger.warning(f"Video OTP session {session_id} not found")
                return False
            
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is expired
            expires_at = datetime.fromisoformat(session_data["expires_at"])
            if datetime.utcnow() > expires_at:
                logger.warning(f"Video OTP session {session_id} expired")
                self._cleanup_session(session_id)
                return False
            
            # Verify OTP code
            if session_data["otp_code"] != user_otp:
                logger.warning(f"Invalid OTP code for session {session_id}")
                return False
            
            # Mark session as completed
            session_data["status"] = "completed"
            session_data["completed_at"] = datetime.utcnow().isoformat()
            
            # Save updated session
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            logger.info(f"Video OTP session {session_id} verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify video OTP session: {str(e)}")
            return False
    
    def get_video_otp_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get video OTP data for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            Video OTP data or None if not found
        """
        try:
            session_file = self.video_storage_path / f"{session_id}.json"
            
            if not session_file.exists():
                return None
            
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is expired
            expires_at = datetime.fromisoformat(session_data["expires_at"])
            if datetime.utcnow() > expires_at:
                self._cleanup_session(session_id)
                return None
            
            return session_data["video_data"]
            
        except Exception as e:
            logger.error(f"Failed to get video OTP data: {str(e)}")
            return None
    
    def cleanup_expired_sessions(self):
        """Clean up expired video OTP sessions"""
        try:
            current_time = datetime.utcnow()
            
            for session_file in self.video_storage_path.glob("*.json"):
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    expires_at = datetime.fromisoformat(session_data["expires_at"])
                    if current_time > expires_at:
                        self._cleanup_session(session_file.stem)
                        logger.info(f"Cleaned up expired session {session_file.stem}")
                        
                except Exception as e:
                    logger.error(f"Error cleaning up session {session_file.stem}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {str(e)}")
    
    def _cleanup_session(self, session_id: str):
        """Clean up a specific session"""
        try:
            session_file = self.video_storage_path / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
                logger.info(f"Cleaned up session {session_id}")
        except Exception as e:
            logger.error(f"Failed to cleanup session {session_id}: {str(e)}")
    
    def _generate_otp_code(self) -> str:
        """Generate a random video OTP code"""
        import random
        import string
        
        characters = string.digits + string.ascii_uppercase
        return ''.join(random.choice(characters) for _ in range(self.video_otp_length))
    
    def generate_video_otp_url(self, session_id: str) -> str:
        """
        Generate URL for video OTP playback
        
        Args:
            session_id: Session ID
            
        Returns:
            Video OTP URL
        """
        return f"/api/video-otp/playback/{session_id}"
    
    def validate_webrtc_answer(self, session_id: str, answer: Dict[str, Any]) -> bool:
        """
        Validate WebRTC answer from client
        
        Args:
            session_id: Session ID
            answer: WebRTC answer from client
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation
            if not answer or "type" not in answer or answer["type"] != "answer":
                return False
            
            if "sdp" not in answer:
                return False
            
            # Check if session exists and is active
            session_file = self.video_storage_path / f"{session_id}.json"
            if not session_file.exists():
                return False
            
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            if session_data["status"] != "active":
                return False
            
            logger.info(f"Valid WebRTC answer for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate WebRTC answer: {str(e)}")
            return False
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session status
        
        Args:
            session_id: Session ID
            
        Returns:
            Session status data or None if not found
        """
        try:
            session_file = self.video_storage_path / f"{session_id}.json"
            
            if not session_file.exists():
                return None
            
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check expiration
            expires_at = datetime.fromisoformat(session_data["expires_at"])
            is_expired = datetime.utcnow() > expires_at
            
            return {
                "session_id": session_id,
                "status": session_data["status"],
                "created_at": session_data["created_at"],
                "expires_at": session_data["expires_at"],
                "is_expired": is_expired,
                "otp_code": session_data["otp_code"] if session_data["status"] == "completed" else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get session status: {str(e)}")
            return None