"""
Security Scan Module - Configuration

Configuration and folder setup for the security scan module.
"""

import os
from pathlib import Path
from typing import Optional


class SecurityScanConfig:
    """Configuration class for security scan module."""
    
    def __init__(self):
        """Initialize configuration with default values."""
        # Base paths
        self.base_data_path = self._get_base_data_path()
        self.quarantine_base_path = os.path.join(self.base_data_path, "quarantine")
        self.virus_db_path = os.path.join(self.base_data_path, "virus_db")
        self.backup_db_path = os.path.join(self.base_data_path, "virus_db_backup")
        
        # Quarantine subfolders
        self.incoming_path = os.path.join(self.quarantine_base_path, "incoming")
        self.scanning_path = os.path.join(self.quarantine_base_path, "scanning")
        self.clean_path = os.path.join(self.quarantine_base_path, "clean")
        self.infected_path = os.path.join(self.quarantine_base_path, "infected")
        self.logs_path = os.path.join(self.quarantine_base_path, "logs")
        
        # ClamAV configuration
        self.clamav_socket = None  # None for localhost, or specify socket path
        self.clamav_timeout = 30  # seconds
        
        # Security settings
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_mime_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'application/zip',
            'application/x-rar-compressed'
        ]
        
        # Logging configuration
        self.log_level = "INFO"
        self.log_file = os.path.join(self.logs_path, "security_scan.log")
    
    def _get_base_data_path(self) -> str:
        """
        Get the base data path for the application.
        
        Returns:
            str: Base data path
        """
        # Try to get from environment variable first
        base_path = os.environ.get('SECURITY_SCAN_DATA_PATH')
        if base_path:
            return base_path
        
        # Default to data directory in project root
        project_root = self._get_project_root()
        default_path = os.path.join(project_root, "data")
        
        return default_path
    
    def _get_project_root(self) -> str:
        """
        Get the project root directory.
        
        Returns:
            str: Project root path
        """
        # Navigate up from this file's location to find project root
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        
        return str(project_root)
    
    def ensure_folder_structure(self) -> None:
        """
        Ensure all required folders exist and create them if necessary.
        """
        folders = [
            self.base_data_path,
            self.quarantine_base_path,
            self.virus_db_path,
            self.backup_db_path,
            self.incoming_path,
            self.scanning_path,
            self.clean_path,
            self.infected_path,
            self.logs_path
        ]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
    
    def get_quarantine_paths(self) -> dict:
        """
        Get all quarantine folder paths.
        
        Returns:
            dict: Dictionary of quarantine paths
        """
        return {
            'base': self.quarantine_base_path,
            'incoming': self.incoming_path,
            'scanning': self.scanning_path,
            'clean': self.clean_path,
            'infected': self.infected_path,
            'logs': self.logs_path
        }
    
    def get_virus_db_paths(self) -> dict:
        """
        Get virus database paths.
        
        Returns:
            dict: Dictionary of virus database paths
        """
        return {
            'db': self.virus_db_path,
            'backup': self.backup_db_path
        }
    
    @classmethod
    def create_default_config(cls) -> 'SecurityScanConfig':
        """
        Create a default configuration instance.
        
        Returns:
            SecurityScanConfig: Configured instance
        """
        config = cls()
        config.ensure_folder_structure()
        return config


# Default configuration instance
default_config = SecurityScanConfig.create_default_config()


def get_config() -> SecurityScanConfig:
    """
    Get the default configuration instance.
    
    Returns:
        SecurityScanConfig: Configuration instance
    """
    return default_config


# Environment-based configuration
def get_config_from_env() -> SecurityScanConfig:
    """
    Get configuration based on environment variables.
    
    Returns:
        SecurityScanConfig: Configuration instance
    """
    config = SecurityScanConfig()
    
    # Override with environment variables if present
    clamav_socket = os.environ.get('CLAMAV_SOCKET')
    if clamav_socket:
        config.clamav_socket = clamav_socket
    
    clamav_timeout = os.environ.get('CLAMAV_TIMEOUT')
    if clamav_timeout:
        try:
            config.clamav_timeout = int(clamav_timeout)
        except ValueError:
            pass
    
    max_file_size = os.environ.get('MAX_FILE_SIZE')
    if max_file_size:
        try:
            config.max_file_size = int(max_file_size)
        except ValueError:
            pass
    
    # Ensure folders exist
    config.ensure_folder_structure()
    
    return config