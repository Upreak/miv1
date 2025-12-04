"""
File Hasher - Calculates file hashes for integrity verification and deduplication.

This utility provides:
- SHA256 hash calculation
- MD5 hash calculation (for legacy systems)
- File integrity verification
- Hash comparison utilities
- Progress tracking for large files
"""

import hashlib
import os
from typing import Optional, Dict, Tuple, BinaryIO
from pathlib import Path


class FileHasher:
    """File hashing utility for integrity verification and deduplication."""
    
    def __init__(self, algorithm: str = 'sha256'):
        """
        Initialize file hasher.
        
        Args:
            algorithm: Hash algorithm to use ('sha256', 'md5', 'sha1', 'sha512')
        """
        self.algorithm = algorithm.lower()
        self.supported_algorithms = {
            'sha256': hashlib.sha256,
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha512': hashlib.sha512,
            'sha384': hashlib.sha384,
            'sha224': hashlib.sha224,
        }
        
        if self.algorithm not in self.supported_algorithms:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    def calculate_hash(self, file_path: str, chunk_size: int = 8192) -> str:
        """
        Calculate hash of a file.
        
        Args:
            file_path: Path to the file
            chunk_size: Size of chunks to read (default: 8KB)
            
        Returns:
            str: Hexadecimal hash string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
            ValueError: If algorithm is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not os.path.isfile(file_path):
            raise IOError(f"Path is not a file: {file_path}")
        
        hash_func = self.supported_algorithms[self.algorithm]()
        
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
            
        except IOError as e:
            raise IOError(f"Failed to read file {file_path}: {str(e)}")
    
    def calculate_hash_from_bytes(self, data: bytes) -> str:
        """
        Calculate hash from bytes data.
        
        Args:
            data: Bytes data to hash
            
        Returns:
            str: Hexadecimal hash string
        """
        hash_func = self.supported_algorithms[self.algorithm]()
        hash_func.update(data)
        return hash_func.hexdigest()
    
    def calculate_hash_from_file_object(self, file_obj: BinaryIO, chunk_size: int = 8192) -> str:
        """
        Calculate hash from a file object.
        
        Args:
            file_obj: File object to hash
            chunk_size: Size of chunks to read (default: 8KB)
            
        Returns:
            str: Hexadecimal hash string
        """
        hash_func = self.supported_algorithms[self.algorithm]()
        
        # Save current position
        current_pos = file_obj.tell()
        
        try:
            # Reset to beginning
            file_obj.seek(0)
            
            while chunk := file_obj.read(chunk_size):
                hash_func.update(chunk)
            
            return hash_func.hexdigest()
            
        finally:
            # Restore original position
            file_obj.seek(current_pos)
    
    def verify_hash(self, file_path: str, expected_hash: str) -> bool:
        """
        Verify file hash against expected hash.
        
        Args:
            file_path: Path to the file
            expected_hash: Expected hash value
            
        Returns:
            bool: True if hash matches, False otherwise
        """
        try:
            actual_hash = self.calculate_hash(file_path)
            return actual_hash.lower() == expected_hash.lower()
        except Exception:
            return False
    
    def verify_hash_from_bytes(self, data: bytes, expected_hash: str) -> bool:
        """
        Verify hash from bytes data against expected hash.
        
        Args:
            data: Bytes data to verify
            expected_hash: Expected hash value
            
        Returns:
            bool: True if hash matches, False otherwise
        """
        try:
            actual_hash = self.calculate_hash_from_bytes(data)
            return actual_hash.lower() == expected_hash.lower()
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Dict:
        """
        Get file information including hash, size, and metadata.
        
        Args:
            file_path: Path to the file
            
        Returns:
            dict: File information dictionary
        """
        try:
            stat = os.stat(file_path)
            file_hash = self.calculate_hash(file_path)
            
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'file_size': stat.st_size,
                'file_hash': file_hash,
                'algorithm': self.algorithm,
                'created_at': stat.st_ctime,
                'modified_at': stat.st_mtime,
                'accessed_at': stat.st_atime,
                'is_file': os.path.isfile(file_path),
                'is_directory': os.path.isdir(file_path),
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK),
                'is_executable': os.access(file_path, os.X_OK),
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'success': False
            }
    
    def compare_files(self, file1_path: str, file2_path: str) -> Dict:
        """
        Compare two files by hash and size.
        
        Args:
            file1_path: Path to first file
            file2_path: Path to second file
            
        Returns:
            dict: Comparison results
        """
        try:
            # Get file sizes
            size1 = os.path.getsize(file1_path)
            size2 = os.path.getsize(file2_path)
            
            # If sizes are different, files are different
            if size1 != size2:
                return {
                    'files_match': False,
                    'reason': 'different_sizes',
                    'file1_size': size1,
                    'file2_size': size2,
                    'file1_hash': None,
                    'file2_hash': None
                }
            
            # Calculate hashes
            hash1 = self.calculate_hash(file1_path)
            hash2 = self.calculate_hash(file2_path)
            
            return {
                'files_match': hash1 == hash2,
                'reason': 'hash_comparison',
                'file1_size': size1,
                'file2_size': size2,
                'file1_hash': hash1,
                'file2_hash': hash2,
                'algorithm': self.algorithm
            }
            
        except Exception as e:
            return {
                'files_match': False,
                'reason': 'error',
                'error': str(e),
                'file1_hash': None,
                'file2_hash': None
            }
    
    def batch_hash_files(self, file_paths: list, progress_callback=None) -> Dict[str, str]:
        """
        Calculate hashes for multiple files.
        
        Args:
            file_paths: List of file paths
            progress_callback: Optional callback function for progress updates
            
        Returns:
            dict: Mapping of file paths to hashes
        """
        results = {}
        total_files = len(file_paths)
        
        for i, file_path in enumerate(file_paths):
            try:
                file_hash = self.calculate_hash(file_path)
                results[file_path] = file_hash
                
                if progress_callback:
                    progress = (i + 1) / total_files * 100
                    progress_callback(file_path, progress, i + 1, total_files)
                    
            except Exception as e:
                results[file_path] = f"ERROR: {str(e)}"
        
        return results
    
    def find_duplicate_files(self, directory: str, recursive: bool = True) -> Dict[str, list]:
        """
        Find duplicate files in a directory.
        
        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories
            
        Returns:
            dict: Mapping of hash values to lists of file paths
        """
        duplicates = {}
        file_hashes = {}
        
        # Walk directory
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_hash = self.calculate_hash(file_path)
                        if file_hash not in file_hashes:
                            file_hashes[file_hash] = []
                        file_hashes[file_hash].append(file_path)
                    except Exception:
                        continue
        else:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    try:
                        file_hash = self.calculate_hash(file_path)
                        if file_hash not in file_hashes:
                            file_hashes[file_hash] = []
                        file_hashes[file_hash].append(file_path)
                    except Exception:
                        continue
        
        # Filter for duplicates (files with same hash)
        for hash_value, files in file_hashes.items():
            if len(files) > 1:
                duplicates[hash_value] = files
        
        return duplicates
    
    def hash_progressive(self, file_path: str, progress_callback=None) -> str:
        """
        Calculate hash with progress tracking.
        
        Args:
            file_path: Path to the file
            progress_callback: Callback function for progress updates
            
        Returns:
            str: Hexadecimal hash string
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size = os.path.getsize(file_path)
        hash_func = self.supported_algorithms[self.algorithm]()
        
        try:
            with open(file_path, 'rb') as f:
                bytes_read = 0
                while chunk := f.read(8192):
                    hash_func.update(chunk)
                    bytes_read += len(chunk)
                    
                    if progress_callback:
                        progress = (bytes_read / file_size) * 100
                        progress_callback(file_path, progress, bytes_read, file_size)
            
            return hash_func.hexdigest()
            
        except IOError as e:
            raise IOError(f"Failed to read file {file_path}: {str(e)}")


# Global hasher instances
sha256_hasher = FileHasher('sha256')
md5_hasher = FileHasher('md5')


def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Calculate file hash using specified algorithm.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use
        
    Returns:
        str: Hexadecimal hash string
    """
    hasher = FileHasher(algorithm)
    return hasher.calculate_hash(file_path)


def verify_file_integrity(file_path: str, expected_hash: str, algorithm: str = 'sha256') -> bool:
    """
    Verify file integrity against expected hash.
    
    Args:
        file_path: Path to the file
        expected_hash: Expected hash value
        algorithm: Hash algorithm to use
        
    Returns:
        bool: True if hash matches, False otherwise
    """
    hasher = FileHasher(algorithm)
    return hasher.verify_hash(file_path, expected_hash)


def get_file_hash_info(file_path: str, algorithm: str = 'sha256') -> Dict:
    """
    Get comprehensive file information including hash.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use
        
    Returns:
        dict: File information dictionary
    """
    hasher = FileHasher(algorithm)
    return hasher.get_file_info(file_path)