"""
SID Generator - Generates unique Session ID identifiers for file intake sessions.

SID (Session ID) is a unique identifier for file intake sessions that serves as:
- Session tracking identifier
- Database primary key for sessions
- Reference for multiple file uploads within a session

Format: SID-UUID8
Example: SID-a1b2c3d4-e5f6-7890-1234-567890abcdef
"""

import uuid
from datetime import datetime
import re
from typing import Optional


def generate_sid() -> str:
    """
    Generate a unique SID identifier.
    
    Format: SID-UUID8
    
    Returns:
        str: Generated SID
        
    Raises:
        RuntimeError: If SID generation fails
    """
    try:
        # Generate UUID
        session_uuid = uuid.uuid4()
        
        # Construct SID
        sid = f"SID-{session_uuid}"
        
        return sid
        
    except Exception as e:
        raise RuntimeError(f"Failed to generate SID: {str(e)}")


def validate_sid_format(sid: str) -> bool:
    """
    Validate SID format.
    
    Args:
        sid: SID string to validate
        
    Returns:
        bool: True if valid format, False otherwise
    """
    if not sid or not isinstance(sid, str):
        return False
    
    # SID format: SID-UUID
    pattern = r'^SID-[a-f0-9-]{36}$'
    
    return bool(re.match(pattern, sid))


def extract_uuid_from_sid(sid: str) -> Optional[str]:
    """
    Extract UUID from SID.
    
    Args:
        sid: SID string
        
    Returns:
        str: Extracted UUID or None if invalid
    """
    if not validate_sid_format(sid):
        return None
    
    try:
        # Extract UUID part (after SID-)
        uuid_part = sid.split('-')[1]
        return uuid_part
    except (IndexError, ValueError):
        return None


def generate_sid_for_user(user_id: str) -> str:
    """
    Generate a unique SID for a specific user.
    
    Args:
        user_id: User identifier
        
    Returns:
        str: Generated SID
        
    Raises:
        ValueError: If user_id is invalid
        RuntimeError: If generation fails
    """
    if not user_id or not isinstance(user_id, str):
        raise ValueError("User ID must be a non-empty string")
    
    try:
        # Generate UUID with user context
        session_uuid = uuid.uuid5(uuid.NAMESPACE_URL, f"session-{user_id}-{datetime.utcnow().isoformat()}")
        
        # Construct SID
        sid = f"SID-{session_uuid}"
        
        return sid
        
    except Exception as e:
        raise RuntimeError(f"Failed to generate SID for user {user_id}: {str(e)}")


def generate_sid_batch(count: int) -> list:
    """
    Generate a batch of unique SIDs.
    
    Args:
        count: Number of SIDs to generate
        
    Returns:
        list: List of generated SIDs
        
    Raises:
        ValueError: If count is less than 1
        RuntimeError: If generation fails
    """
    if count < 1:
        raise ValueError("Count must be at least 1")
    
    sids = []
    for _ in range(count):
        sids.append(generate_sid())
    
    return sids


def sid_to_dict(sid: str) -> dict:
    """
    Convert SID to structured dictionary.
    
    Args:
        sid: SID string
        
    Returns:
        dict: Structured SID information
        
    Example:
        {
            "sid": "SID-a1b2c3d4-e5f6-7890-1234-567890abcdef",
            "prefix": "SID",
            "uuid": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
            "is_valid": True
        }
    """
    result = {
        "sid": sid,
        "prefix": None,
        "uuid": None,
        "is_valid": False
    }
    
    if not validate_sid_format(sid):
        return result
    
    try:
        parts = sid.split('-', 1)  # Split only on first dash
        result["prefix"] = parts[0]
        result["uuid"] = parts[1]
        result["is_valid"] = True
        
    except Exception:
        pass
    
    return result


def is_sid_valid_for_user(sid: str, user_id: str) -> bool:
    """
    Check if SID was generated for a specific user.
    
    Args:
        sid: SID string
        user_id: User identifier
        
    Returns:
        bool: True if SID belongs to user, False otherwise
    """
    if not validate_sid_format(sid) or not user_id:
        return False
    
    try:
        # Extract UUID from SID
        sid_uuid_str = extract_uuid_from_sid(sid)
        if not sid_uuid_str:
            return False
        
        # Generate expected UUID for user
        expected_uuid = uuid.uuid5(uuid.NAMESPACE_URL, f"session-{user_id}-{datetime.utcnow().isoformat()}")
        
        # Compare UUIDs
        return sid_uuid_str == str(expected_uuid)
        
    except Exception:
        return False


def generate_short_sid() -> str:
    """
    Generate a short SID (8 characters).
    
    Format: SID-8CHAR
    
    Returns:
        str: Generated short SID
    """
    try:
        # Generate short UUID (first 8 characters)
        short_uuid = uuid.uuid4().hex[:8]
        
        # Construct short SID
        sid = f"SID-{short_uuid}"
        
        return sid
        
    except Exception as e:
        raise RuntimeError(f"Failed to generate short SID: {str(e)}")


def validate_short_sid_format(sid: str) -> bool:
    """
    Validate short SID format.
    
    Args:
        sid: Short SID string to validate
        
    Returns:
        bool: True if valid format, False otherwise
    """
    if not sid or not isinstance(sid, str):
        return False
    
    # Short SID format: SID-8CHAR
    pattern = r'^SID-[a-f0-9]{8}$'
    
    return bool(re.match(pattern, sid))