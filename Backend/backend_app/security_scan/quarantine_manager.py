"""
Security Scan Module - Quarantine Manager

Interface definitions for file quarantine and movement operations.
"""

from abc import ABC, abstractmethod
from typing import Optional
import os
import shutil
from datetime import datetime


class QuarantineManager(ABC):
    """Abstract base class for quarantine management operations."""
    
    @abstractmethod
    def move_to_incoming(self, file_bytes: bytes, original_filename: str) -> str:
        """
        Move file bytes to incoming folder with unique naming.
        
        Args:
            file_bytes (bytes): File content as bytes
            original_filename (str): Original filename
            
        Returns:
            str: Path to the saved file in incoming folder
        """
        pass
    
    @abstractmethod
    def move_to_scanning(self, file_path: str) -> str:
        """
        Move file to scanning folder.
        
        Args:
            file_path (str): Current file path
            
        Returns:
            str: Path to the file in scanning folder
        """
        pass
    
    @abstractmethod
    def mark_as_safe(self, scanning_path: str) -> str:
        """
        Mark file as safe and move to clean folder.
        
        Args:
            scanning_path (str): Current file path in scanning folder
            
        Returns:
            str: Path to the file in clean folder
        """
        pass
    
    @abstractmethod
    def mark_as_infected(self, scanning_path: str) -> str:
        """
        Mark file as infected and move to infected folder.
        
        Args:
            scanning_path (str): Current file path in scanning folder
            
        Returns:
            str: Path to the file in infected folder
        """
        pass
    
    @abstractmethod
    def ensure_folder_structure(self) -> None:
        """
        Ensure all required quarantine folders exist.
        Create them if they don't exist.
        """
        pass


class FileQuarantineManager(QuarantineManager):
    """Concrete implementation of QuarantineManager."""
    
    def __init__(self, base_quarantine_path: str):
        """
        Initialize quarantine manager.
        
        Args:
            base_quarantine_path (str): Base path for quarantine folders
        """
        self.base_path = base_quarantine_path
        self.incoming_path = os.path.join(base_quarantine_path, "incoming")
        self.scanning_path = os.path.join(base_quarantine_path, "scanning")
        self.clean_path = os.path.join(base_quarantine_path, "clean")
        self.infected_path = os.path.join(base_quarantine_path, "infected")
        self.logs_path = os.path.join(base_quarantine_path, "logs")
    
    def move_to_incoming(self, file_bytes: bytes, original_filename: str) -> str:
        """
        Move file bytes to incoming folder with unique naming.
        
        Args:
            file_bytes (bytes): File content as bytes
            original_filename (str): Original filename
            
        Returns:
            str: Path to the saved file in incoming folder
        """
        # Ensure folder exists
        os.makedirs(self.incoming_path, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"incoming_{timestamp}_{original_filename}{file_extension}"
        destination_path = os.path.join(self.incoming_path, unique_filename)
        
        # Save file bytes
        with open(destination_path, 'wb') as f:
            f.write(file_bytes)
        
        return destination_path
    
    def move_to_scanning(self, file_path: str) -> str:
        """
        Move file to scanning folder.
        
        Args:
            file_path (str): Current file path
            
        Returns:
            str: Path to the file in scanning folder
        """
        # Ensure folder exists
        os.makedirs(self.scanning_path, exist_ok=True)
        
        # Generate unique filename for scanning
        filename = os.path.basename(file_path)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        scanning_filename = f"scanning_{timestamp}_{filename}"
        destination_path = os.path.join(self.scanning_path, scanning_filename)
        
        # Move file
        shutil.move(file_path, destination_path)
        
        return destination_path
    
    def mark_as_safe(self, scanning_path: str) -> str:
        """
        Mark file as safe and move to clean folder.
        
        Args:
            scanning_path (str): Current file path in scanning folder
            
        Returns:
            str: Path to the file in clean folder
        """
        # Ensure folder exists
        os.makedirs(self.clean_path, exist_ok=True)
        
        # Generate clean filename
        filename = os.path.basename(scanning_path)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        clean_filename = f"clean_{timestamp}_{filename}"
        destination_path = os.path.join(self.clean_path, clean_filename)
        
        # Move file
        shutil.move(scanning_path, destination_path)
        
        return destination_path
    
    def mark_as_infected(self, scanning_path: str) -> str:
        """
        Mark file as infected and move to infected folder.
        
        Args:
            scanning_path (str): Current file path in scanning folder
            
        Returns:
            str: Path to the file in infected folder
        """
        # Ensure folder exists
        os.makedirs(self.infected_path, exist_ok=True)
        
        # Generate infected filename
        filename = os.path.basename(scanning_path)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        infected_filename = f"infected_{timestamp}_{filename}"
        destination_path = os.path.join(self.infected_path, infected_filename)
        
        # Move file
        shutil.move(scanning_path, destination_path)
        
        return destination_path
    
    def ensure_folder_structure(self) -> None:
        """
        Ensure all required quarantine folders exist.
        Create them if they don't exist.
        """
        folders = [
            self.base_path,
            self.incoming_path,
            self.scanning_path,
            self.clean_path,
            self.infected_path,
            self.logs_path
        ]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
    
    def get_log_path(self) -> str:
        """
        Get the path for quarantine operation logs.
        
        Returns:
            str: Path to the logs folder
        """
        return self.logs_path