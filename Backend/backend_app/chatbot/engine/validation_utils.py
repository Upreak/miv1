"""
Validation utilities for chatbot webhook handlers.
"""
import re
from typing import Optional

def validate_email(email: str) -> bool:
    """
    Validate email format using regex.
    
    Args:
        email: Email address to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validate_phone(phone: str) -> bool:
    """
    Validate phone number (supports various formats).
    
    Args:
        phone: Phone number to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it's 10-15 digits
    if cleaned.isdigit() and 10 <= len(cleaned) <= 15:
        return True
    
    return False

def sanitize_phone(phone: str) -> str:
    """
    Sanitize phone number to standard format.
    
    Args:
        phone: Phone number to sanitize
    
    Returns:
        str: Sanitized phone number (digits only)
    """
    if not phone:
        return ""
    
    # Remove all non-digit characters
    return re.sub(r'\D', '', phone)

def format_indian_phone(phone: str) -> Optional[str]:
    """
    Format Indian phone number to +91-XXXXXXXXXX format.
    
    Args:
        phone: Phone number to format
    
    Returns:
        Optional[str]: Formatted phone or None if invalid
    """
    cleaned = sanitize_phone(phone)
    
    # Indian phone numbers are 10 digits
    if len(cleaned) == 10:
        return f"+91-{cleaned}"
    elif len(cleaned) == 12 and cleaned.startswith('91'):
        return f"+{cleaned[:2]}-{cleaned[2:]}"
    
    return None
