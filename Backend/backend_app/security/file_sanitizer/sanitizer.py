"""
Text sanitizer - removes harmful patterns, HTML, JavaScript, and non-printable characters.
"""

import logging
import re
import html
import string
from typing import Optional

logger = logging.getLogger(__name__)

# Patterns to remove/escape
DANGEROUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',  # JavaScript
    r'<iframe[^>]*>.*?</iframe>',  # Iframes
    r'<object[^>]*>.*?</object>',  # Objects
    r'<embed[^>]*>.*?</embed>',    # Embeds
    r'<form[^>]*>.*?</form>',      # Forms
    r'<input[^>]*>',               # Input fields
    r'<button[^>]*>.*?</button>',  # Buttons
    r'javascript:',                # JavaScript URLs
    r'data:',                      # Data URLs
    r'vbscript:',                  # VBScript
    r'on\w+\s*=',                 # Event handlers (onclick, onload, etc.)
]

# HTML tags to preserve (safe subset)
ALLOWED_HTML_TAGS = {
    'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre'
}

def sanitize_text(text: str) -> str:
    """
    Sanitize text by removing harmful patterns and non-printable characters.
    
    Args:
        text: Raw text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    logger.debug(f"Sanitizing text with {len(text)} characters")
    
    # Step 1: Remove dangerous patterns
    sanitized = _remove_dangerous_patterns(text)
    
    # Step 2: Escape HTML entities
    sanitized = html.escape(sanitized, quote=False)
    
    # Step 3: Remove non-printable characters (except whitespace)
    sanitized = _remove_non_printable(sanitized)
    
    # Step 4: Normalize whitespace
    sanitized = _normalize_whitespace(sanitized)
    
    # Step 5: Remove excessive line breaks
    sanitized = _limit_line_breaks(sanitized)
    
    logger.debug(f"Sanitized text length: {len(sanitized)} characters")
    return sanitized

def _remove_dangerous_patterns(text: str) -> str:
    """Remove dangerous HTML/JavaScript patterns."""
    result = text
    
    for pattern in DANGEROUS_PATTERNS:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE | re.DOTALL)
    
    return result

def _remove_non_printable(text: str) -> str:
    """Remove non-printable characters."""
    # Keep printable ASCII, tabs, newlines, and common Unicode characters
    allowed_chars = set(string.printable + '\u2013\u2014\u2018\u2019\u201c\u201d\u2026')
    
    return ''.join(char for char in text if char in allowed_chars or ord(char) > 127)

def _normalize_whitespace(text: str) -> str:
    """Normalize whitespace characters."""
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple tabs with single tab
    text = re.sub(r'\t+', '\t', text)
    
    # Replace multiple newlines with single newline
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip()

def _limit_line_breaks(text: str) -> str:
    """Limit excessive line breaks."""
    # Replace 3+ consecutive newlines with 2 newlines
    return re.sub(r'\n{3,}', '\n\n', text)