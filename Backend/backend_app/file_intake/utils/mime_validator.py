"""
MIME Validator - Validates file types using magic bytes and file extensions.

This utility provides robust file type validation using:
- Magic bytes (file signature) detection
- File extension validation
- MIME type mapping
- Security checks for potentially dangerous file types
"""

import os
import mimetypes
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path


# MIME type to file extension mapping
MIME_TO_EXTENSIONS = {
    'application/pdf': ['.pdf'],
    'application/msword': ['.doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'application/vnd.ms-excel': ['.xls'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'application/vnd.ms-powerpoint': ['.ppt'],
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
    'text/plain': ['.txt', '.text'],
    'text/csv': ['.csv'],
    'application/json': ['.json'],
    'application/xml': ['.xml'],
    'text/html': ['.html', '.htm'],
    'text/css': ['.css'],
    'application/javascript': ['.js'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/gif': ['.gif'],
    'image/webp': ['.webp'],
    'image/svg+xml': ['.svg'],
    'image/tiff': ['.tiff', '.tif'],
    'image/bmp': ['.bmp'],
    'application/zip': ['.zip'],
    'application/x-rar-compressed': ['.rar'],
    'application/x-7z-compressed': ['.7z'],
    'application/x-tar': ['.tar'],
    'application/gzip': ['.gz'],
    'application/x-rpm': ['.rpm'],
    'application/x-debian-package': ['.deb'],
    'application/x-apple-diskimage': ['.dmg'],
    'application/x-executable': ['.exe'],
    'application/x-sharedlib': ['.so'],
    'application/x-object': ['.o'],
    'application/x-pie-executable': ['.out'],
    'application/x-mach-binary': ['.macho'],
    'application/x-java-archive': ['.jar'],
    'application/x-java-applet': ['.class'],
    'application/x-shockwave-flash': ['.swf'],
    'video/mp4': ['.mp4'],
    'video/mpeg': ['.mpeg', '.mpg'],
    'video/quicktime': ['.mov'],
    'video/x-msvideo': ['.avi'],
    'video/x-ms-wmv': ['.wmv'],
    'video/x-flv': ['.flv'],
    'audio/mpeg': ['.mp3'],
    'audio/wav': ['.wav'],
    'audio/ogg': ['.ogg'],
    'audio/x-ms-wma': ['.wma'],
    'audio/x-aiff': ['.aiff'],
    'audio/x-au': ['.au'],
    'application/x-font-ttf': ['.ttf'],
    'application/x-font-otf': ['.otf'],
    'application/x-font-type1': ['.pfa', '.pfb'],
    'font/woff': ['.woff'],
    'font/woff2': ['.woff2'],
    'application/x-font-woff': ['.woff'],
    'application/vnd.ms-fontobject': ['.eot'],
}

# Dangerous file types that should be blocked
DANGEROUS_FILE_TYPES = {
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
    '.app', '.deb', '.pkg', '.dmg', '.rpm', '.msi', '.msp', '.mst',
    '.ps1', '.psm1', '.psd1', '.reg', '.inf', '.lnk', '.scf', '.shs',
    '.hta', '.cpl', '.msc', '.jse', '.wsh', '.msh', '.wsf', '.wsc',
    '.wsh', '.ws', '.ps1xml', '.psc1', '.osd', '.msi', '.msp', '.mst',
    '.ps2', '.ps2xml', '.psc2', '.pssc', '.pfx', '.cer', '.crt', '.der',
    '.p7b', '.p7c', '.p12', '.pfx', '.pem', '.sddl', '.acm', '.ade', '.adp',
    '.bas', '.chm', '.cmd', '.com', '.cpl', '.crt', '.dll', '.exe', '.fxp',
    '.hlp', '.hta', '.inf', '.ins', '.isp', '.js', '.jse', '.lnk', '.mad',
    '.maf', '.mag', '.mam', '.maq', '.mar', '.mas', '.mat', '.mau', '.mav',
    '.maw', '.mbx', '.mde', '.mdt', '.mdw', '.mdz', '.mim', '.msc', '.msi',
    '.msp', '.mst', '.ocx', '.ops', '.pcd', '.pif', '.prf', '.prg', '.pst',
    '.reg', '.scf', '.scr', '.sct', '.shb', '.shs', '.url', '.vb', '.vbe',
    '.vbs', '.wsc', '.wsf', '.wsh', '.xbap', '.xll', '.xlm', '.xls', '.xlt',
    '.xlw', '.xsn', '.xtp', '.xla', '.xlam', '.xll', '.xlm', '.xls', '.xlt',
    '.xlsm', '.xlsx', '.xltm', '.xltx', '.xlam', '.xll', '.xlm', '.xls',
    '.xlt', '.xlsm', '.xlsx', '.xltm', '.xltx', '.xlam'
}

# Suspicious file extensions that should be flagged
SUSPICIOUS_EXTENSIONS = {
    '.php', '.asp', '.jsp', '.cgi', '.pl', '.py', '.rb', '.go', '.rs',
    '.swift', '.kt', '.scala', '.r', '.m', '.f90', '.f95', '.f03',
    '.f08', '.f', '.for', '.f77', '.f90', '.f95', '.f03', '.f08',
    '.f', '.for', '.f77', '.php3', '.php4', '.php5', '.phtml', '.shtml',
    '.pl', '.py', '.rb', '.cgi', '.sh', '.bash', '.zsh', '.fish',
    '.ps1', '.bat', '.cmd', '.vbs', '.js', '.ts', '.coffee', '.litcoffee'
}


class MIMEValidator:
    """MIME type and file extension validator."""
    
    def __init__(self):
        self.allowed_mime_types: Set[str] = set()
        self.allowed_extensions: Set[str] = set()
        self.blocked_extensions: Set[str] = DANGEROUS_FILE_TYPES.union(SUSPICIOUS_EXTENSIONS)
        self._load_allowed_types()
    
    def _load_allowed_types(self):
        """Load allowed MIME types and extensions from configuration."""
        # Default allowed types (can be overridden by config)
        default_allowed = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'text/csv',
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp',
            'image/svg+xml',
            'image/tiff',
            'image/bmp',
            'application/zip',
            'application/x-rar-compressed',
            'application/x-7z-compressed',
            'application/x-tar',
            'application/gzip',
            'video/mp4',
            'video/mpeg',
            'video/quicktime',
            'video/x-msvideo',
            'video/x-ms-wmv',
            'video/x-flv',
            'audio/mpeg',
            'audio/wav',
            'audio/ogg',
            'audio/x-ms-wma',
            'audio/x-aiff',
            'audio/x-au',
            'application/x-font-ttf',
            'application/x-font-otf',
            'application/x-font-type1',
            'font/woff',
            'font/woff2',
            'application/vnd.ms-fontobject',
        ]
        
        self.allowed_mime_types = set(default_allowed)
        
        # Build allowed extensions from MIME types
        for mime_type in self.allowed_mime_types:
            if mime_type in MIME_TO_EXTENSIONS:
                self.allowed_extensions.update(MIME_TO_EXTENSIONS[mime_type])
    
    def set_allowed_types(self, mime_types: List[str], extensions: List[str]):
        """Set allowed MIME types and extensions."""
        self.allowed_mime_types = set(mime_types)
        self.allowed_extensions = set(extensions)
    
    def is_mime_type_allowed(self, mime_type: str) -> bool:
        """Check if MIME type is allowed."""
        return mime_type.lower() in self.allowed_mime_types
    
    def is_extension_allowed(self, extension: str) -> bool:
        """Check if file extension is allowed."""
        return extension.lower() in self.allowed_extensions
    
    def is_extension_blocked(self, extension: str) -> bool:
        """Check if file extension is blocked."""
        return extension.lower() in self.blocked_extensions
    
    def is_extension_suspicious(self, extension: str) -> bool:
        """Check if file extension is suspicious."""
        return extension.lower() in SUSPICIOUS_EXTENSIONS
    
    def detect_mime_type(self, file_path: str) -> Optional[str]:
        """Detect MIME type from file path."""
        try:
            # Use mimetypes to guess
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                return mime_type.lower()
            
            # Fallback to file extension
            extension = Path(file_path).suffix.lower()
            if extension in MIME_TO_EXTENSIONS:
                for mime, exts in MIME_TO_EXTENSIONS.items():
                    if extension in exts:
                        return mime
            
            return None
            
        except Exception:
            return None
    
    def validate_file_type(self, file_path: str, filename: str) -> Tuple[bool, str, str]:
        """
        Validate file type using magic bytes and extension.
        
        Args:
            file_path: Path to the file
            filename: Original filename
            
        Returns:
            Tuple of (is_valid, mime_type, extension)
        """
        try:
            # Extract extension from filename
            extension = Path(filename).suffix.lower()
            
            # Check if extension is blocked
            if self.is_extension_blocked(extension):
                return False, f"Blocked file extension: {extension}", extension
            
            # Check if extension is suspicious
            if self.is_extension_suspicious(extension):
                return False, f"Suspicious file extension: {extension}", extension
            
            # Check if extension is allowed
            if not self.is_extension_allowed(extension):
                return False, f"File extension not allowed: {extension}", extension
            
            # Detect MIME type
            mime_type = self.detect_mime_type(file_path)
            if not mime_type:
                return False, "Could not detect file type", extension
            
            # Check if MIME type is allowed
            if not self.is_mime_type_allowed(mime_type):
                return False, f"MIME type not allowed: {mime_type}", extension
            
            # Validate magic bytes for critical file types
            if not self._validate_magic_bytes(file_path, mime_type):
                return False, f"File signature does not match {mime_type}", extension
            
            return True, mime_type, extension
            
        except Exception as e:
            return False, f"File validation error: {str(e)}", extension
    
    def _validate_magic_bytes(self, file_path: str, expected_mime: str) -> bool:
        """Validate file magic bytes against expected MIME type."""
        try:
            # Magic bytes validation for common file types
            magic_bytes_map = {
                'application/pdf': b'%PDF',
                'application/msword': b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': b'PK\x03\x04',
                'text/plain': b'',  # Text files don't have magic bytes
                'image/jpeg': b'\xFF\xD8\xFF',
                'image/png': b'\x89PNG\r\n\x1A\n',
                'image/gif': b'GIF87a' or b'GIF89a',
                'image/webp': b'RIFF',
                'image/svg+xml': b'<?xml',
                'application/zip': b'PK\x03\x04',
                'application/x-rar-compressed': b'Rar!\x1a\x07',
                'application/x-7z-compressed': b'7z\xbc\xaf\x27\x1c',
                'application/x-tar': b'ustar',
                'application/gzip': b'\x1f\x8b',
                'video/mp4': b'ftyp',
                'video/mpeg': b'\x00\x00\x01\xB3',
                'audio/mpeg': b'ID3',
                'application/x-font-ttf': b'\x00\x01\x00\x00',
                'application/vnd.ms-fontobject': b'OTTO',
            }
            
            if expected_mime not in magic_bytes_map:
                return True  # No magic bytes validation required
            
            expected_magic = magic_bytes_map[expected_mime]
            
            if not expected_magic:
                return True  # No magic bytes to validate
            
            with open(file_path, 'rb') as f:
                file_bytes = f.read(len(expected_magic))
                
            return file_bytes == expected_magic
            
        except Exception:
            return False  # If we can't validate, assume it's invalid
    
    def get_allowed_mime_types(self) -> List[str]:
        """Get list of allowed MIME types."""
        return list(self.allowed_mime_types)
    
    def get_allowed_extensions(self) -> List[str]:
        """Get list of allowed extensions."""
        return list(self.allowed_extensions)
    
    def get_blocked_extensions(self) -> List[str]:
        """Get list of blocked extensions."""
        return list(self.blocked_extensions)
    
    def get_suspicious_extensions(self) -> List[str]:
        """Get list of suspicious extensions."""
        return list(SUSPICIOUS_EXTENSIONS)


# Global validator instance
validator = MIMEValidator()


def validate_file_mime_type(file_path: str, filename: str) -> Tuple[bool, str, str]:
    """
    Validate file MIME type and extension.
    
    Args:
        file_path: Path to the file
        filename: Original filename
        
    Returns:
        Tuple of (is_valid, message, extension)
    """
    return validator.validate_file_type(file_path, filename)


def is_file_type_allowed(filename: str) -> bool:
    """
    Check if file type is allowed based on extension.
    
    Args:
        filename: Filename to check
        
    Returns:
        bool: True if allowed, False otherwise
    """
    extension = Path(filename).suffix.lower()
    return validator.is_extension_allowed(extension)


def get_file_mime_type(file_path: str) -> Optional[str]:
    """
    Get MIME type from file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: MIME type or None if undetectable
    """
    return validator.detect_mime_type(file_path)