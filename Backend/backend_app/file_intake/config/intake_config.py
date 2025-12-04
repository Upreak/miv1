"""
File Intake Configuration

This module contains configuration settings for the file intake system.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class StorageConfig:
    """Storage configuration settings."""
    storage_type: str = "local"  # local, s3, gcs, azure
    local_storage_path: str = "./storage"
    s3_bucket: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_region: Optional[str] = None
    s3_endpoint_url: Optional[str] = None
    azure_connection_string: Optional[str] = None
    azure_container_name: Optional[str] = None
    gcs_bucket: Optional[str] = None
    gcs_credentials_path: Optional[str] = None
    
    def __post_init__(self):
        """Validate storage configuration."""
        if self.storage_type == "s3":
            if not self.s3_bucket:
                raise ValueError("S3 bucket name is required for S3 storage")
        
        elif self.storage_type == "azure":
            if not self.azure_container_name:
                raise ValueError("Azure container name is required for Azure storage")
        
        elif self.storage_type == "gcs":
            if not self.gcs_bucket:
                raise ValueError("GCS bucket name is required for GCS storage")


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = field(default_factory=lambda: [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
        "image/tiff",
        "image/bmp",
        "application/zip",
        "application/x-rar-compressed",
        "application/x-7z-compressed",
        "application/x-tar",
        "application/gzip",
        "video/mp4",
        "video/mpeg",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-ms-wmv",
        "video/x-flv",
        "audio/mpeg",
        "audio/wav",
        "audio/ogg",
        "audio/x-ms-wma",
        "audio/x-aiff",
        "audio/x-au",
        "application/x-font-ttf",
        "application/x-font-otf",
        "application/x-font-type1",
        "font/woff",
        "font/woff2",
        "application/vnd.ms-fontobject",
    ])
    blocked_extensions: List[str] = field(default_factory=lambda: [
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
        '.xlsm', '.xlsx', '.xltm', '.xltx', '.xlam'
    ])
    suspicious_extensions: List[str] = field(default_factory=lambda: [
        '.php', '.asp', '.jsp', '.cgi', '.pl', '.py', '.rb', '.go', '.rs',
        '.swift', '.kt', '.scala', '.r', '.m', '.f90', '.f95', '.f03',
        '.f08', '.f', '.for', '.f77', '.f90', '.f95', '.f03', '.f08',
        '.f', '.for', '.f77', '.php3', '.php4', '.php5', '.phtml', '.shtml',
        '.pl', '.py', '.rb', '.cgi', '.sh', '.bash', '.zsh', '.fish',
        '.ps1', '.bat', '.cmd', '.vbs', '.js', '.ts', '.coffee', '.litcoffee'
    ])
    require_virus_scan: bool = True
    quarantine_infected_files: bool = True
    quarantine_duration_hours: int = 24
    scan_metadata: bool = True
    validate_file_signature: bool = True
    max_retries: int = 3
    retry_delay_seconds: int = 5


@dataclass
class VirusScanConfig:
    """Virus scan configuration settings."""
    engine: str = "clamav"  # clamav, virustotal, sophos, mcafee
    clamav_socket_path: Optional[str] = None
    clamav_host: Optional[str] = None
    clamav_port: Optional[int] = None
    virustotal_api_key: Optional[str] = None
    virustotal_timeout: int = 30
    sophos_engine_path: Optional[str] = None
    mcafee_engine_path: Optional[str] = None
    scan_timeout: int = 300  # 5 minutes
    max_file_size_for_scan: int = 100 * 1024 * 1024  # 100MB
    enable_heuristic_scan: bool = True
    scan_compressed_files: bool = True
    scan_embedded_files: bool = True


@dataclass
class ProcessingConfig:
    """Processing configuration settings."""
    max_concurrent_uploads: int = 10
    max_concurrent_scans: int = 5
    max_concurrent_extractions: int = 3
    max_concurrent_parsing: int = 2
    extraction_timeout: int = 300  # 5 minutes
    parsing_timeout: int = 600  # 10 minutes
    cleanup_interval_hours: int = 24
    retention_days: int = 30
    enable_progress_tracking: bool = True
    enable_deduplication: bool = True
    deduplication_hash_algorithm: str = "sha256"
    enable_compression: bool = False
    compression_algorithm: str = "gzip"


@dataclass
class QueueConfig:
    """Queue configuration settings."""
    queue_type: str = "redis"  # redis, rabbitmq, sqs, kafka
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_password: Optional[str] = None
    rabbitmq_host: Optional[str] = None
    rabbitmq_port: Optional[int] = None
    rabbitmq_username: Optional[str] = None
    rabbitmq_password: Optional[str] = None
    rabbitmq_vhost: Optional[str] = None
    sqs_region: Optional[str] = None
    sqs_queue_url: Optional[str] = None
    sqs_access_key: Optional[str] = None
    sqs_secret_key: Optional[str] = None
    kafka_bootstrap_servers: Optional[str] = None
    kafka_topic: Optional[str] = None
    kafka_group_id: Optional[str] = None
    max_retries: int = 3
    retry_delay_seconds: int = 5
    dead_letter_queue_enabled: bool = True
    dead_letter_queue_max_retries: int = 5


@dataclass
class CeleryConfig:
    """Celery configuration settings."""
    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/1"
    broker_connection_retry_on_startup: bool = True
    broker_connection_max_retries: int = 3
    broker_connection_retry_delay: float = 1.0
    broker_connection_retry_backoff: bool = True
    broker_connection_retry_backoff_max: float = 10.0
    result_backend_always_retry: bool = True
    result_backend_retry_policy: Dict[str, Any] = field(default_factory=lambda: {
        "max_retries": 3,
        "interval_start": 0,
        "interval_step": 0.2,
        "interval_max": 2,
        "jitter": None
    })
    task_serializer: str = "json"
    accept_content: List[str] = field(default_factory=lambda: ["json"])
    result_serializer: str = "json"
    timezone: str = "UTC"
    enable_utc: bool = True
    task_track_started: bool = True
    task_acks_late: bool = True
    worker_prefetch_multiplier: int = 1
    worker_max_tasks_per_child: int = 1000
    worker_max_memory_per_child: str = "300MB"
    task_soft_time_limit: int = 300
    task_time_limit: int = 600
    worker_disable_rate_limits: bool = False
    worker_hijack_root_logger: bool = False
    worker_log_color: bool = True
    worker_log_format: str = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
    worker_task_log_format: str = "[%(asctime)s: %(levelname)s/%(processName)s][%(task_id)s] %(message)s"
    worker_redirect_stdouts: bool = True
    worker_redirect_stdouts_level: str = "WARNING"
    task_routes: Dict[str, str] = field(default_factory=lambda: {
        "file_intake.tasks.virus_scan_task": {"queue": "virus_scan"},
        "file_intake.tasks.sanitize_task": {"queue": "sanitize"},
        "file_intake.tasks.extract_task": {"queue": "extraction"},
        "file_intake.tasks.parse_task": {"queue": "parsing"},
        "file_intake.tasks.finalize_task": {"queue": "finalize"}
    })
    task_default_queue: str = "file_intake"
    task_default_exchange: str = "file_intake"
    task_default_routing_key: str = "file_intake"
    task_queues: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "virus_scan": {
            "exchange": "virus_scan",
            "routing_key": "virus_scan",
            "queue_arguments": {"x-max-priority": 10}
        },
        "sanitize": {
            "exchange": "sanitize",
            "routing_key": "sanitize",
            "queue_arguments": {"x-max-priority": 8}
        },
        "extraction": {
            "exchange": "extraction",
            "routing_key": "extraction",
            "queue_arguments": {"x-max-priority": 6}
        },
        "parsing": {
            "exchange": "parsing",
            "routing_key": "parsing",
            "queue_arguments": {"x-max-priority": 4}
        },
        "finalize": {
            "exchange": "finalize",
            "routing_key": "finalize",
            "queue_arguments": {"x-max-priority": 2}
        },
        "file_intake": {
            "exchange": "file_intake",
            "routing_key": "file_intake",
            "queue_arguments": {"x-max-priority": 1}
        }
    })


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_date_format: str = "%Y-%m-%d %H:%M:%S"
    log_directory: str = "./logs"
    enable_file_logging: bool = True
    enable_console_logging: bool = True
    enable_audit_logging: bool = True
    enable_performance_logging: bool = True
    log_rotation_enabled: bool = True
    log_rotation_max_size_mb: int = 100
    log_rotation_backup_count: int = 5
    sensitive_data_masking: bool = True
    request_id_header: str = "X-Request-ID"
    correlation_id_header: str = "X-Correlation-ID"


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    database_url: str = "sqlite:///./file_intake.db"
    echo_sql: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    enable_migrations: bool = True
    migration_directory: str = "./migrations"


@dataclass
class MonitoringConfig:
    """Monitoring configuration settings."""
    enable_metrics: bool = True
    metrics_port: int = 8080
    metrics_path: str = "/metrics"
    enable_health_checks: bool = True
    health_check_path: str = "/health"
    enable_tracing: bool = False
    tracing_service_name: str = "file_intake"
    tracing_endpoint: Optional[str] = None
    alerting_enabled: bool = True
    alerting_email: Optional[str] = None
    alerting_webhook_url: Optional[str] = None
    alerting_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "error_rate": 0.05,
        "processing_time": 300,
        "queue_size": 1000,
        "disk_usage": 0.90
    })


@dataclass
class FileIntakeConfig:
    """Main configuration class for file intake system."""
    storage: StorageConfig = field(default_factory=StorageConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    virus_scan: VirusScanConfig = field(default_factory=VirusScanConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    queue: QueueConfig = field(default_factory=QueueConfig)
    celery: CeleryConfig = field(default_factory=CeleryConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    environment: str = "development"
    debug: bool = False
    testing: bool = False
    
    def __post_init__(self):
        """Validate configuration."""
        # Create necessary directories
        Path(self.storage.local_storage_path).mkdir(parents=True, exist_ok=True)
        Path(self.logging.log_directory).mkdir(parents=True, exist_ok=True)
        
        # Validate configurations
        self.storage.__post_init__()
    
    @classmethod
    def from_env(cls) -> 'FileIntakeConfig':
        """Load configuration from environment variables."""
        config = cls()
        
        # Storage configuration
        config.storage.storage_type = os.getenv("STORAGE_TYPE", config.storage.storage_type)
        config.storage.local_storage_path = os.getenv("LOCAL_STORAGE_PATH", config.storage.local_storage_path)
        config.storage.s3_bucket = os.getenv("S3_BUCKET")
        config.storage.s3_access_key = os.getenv("S3_ACCESS_KEY")
        config.storage.s3_secret_key = os.getenv("S3_SECRET_KEY")
        config.storage.s3_region = os.getenv("S3_REGION")
        config.storage.s3_endpoint_url = os.getenv("S3_ENDPOINT_URL")
        config.storage.azure_connection_string = os.getenv("AZURE_CONNECTION_STRING")
        config.storage.azure_container_name = os.getenv("AZURE_CONTAINER_NAME")
        config.storage.gcs_bucket = os.getenv("GCS_BUCKET")
        config.storage.gcs_credentials_path = os.getenv("GCS_CREDENTIALS_PATH")
        
        # Security configuration
        config.security.max_file_size = int(os.getenv("MAX_FILE_SIZE", config.security.max_file_size))
        config.security.require_virus_scan = os.getenv("REQUIRE_VIRUS_SCAN", "true").lower() == "true"
        config.security.quarantine_infected_files = os.getenv("QUARANTINE_INFECTED_FILES", "true").lower() == "true"
        config.security.quarantine_duration_hours = int(os.getenv("QUARANTINE_DURATION_HOURS", config.security.quarantine_duration_hours))
        
        # Virus scan configuration
        config.virus_scan.engine = os.getenv("VIRUS_SCAN_ENGINE", config.virus_scan.engine)
        config.virus_scan.clamav_socket_path = os.getenv("CLAMAV_SOCKET_PATH")
        config.virus_scan.clamav_host = os.getenv("CLAMAV_HOST")
        config.virus_scan.clamav_port = int(os.getenv("CLAMAV_PORT", 3310)) if os.getenv("CLAMAV_PORT") else None
        config.virus_scan.virustotal_api_key = os.getenv("VIRUSTOTAL_API_KEY")
        config.virus_scan.scan_timeout = int(os.getenv("SCAN_TIMEOUT", config.virus_scan.scan_timeout))
        
        # Processing configuration
        config.processing.max_concurrent_uploads = int(os.getenv("MAX_CONCURRENT_UPLOADS", config.processing.max_concurrent_uploads))
        config.processing.max_concurrent_scans = int(os.getenv("MAX_CONCURRENT_SCANS", config.processing.max_concurrent_scans))
        config.processing.extraction_timeout = int(os.getenv("EXTRACTION_TIMEOUT", config.processing.extraction_timeout))
        config.processing.parsing_timeout = int(os.getenv("PARSING_TIMEOUT", config.processing.parsing_timeout))
        
        # Queue configuration
        config.queue.queue_type = os.getenv("QUEUE_TYPE", config.queue.queue_type)
        config.queue.redis_url = os.getenv("REDIS_URL", config.queue.redis_url)
        config.queue.max_retries = int(os.getenv("QUEUE_MAX_RETRIES", config.queue.max_retries))
        
        # Celery configuration
        config.celery.broker_url = os.getenv("CELERY_BROKER_URL", config.celery.broker_url)
        config.celery.result_backend = os.getenv("CELERY_RESULT_BACKEND", config.celery.result_backend)
        config.celery.broker_connection_retry_on_startup = os.getenv("CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP", "true").lower() == "true"
        config.celery.broker_connection_max_retries = int(os.getenv("CELERY_BROKER_CONNECTION_MAX_RETRIES", config.celery.broker_connection_max_retries))
        config.celery.broker_connection_retry_delay = float(os.getenv("CELERY_BROKER_CONNECTION_RETRY_DELAY", config.celery.broker_connection_retry_delay))
        config.celery.task_soft_time_limit = int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", config.celery.task_soft_time_limit))
        config.celery.task_time_limit = int(os.getenv("CELERY_TASK_TIME_LIMIT", config.celery.task_time_limit))
        config.celery.worker_prefetch_multiplier = int(os.getenv("CELERY_WORKER_PREFETCH_MULTIPLIER", config.celery.worker_prefetch_multiplier))
        config.celery.worker_max_tasks_per_child = int(os.getenv("CELERY_WORKER_MAX_TASKS_PER_CHILD", config.celery.worker_max_tasks_per_child))
        
        # Logging configuration
        config.logging.log_level = os.getenv("LOG_LEVEL", config.logging.log_level)
        config.logging.log_directory = os.getenv("LOG_DIRECTORY", config.logging.log_directory)
        
        # Database configuration
        config.database.database_url = os.getenv("DATABASE_URL", config.database.database_url)
        config.database.echo_sql = os.getenv("ECHO_SQL", "false").lower() == "true"
        
        # Environment
        config.environment = os.getenv("ENVIRONMENT", config.environment)
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        config.testing = os.getenv("TESTING", "false").lower() == "true"
        
        return config


# Global configuration instance
config = FileIntakeConfig.from_env()


def get_config() -> FileIntakeConfig:
    """Get the global configuration instance."""
    return config


def reload_config() -> FileIntakeConfig:
    """Reload configuration from environment variables."""
    global config
    config = FileIntakeConfig.from_env()
    return config