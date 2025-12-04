import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import random
import string
from pathlib import Path

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = None
        self.smtp_port = None
        self.smtp_username = None
        self.smtp_password = None
        self.smtp_use_tls = None
        self.from_email = None
        self.from_name = None
        
        # Email templates
        self.templates_dir = Path("templates/emails")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load email configuration from environment variables"""
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # SMTP configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.from_name = os.getenv("FROM_NAME", "Recruitment App")
    
    def send_otp(self, email: str, otp_code: str, user_name: str = None) -> bool:
        """Send OTP code to email"""
        try:
            if not self.smtp_username or not self.smtp_password:
                logger.error("SMTP configuration not provided")
                return False
            
            # Create email message
            subject = "Your OTP Code"
            body = self._create_otp_email_body(email, otp_code, user_name)
            
            # Send email
            return self._send_email(email, subject, body)
            
        except Exception as e:
            logger.error(f"Failed to send OTP email: {str(e)}")
            return False
    
    def send_welcome_email(self, email: str, user_name: str = None) -> bool:
        """Send welcome email to new user"""
        try:
            subject = "Welcome to Recruitment App"
            body = self._create_welcome_email_body(email, user_name)
            
            return self._send_email(email, subject, body)
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return False
    
    def send_password_reset(self, email: str, reset_token: str, user_name: str = None) -> bool:
        """Send password reset email"""
        try:
            subject = "Password Reset Request"
            body = self._create_password_reset_email_body(email, reset_token, user_name)
            
            return self._send_email(email, subject, body)
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return False
    
    def send_security_alert(self, email: str, alert_type: str, details: Dict[str, Any] = None) -> bool:
        """Send security alert email"""
        try:
            subject = f"Security Alert - {alert_type}"
            body = self._create_security_alert_email_body(email, alert_type, details)
            
            return self._send_email(email, subject, body)
            
        except Exception as e:
            logger.error(f"Failed to send security alert email: {str(e)}")
            return False
    
    def send_account_verification(self, email: str, verification_token: str, user_name: str = None) -> bool:
        """Send account verification email"""
        try:
            subject = "Verify Your Account"
            body = self._create_verification_email_body(email, verification_token, user_name)
            
            return self._send_email(email, subject, body)
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False
    
    def send_mfa_notification(self, email: str, mfa_method: str, user_name: str = None) -> bool:
        """Send MFA notification email"""
        try:
            subject = "Multi-Factor Authentication Notification"
            body = self._create_mfa_email_body(email, mfa_method, user_name)
            
            return self._send_email(email, subject, body)
            
        except Exception as e:
            logger.error(f"Failed to send MFA notification email: {str(e)}")
            return False
    
    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add body
            message.attach(MIMEText(body, "html"))
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls(context=context)
                
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def _create_otp_email_body(self, email: str, otp_code: str, user_name: str = None) -> str:
        """Create OTP email body"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>OTP Verification</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .otp-container {
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 20px 0;
                }
                .otp-code {
                    font-size: 32px;
                    font-weight: bold;
                    color: #007bff;
                    letter-spacing: 3px;
                    margin: 20px 0;
                }
                .expiry {
                    color: #6c757d;
                    font-size: 14px;
                }
                .footer {
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    font-size: 12px;
                    color: #6c757d;
                }
            </style>
        </head>
        <body>
            <h1>Hello {user_name or "User"},</h1>
            <p>Your OTP code for verification is:</p>
            
            <div class="otp-container">
                <div class="otp-code">{otp_code}</div>
                <div class="expiry">This code will expire in 5 minutes</div>
            </div>
            
            <p>If you did not request this code, please ignore this email.</p>
            
            <div class="footer">
                <p>This is an automated message from Recruitment App.</p>
                <p>© 2024 Recruitment App. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        return template.format(
            user_name=user_name or "User",
            otp_code=otp_code
        )
    
    def _create_welcome_email_body(self, email: str, user_name: str = None) -> str:
        """Create welcome email body"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Welcome to Recruitment App</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    background: #007bff;
                    color: white;
                    padding: 20px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }
                .content {
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }
                .button {
                    background: #007bff;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                    margin: 20px 0;
                }
                .footer {
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    font-size: 12px;
                    color: #6c757d;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Welcome to Recruitment App!</h1>
            </div>
            
            <div class="content">
                <h2>Hello {user_name or "User"},</h2>
                <p>Thank you for joining Recruitment App! We're excited to help you find your dream job.</p>
                
                <p>Here's what you can do next:</p>
                <ul>
                    <li>Complete your profile</li>
                    <li>Browse job opportunities</li>
                    <li>Apply to your dream positions</li>
                    <li>Track your application status</li>
                </ul>
                
                <a href="#" class="button">Get Started</a>
                
                <p>If you have any questions, feel free to reach out to our support team.</p>
            </div>
            
            <div class="footer">
                <p>This is an automated message from Recruitment App.</p>
                <p>© 2024 Recruitment App. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        return template.format(user_name=user_name or "User")
    
    def _create_password_reset_email_body(self, email: str, reset_token: str, user_name: str = None) -> str:
        """Create password reset email body"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Password Reset Request</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    background: #dc3545;
                    color: white;
                    padding: 20px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }
                .content {
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }
                .button {
                    background: #dc3545;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                    margin: 20px 0;
                }
                .footer {
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    font-size: 12px;
                    color: #6c757d;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            
            <div class="content">
                <h2>Hello {user_name or "User"},</h2>
                <p>We received a request to reset your password. If you made this request, please click the button below to reset your password.</p>
                
                <a href="#" class="button">Reset Password</a>
                
                <p>If you did not request a password reset, please ignore this email. Your password will remain unchanged.</p>
                
                <p>This link will expire in 24 hours for security reasons.</p>
            </div>
            
            <div class="footer">
                <p>This is an automated message from Recruitment App.</p>
                <p>© 2024 Recruitment App. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        return template.format(user_name=user_name or "User")
    
    def _create_security_alert_email_body(self, email: str, alert_type: str, details: Dict[str, Any] = None) -> str:
        """Create security alert email body"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Security Alert</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    background: #fd7e14;
                    color: white;
                    padding: 20px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }
                .content {
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }
                .alert-details {
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }
                .footer {
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    font-size: 12px;
                    color: #6c757d;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Security Alert</h1>
            </div>
            
            <div class="content">
                <h2>Hello User,</h2>
                <p>We detected unusual activity on your account. Please review the details below:</p>
                
                <div class="alert-details">
                    <h3>Alert Type: {alert_type}</h3>
                    {details}
                </div>
                
                <p>If this activity was not performed by you, please secure your account immediately.</p>
                
                <p><strong>Recommended actions:</strong></p>
                <ul>
                    <li>Change your password</li>
                    <li>Enable two-factor authentication</li>
                    <li>Review your account activity</li>
                    <li>Contact support if needed</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>This is an automated message from Recruitment App.</p>
                <p>© 2024 Recruitment App. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        details_html = ""
        if details:
            details_html += "<p><strong>Details:</strong></p>"
            for key, value in details.items():
                details_html += f"<p><strong>{key}:</strong> {value}</p>"
        
        return template.format(
            alert_type=alert_type,
            details=details_html
        )
    
    def _create_verification_email_body(self, email: str, verification_token: str, user_name: str = None) -> str:
        """Create account verification email body"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Verify Your Account</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    background: #28a745;
                    color: white;
                    padding: 20px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }
                .content {
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }
                .button {
                    background: #28a745;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                    margin: 20px 0;
                }
                .footer {
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    font-size: 12px;
                    color: #6c757d;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Verify Your Account</h1>
            </div>
            
            <div class="content">
                <h2>Hello {user_name or "User"},</h2>
                <p>Thank you for joining Recruitment App! Please verify your email address to complete your registration.</p>
                
                <a href="#" class="button">Verify Email</a>
                
                <p>If the button doesn't work, please copy and paste the following URL into your browser:</p>
                <p><code>https://yourapp.com/verify?token={verification_token}</code></p>
                
                <p>This link will expire in 24 hours for security reasons.</p>
            </div>
            
            <div class="footer">
                <p>This is an automated message from Recruitment App.</p>
                <p>© 2024 Recruitment App. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        return template.format(
            user_name=user_name or "User",
            verification_token=verification_token
        )
    
    def _create_mfa_email_body(self, email: str, mfa_method: str, user_name: str = None) -> str:
        """Create MFA notification email body"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Multi-Factor Authentication</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    background: #17a2b8;
                    color: white;
                    padding: 20px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }
                .content {
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }
                .alert {
                    background: #d1ecf1;
                    border: 1px solid #bee5eb;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }
                .footer {
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    font-size: 12px;
                    color: #6c757d;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Multi-Factor Authentication</h1>
            </div>
            
            <div class="content">
                <h2>Hello {user_name or "User"},</h2>
                <p>We detected a login attempt to your account using multi-factor authentication.</p>
                
                <div class="alert">
                    <h3>Login Details:</h3>
                    <p><strong>Method:</strong> {mfa_method}</p>
                    <p><strong>Time:</strong> {current_time}</p>
                    <p><strong>IP Address:</strong> {ip_address}</p>
                </div>
                
                <p>If this was you, no further action is needed. If this wasn't you, please secure your account immediately.</p>
                
                <p><strong>Security Tips:</strong></p>
                <ul>
                    <li>Use strong, unique passwords</li>
                    <li>Enable two-factor authentication</li>
                    <li>Regularly review your account activity</li>
                    <li>Keep your contact information updated</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>This is an automated message from Recruitment App.</p>
                <p>© 2024 Recruitment App. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return template.format(
            user_name=user_name or "User",
            mfa_method=mfa_method,
            current_time=current_time,
            ip_address="Unknown"  # In production, get actual IP
        )
    
    def generate_verification_token(self) -> str:
        """Generate email verification token"""
        return secrets.token_urlsafe(32)
    
    def generate_password_reset_token(self) -> str:
        """Generate password reset token"""
        return secrets.token_urlsafe(32)
    
    def test_email_connection(self) -> bool:
        """Test email connection"""
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls(context=context)
                
                server.login(self.smtp_username, self.smtp_password)
            
            logger.info("Email connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Email connection test failed: {str(e)}")
            return False
    
    def get_email_statistics(self) -> Dict[str, Any]:
        """Get email service statistics"""
        try:
            return {
                "smtp_server": self.smtp_server,
                "smtp_port": self.smtp_port,
                "smtp_use_tls": self.smtp_use_tls,
                "from_email": self.from_email,
                "from_name": self.from_name,
                "templates_dir": str(self.templates_dir),
                "available_templates": [
                    "otp.html",
                    "welcome.html",
                    "password_reset.html",
                    "security_alert.html",
                    "verification.html",
                    "mfa.html"
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get email statistics: {str(e)}")
            return {}