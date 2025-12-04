"""
Logging Utilities - Enhanced logging for file intake operations.

This module provides:
- Structured logging for file intake operations
- Request correlation tracking
- Performance monitoring
- Error tracking and alerting
- Audit logging
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import os


class FileIntakeLogger:
    """Enhanced logger for file intake operations."""
    
    def __init__(self, name: str = "file_intake", log_level: str = "INFO"):
        """
        Initialize file intake logger.
        
        Args:
            name: Logger name
            log_level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / "file_intake.log")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.FileHandler(log_dir / "file_intake_errors.log")
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        self.logger.addHandler(error_handler)
        
        # Audit file handler
        audit_handler = logging.FileHandler(log_dir / "file_intake_audit.log")
        audit_handler.setFormatter(formatter)
        audit_handler.setLevel(logging.INFO)
        self.logger.addHandler(audit_handler)
        
        self.request_id = None
        self.session_id = None
        self.user_id = None
    
    def set_request_context(self, request_id: str = None, session_id: str = None, user_id: str = None):
        """
        Set request context for logging.
        
        Args:
            request_id: Request identifier
            session_id: Session identifier
            user_id: User identifier
        """
        self.request_id = request_id or str(uuid.uuid4())
        self.session_id = session_id
        self.user_id = user_id
    
    def _get_context(self) -> Dict[str, Any]:
        """Get current logging context."""
        context = {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        return context
    
    def _format_message(self, message: str, extra: Dict[str, Any] = None) -> str:
        """Format log message with context."""
        context = self._get_context()
        if extra:
            context.update(extra)
        
        return json.dumps({
            "message": message,
            "context": context
        })
    
    def info(self, message: str, extra: Dict[str, Any] = None):
        """Log info message."""
        self.logger.info(self._format_message(message, extra))
    
    def debug(self, message: str, extra: Dict[str, Any] = None):
        """Log debug message."""
        self.logger.debug(self._format_message(message, extra))
    
    def warning(self, message: str, extra: Dict[str, Any] = None):
        """Log warning message."""
        self.logger.warning(self._format_message(message, extra))
    
    def error(self, message: str, extra: Dict[str, Any] = None):
        """Log error message."""
        self.logger.error(self._format_message(message, extra))
    
    def critical(self, message: str, extra: Dict[str, Any] = None):
        """Log critical message."""
        self.logger.critical(self._format_message(message, extra))
    
    def audit(self, action: str, resource: str, details: Dict[str, Any] = None):
        """Log audit event."""
        audit_event = {
            "action": action,
            "resource": resource,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": self.request_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "details": details or {}
        }
        
        self.logger.info(json.dumps({
            "message": f"AUDIT: {action}",
            "audit_event": audit_event
        }))
    
    def performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """Log performance metrics."""
        perf_data = {
            "operation": operation,
            "duration_ms": duration * 1000,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": self.request_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "details": details or {}
        }
        
        self.logger.info(json.dumps({
            "message": f"PERFORMANCE: {operation}",
            "performance": perf_data
        }))


class FileProcessingLogger:
    """Logger specifically for file processing operations."""
    
    def __init__(self, base_logger: FileIntakeLogger):
        """
        Initialize file processing logger.
        
        Args:
            base_logger: Base logger instance
        """
        self.base_logger = base_logger
        self.processing_start_time = None
        self.file_id = None
        self.file_name = None
    
    def start_processing(self, file_id: str, file_name: str, file_size: int = None):
        """
        Start file processing logging.
        
        Args:
            file_id: File identifier
            file_name: File name
            file_size: File size in bytes
        """
        self.file_id = file_id
        self.file_name = file_name
        self.processing_start_time = datetime.utcnow()
        
        self.base_logger.info(
            f"Starting file processing",
            extra={
                "file_id": file_id,
                "file_name": file_name,
                "file_size": file_size,
                "operation": "start_processing"
            }
        )
    
    def log_step(self, step: str, status: str, details: Dict[str, Any] = None):
        """
        Log processing step.
        
        Args:
            step: Processing step name
            status: Step status
            details: Additional details
        """
        duration = None
        if self.processing_start_time:
            duration = (datetime.utcnow() - self.processing_start_time).total_seconds()
        
        self.base_logger.info(
            f"Processing step: {step}",
            extra={
                "file_id": self.file_id,
                "file_name": self.file_name,
                "step": step,
                "status": status,
                "duration_ms": duration * 1000 if duration else None,
                "operation": "processing_step"
            }
        )
    
    def log_error(self, error: Exception, step: str = None):
        """
        Log processing error.
        
        Args:
            error: Error exception
            step: Processing step where error occurred
        """
        self.base_logger.error(
            f"File processing error: {str(error)}",
            extra={
                "file_id": self.file_id,
                "file_name": self.file_name,
                "step": step,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "operation": "processing_error"
            }
        )
    
    def complete_processing(self, success: bool, result: Dict[str, Any] = None):
        """
        Complete file processing logging.
        
        Args:
            success: Whether processing was successful
            result: Processing result details
        """
        duration = None
        if self.processing_start_time:
            duration = (datetime.utcnow() - self.processing_start_time).total_seconds()
        
        status = "completed" if success else "failed"
        
        self.base_logger.info(
            f"File processing {status}",
            extra={
                "file_id": self.file_id,
                "file_name": self.file_name,
                "status": status,
                "duration_ms": duration * 1000 if duration else None,
                "result": result,
                "operation": "complete_processing"
            }
        )


class SecurityLogger:
    """Logger for security-related events."""
    
    def __init__(self, base_logger: FileIntakeLogger):
        """
        Initialize security logger.
        
        Args:
            base_logger: Base logger instance
        """
        self.base_logger = base_logger
    
    def log_security_event(self, event_type: str, severity: str, details: Dict[str, Any]):
        """
        Log security event.
        
        Args:
            event_type: Type of security event
            severity: Event severity (low, medium, high, critical)
            details: Event details
        """
        self.base_logger.warning(
            f"Security event: {event_type}",
            extra={
                "event_type": event_type,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat(),
                "security_event": True,
                "details": details
            }
        )
    
    def log_virus_detection(self, file_id: str, file_name: str, virus_name: str):
        """
        Log virus detection event.
        
        Args:
            file_id: File identifier
            file_name: File name
            virus_name: Name of detected virus
        """
        self.log_security_event(
            "virus_detected",
            "high",
            {
                "file_id": file_id,
                "file_name": file_name,
                "virus_name": virus_name,
                "action": "quarantine"
            }
        )
    
    def log_suspicious_activity(self, user_id: str, activity: str, details: Dict[str, Any]):
        """
        Log suspicious user activity.
        
        Args:
            user_id: User identifier
            activity: Description of suspicious activity
            details: Additional details
        """
        self.log_security_event(
            "suspicious_activity",
            "medium",
            {
                "user_id": user_id,
                "activity": activity,
                "details": details
            }
        )
    
    def log_access_attempt(self, user_id: str, resource: str, access_type: str, success: bool):
        """
        Log access attempt.
        
        Args:
            user_id: User identifier
            resource: Resource being accessed
            access_type: Type of access attempt
            success: Whether access was successful
        """
        self.base_logger.info(
            f"Access attempt: {access_type}",
            extra={
                "user_id": user_id,
                "resource": resource,
                "access_type": access_type,
                "success": success,
                "timestamp": datetime.utcnow().isoformat(),
                "security_event": True
            }
        )


# Global logger instances
base_logger = FileIntakeLogger()
file_processing_logger = FileProcessingLogger(base_logger)
security_logger = SecurityLogger(base_logger)


def get_logger() -> FileIntakeLogger:
    """Get the base logger instance."""
    return base_logger


def get_file_processing_logger() -> FileProcessingLogger:
    """Get the file processing logger instance."""
    return file_processing_logger


def get_security_logger() -> SecurityLogger:
    """Get the security logger instance."""
    return security_logger


def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        log_dir: Directory for log files
    """
    global base_logger, file_processing_logger, security_logger
    
    # Create log directory if it doesn't exist
    Path(log_dir).mkdir(exist_ok=True)
    
    # Create new logger instances
    base_logger = FileIntakeLogger(log_level=log_level)
    file_processing_logger = FileProcessingLogger(base_logger)
    security_logger = SecurityLogger(base_logger)
    
    return base_logger