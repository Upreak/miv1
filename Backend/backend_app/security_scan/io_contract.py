"""
Security Scan Module - IO Contracts

Defines the data structures and contracts for the security scan module.
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class ScanStatus(str, Enum):
    """Enumeration of possible scan statuses."""
    SAFE = "SAFE"
    INFECTED = "INFECTED"
    ERROR = "ERROR"


class ScanRequest:
    """Request object for file scanning operations."""
    
    def __init__(self, file_id: str, file_path: str, mime_type: str):
        """
        Initialize a scan request.
        
        Args:
            file_id (str): Unique identifier for the file
            file_path (str): Path to the file to be scanned
            mime_type (str): MIME type of the file
        """
        self.file_id = file_id
        self.file_path = file_path
        self.mime_type = mime_type


class ScanResult:
    """Result object for file scanning operations."""
    
    def __init__(
        self,
        status: ScanStatus,
        details: Dict[str, Any],
        safe_path: Optional[str] = None,
        infected_path: Optional[str] = None
    ):
        """
        Initialize a scan result.
        
        Args:
            status (ScanStatus): The scan status (SAFE, INFECTED, ERROR)
            details (Dict[str, Any]): Detailed scan information
            safe_path (Optional[str]): Path to safe file (if status is SAFE)
            infected_path (Optional[str]): Path to infected file (if status is INFECTED)
        """
        self.status = status
        self.details = details
        self.safe_path = safe_path
        self.infected_path = infected_path
        self.timestamp = datetime.utcnow()


class VirusUpdateStatus:
    """Status object for virus database update operations."""
    
    def __init__(
        self,
        last_update: datetime,
        checksum_valid: bool,
        db_version: str
    ):
        """
        Initialize virus database update status.
        
        Args:
            last_update (datetime): Timestamp of last successful update
            checksum_valid (bool): Whether the database checksum is valid
            db_version (str): Current database version
        """
        self.last_update = last_update
        self.checksum_valid = checksum_valid
        self.db_version = db_version