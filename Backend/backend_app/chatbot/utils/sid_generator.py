"""
SID Generator for Chatbot/Co-Pilot Module

Generates and validates Session IDs (SIDs) for chatbot conversations.
"""

import uuid
import hashlib
import time
from typing import Optional
import re


class SIDGenerator:
    """
    Generates and validates Session IDs (SIDs) for chatbot conversations.
    
    SIDs are unique identifiers that track user conversations across platforms.
    Format: chatbot_<timestamp>_<random_hash>_<channel_prefix>
    """
    
    @staticmethod
    def generate_sid_for_user(user_id: str, channel: str, prefix: str = "chatbot") -> str:
        """
        Generate a SID for a specific user and channel.
        
        Args:
            user_id: User identifier
            channel: Platform channel (whatsapp/telegram/web)
            prefix: SID prefix
            
        Returns:
            str: Generated SID
        """
        # Generate timestamp
        timestamp = str(int(time.time()))
        
        # Generate random UUID
        random_uuid = str(uuid.uuid4())
        
        # Create hash of user_id and timestamp for uniqueness
        hash_input = f"{user_id}_{timestamp}_{random_uuid}"
        hash_obj = hashlib.md5(hash_input.encode())
        hash_hex = hash_obj.hexdigest()[:8]  # Use first 8 characters
        
        # Clean channel name
        clean_channel = re.sub(r'[^a-zA-Z0-9]', '_', channel.lower())
        
        # Format SID
        sid = f"{prefix}_{timestamp}_{hash_hex}_{clean_channel}"
        
        return sid
    
    @staticmethod
    def generate_temp_sid(prefix: str = "temp") -> str:
        """
        Generate a temporary SID for testing or special cases.
        
        Args:
            prefix: SID prefix
            
        Returns:
            str: Generated temporary SID
        """
        timestamp = str(int(time.time()))
        random_uuid = str(uuid.uuid4())[:8]
        
        sid = f"{prefix}_{timestamp}_{random_uuid}"
        
        return sid
    
    @staticmethod
    def validate_sid(sid: str) -> bool:
        """
        Validate SID format.
        
        Args:
            sid: SID to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not sid or not isinstance(sid, str):
            return False
        
        # Basic format check
        if not sid.startswith('chatbot_') and not sid.startswith('temp_'):
            return False
        
        # Check length
        if len(sid) < 20 or len(sid) > 100:
            return False
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9_\-]+$', sid):
            return False
        
        # Check timestamp component
        parts = sid.split('_')
        if len(parts) < 3:
            return False
        
        # Try to parse timestamp
        try:
            timestamp = int(parts[1])
            # Check if timestamp is reasonable (not too old or in the future)
            current_time = int(time.time())
            if timestamp < current_time - 365 * 24 * 3600:  # More than 1 year old
                return False
            if timestamp > current_time + 24 * 3600:  # More than 1 day in future
                return False
        except ValueError:
            return False
        
        return True
    
    @staticmethod
    def anonymize_sid(sid: str) -> str:
        """
        Anonymize SID for logging purposes.
        
        Args:
            sid: Original SID
            
        Returns:
            str: Anonymized SID
        """
        if not sid:
            return "unknown"
        
        # Keep prefix and timestamp, anonymize the hash
        parts = sid.split('_')
        if len(parts) >= 3:
            parts[2] = '****'  # Replace hash with asterisks
            return '_'.join(parts)
        
        return f"****_{sid}"
    
    @staticmethod
    def extract_channel_from_sid(sid: str) -> Optional[str]:
        """
        Extract channel information from SID.
        
        Args:
            sid: SID to extract from
            
        Returns:
            Optional[str]: Channel name if found, None otherwise
        """
        if not sid:
            return None
        
        parts = sid.split('_')
        if len(parts) >= 4:
            return parts[3]
        
        return None
    
    @staticmethod
    def extract_timestamp_from_sid(sid: str) -> Optional[int]:
        """
        Extract timestamp from SID.
        
        Args:
            sid: SID to extract from
            
        Returns:
            Optional[int]: Timestamp if found, None otherwise
        """
        if not sid:
            return None
        
        parts = sid.split('_')
        if len(parts) >= 2:
            try:
                return int(parts[1])
            except ValueError:
                return None
        
        return None
    
    @staticmethod
    def is_sid_expired(sid: str, max_age_seconds: int = 30 * 24 * 3600) -> bool:
        """
        Check if SID has expired.
        
        Args:
            sid: SID to check
            max_age_seconds: Maximum age in seconds
            
        Returns:
            bool: True if expired, False otherwise
        """
        if not sid:
            return True
        
        timestamp = SIDGenerator.extract_timestamp_from_sid(sid)
        if not timestamp:
            return True
        
        current_time = int(time.time())
        return (current_time - timestamp) > max_age_seconds
    
    @staticmethod
    def generate_sid_batch(user_ids: list, channel: str, prefix: str = "chatbot") -> list:
        """
        Generate multiple SIDs for a list of users.
        
        Args:
            user_ids: List of user IDs
            channel: Platform channel
            prefix: SID prefix
            
        Returns:
            list: List of generated SIDs
        """
        sids = []
        for user_id in user_ids:
            sid = SIDGenerator.generate_sid_for_user(user_id, channel, prefix)
            sids.append(sid)
        
        return sids
    
    @staticmethod
    def create_sid_hash(sid: str) -> str:
        """
        Create a hash of SID for database indexing.
        
        Args:
            sid: Original SID
            
        Returns:
            str: Hashed SID
        """
        if not sid:
            return ""
        
        hash_obj = hashlib.sha256(sid.encode())
        return hash_obj.hexdigest()
    
    @staticmethod
    def format_sid_for_display(sid: str) -> str:
        """
        Format SID for display purposes.
        
        Args:
            sid: Original SID
            
        Returns:
            str: Formatted SID
        """
        if not sid:
            return "Unknown"
        
        # Extract channel and timestamp
        channel = SIDGenerator.extract_channel_from_sid(sid)
        timestamp = SIDGenerator.extract_timestamp_from_sid(sid)
        
        if timestamp:
            # Convert timestamp to readable format
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp)
            formatted_time = dt.strftime('%Y-%m-%d %H:%M')
            
            if channel:
                return f"Session ({channel}) - {formatted_time}"
            else:
                return f"Session - {formatted_time}"
        
        return sid
    
    @staticmethod
    def get_sid_info(sid: str) -> dict:
        """
        Extract information from SID.
        
        Args:
            sid: SID to analyze
            
        Returns:
            dict: SID information
        """
        if not sid:
            return {'valid': False}
        
        info = {
            'valid': True,
            'original': sid,
            'anonymized': SIDGenerator.anonymize_sid(sid),
            'channel': SIDGenerator.extract_channel_from_sid(sid),
            'timestamp': SIDGenerator.extract_timestamp_from_sid(sid),
            'expired': SIDGenerator.is_sid_expired(sid),
            'hash': SIDGenerator.create_sid_hash(sid)
        }
        
        # Format timestamp if available
        if info['timestamp']:
            from datetime import datetime
            dt = datetime.fromtimestamp(info['timestamp'])
            info['formatted_time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
        
        return info
    
    @staticmethod
    def validate_sid_batch(sids: list) -> dict:
        """
        Validate a batch of SIDs.
        
        Args:
            sids: List of SIDs to validate
            
        Returns:
            dict: Validation results
        """
        results = {
            'total': len(sids),
            'valid': 0,
            'invalid': 0,
            'expired': 0,
            'channels': {},
            'details': []
        }
        
        for sid in sids:
            info = SIDGenerator.get_sid_info(sid)
            
            if not info['valid']:
                results['invalid'] += 1
            else:
                results['valid'] += 1
                
                if info['expired']:
                    results['expired'] += 1
                
                # Track channels
                channel = info['channel']
                if channel:
                    results['channels'][channel] = results['channels'].get(channel, 0) + 1
            
            results['details'].append(info)
        
        return results
    
    @staticmethod
    def generate_sid_with_metadata(user_id: str, channel: str, metadata: dict = None) -> str:
        """
        Generate SID with embedded metadata.
        
        Args:
            user_id: User identifier
            channel: Platform channel
            metadata: Additional metadata to embed
            
        Returns:
            str: SID with metadata
        """
        # Generate base SID
        base_sid = SIDGenerator.generate_sid_for_user(user_id, channel)
        
        # Add metadata if provided
        if metadata:
            # Create metadata hash
            import json
            metadata_str = json.dumps(metadata, sort_keys=True)
            metadata_hash = hashlib.md5(metadata_str.encode()).hexdigest()[:6]
            
            # Append to SID
            sid_with_metadata = f"{base_sid}_{metadata_hash}"
            return sid_with_metadata
        
        return base_sid
    
    @staticmethod
    def extract_metadata_from_sid(sid: str) -> dict:
        """
        Extract metadata from SID (if embedded).
        
        Args:
            sid: SID with potential metadata
            
        Returns:
            dict: Extracted metadata or empty dict
        """
        if not sid:
            return {}
        
        # Check if SID has metadata component
        parts = sid.split('_')
        if len(parts) >= 5:
            # The last part might be metadata hash
            metadata_hash = parts[-1]
            
            # Try to find corresponding metadata (this would require a metadata store)
            # For now, return basic info
            return {
                'has_metadata': True,
                'metadata_hash': metadata_hash,
                'channel': SIDGenerator.extract_channel_from_sid(sid),
                'timestamp': SIDGenerator.extract_timestamp_from_sid(sid)
            }
        
        return {
            'has_metadata': False,
            'channel': SIDGenerator.extract_channel_from_sid(sid),
            'timestamp': SIDGenerator.extract_timestamp_from_sid(sid)
        }