# Security Scan Module

Local security scanning module with quarantine flow and virus DB management for the AI Recruitment System.

## Overview

The Security Scan Module provides comprehensive file security scanning capabilities using ClamAV, with automated quarantine management and scheduled virus database updates. This module ensures all uploaded files are scanned for malware before processing.

## Architecture

### High-Level Workflow

```
UPLOAD → /incoming → /scanning → ClamAV Scan → SAFE → /clean
                                        └──────── INFECTED → /infected
```

### Components

1. **Scan Service** (`scan_service.py`)
   - File scanning operations using ClamAV
   - Scan result processing and logging
   - Error handling and reporting

2. **Quarantine Manager** (`quarantine_manager.py`)
   - File movement between quarantine folders
   - Folder structure management
   - Safe file isolation and infected file containment

3. **Virus Update Manager** (`virus_update_manager.py`)
   - Virus database validation
   - Database backup and restore operations
   - ClamAV engine reload management

4. **Cron Scheduler** (`cron_scheduler.py`)
   - Daily scheduled maintenance at 00:00
   - Automated database updates and validation
   - Background task management using APScheduler

5. **Configuration** (`config.py`)
   - Folder path definitions
   - Security settings and limits
   - Environment-based configuration

6. **IO Contracts** (`io_contract.py`)
   - Data structures for scan requests and results
   - Type definitions and enums

## Folder Structure

```
data/
└── quarantine/
    ├── incoming/      # Files awaiting scanning
    ├── scanning/      # Files currently being scanned
    ├── clean/         # Safe files after scanning
    ├── infected/      # Infected files in quarantine
    └── logs/          # Security scan and update logs
        ├── security_scan.log
        └── update.log
```

## API Endpoints

### POST /security/scan-file

Scan an uploaded file for viruses.

**Request:**
- File upload (multipart/form-data)

**Response:**
```json
{
  "status": "SAFE|INFECTED|ERROR",
  "details": {
    "engine": "ClamAV",
    "virus_name": "string|null",
    "scan_time": "number|null",
    "error": "string|null"
  },
  "safe_path": "string|null",
  "infected_path": "string|null",
  "timestamp": "ISO 8601 timestamp"
}
```

**Workflow:**
1. Accept file upload
2. Move to `/incoming` folder
3. Move to `/scanning` folder
4. Trigger ClamAV scan
5. Move to `/clean` or `/infected` based on result
6. Return ScanResult

### GET /security/virus-db-status

Get virus database status.

**Response:**
```json
{
  "last_update": "ISO 8601 timestamp",
  "checksum_valid": true|false,
  "db_version": "string"
}
```

### POST /security/manual-db-restore

Manually restore virus database from backup.

**Response:**
```json
{
  "success": true|false,
  "message": "string"
}
```

### Scheduler Management

- **POST /security/start-scheduler**: Start daily maintenance scheduler
- **POST /security/stop-scheduler**: Stop scheduler
- **GET /security/scheduler-status**: Get scheduler status and jobs

## Daily Auto-Update Schedule

**Trigger Time:** `0 0 * * *` (00:00 daily)

**Operations:**
1. Validate virus database checksum
2. If valid: Create backup
3. If invalid: Restore from backup and reload engine
4. Reload ClamAV engine if database was updated
5. Log all operations to `/data/quarantine/logs/update.log`

## Configuration

### Security Settings

- **Max File Size:** 50MB
- **Allowed MIME Types:**
  - `application/pdf`
  - `application/msword`
  - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
  - `text/plain`
  - `application/zip`
  - `application/x-rar-compressed`

### Environment Variables

- `SECURITY_SCAN_DATA_PATH`: Base path for security scan data
- `CLAMAV_SOCKET`: ClamAV socket path (optional)
- `CLAMAV_TIMEOUT`: ClamAV timeout in seconds (default: 30)
- `MAX_FILE_SIZE`: Maximum file size in bytes

## Testing

### Test Suite Structure

```
tests/
├── test_safe_file_scan.py      # Safe file scanning tests
├── test_infected_file_scan.py  # Infected file scanning tests
├── test_quarantine_movement.py # Quarantine file movement tests
├── test_virus_db_validation.py # Virus DB validation and recovery tests
└── test_daily_scheduler.py     # Scheduler functionality tests
```

### Test Coverage

- **Safe file scan**: Moves → clean folder, status = SAFE
- **Infected file scan**: Moves → infected folder, status = INFECTED
- **Corrupted DB**: Fallback → restore backup
- **Missing folders**: Auto-create folder structure
- **Update scheduler**: Runs exactly at 00:00
- **Concurrent scans**: No race conditions, unique IDs

### Running Tests

```bash
cd Backend/backend_app/security_scan
python -m pytest tests/ -v
```

## Integration

### Orchestrator Integration

The security scan module integrates with the central orchestrator through:

1. **IO Contract Requirements:**
   ```python
   requires_security_scan: true
   security_scan_result: ScanResult
   ```

2. **Module Dependencies:**
   - ClamAV daemon must be running
   - APScheduler for scheduled tasks
   - Proper file system permissions for quarantine folders

### Dependencies

**Runtime Dependencies:**
- ClamAV daemon
- APScheduler
- FastAPI

**Development Dependencies:**
- pytest
- pytest-asyncio
- unittest.mock

## Security Considerations

1. **File Isolation**: All files are processed in isolated quarantine folders
2. **Access Control**: Restricted access to infected file storage
3. **Audit Logging**: All scan operations are logged with timestamps
4. **Database Integrity**: Regular checksum validation of virus definitions
5. **Backup Strategy**: Automatic backup before updates, restore on corruption

## Monitoring and Logging

### Log Files

1. **security_scan.log**: Individual scan operations
2. **update.log**: Daily maintenance operations

### Log Format

```
[YYYY-MM-DD HH:MM:SS UTC] Operation - Details
```

### Monitoring Points

- Scan success/failure rates
- Database update frequency
- Quarantine folder sizes
- Scheduler job execution times

## Troubleshooting

### Common Issues

1. **ClamAV Connection Errors**
   - Verify ClamAV daemon is running
   - Check socket configuration
   - Validate permissions

2. **Database Corruption**
   - Manual restore: `POST /security/manual-db-restore`
   - Check backup integrity
   - Monitor disk space

3. **Scheduler Not Running**
   - Start scheduler: `POST /security/start-scheduler`
   - Check APScheduler logs
   - Verify job configuration

4. **File Permission Errors**
   - Ensure write access to quarantine folders
   - Check file ownership
   - Validate umask settings

### Debug Mode

Enable debug logging by setting log level to DEBUG in config.

## Deployment

### Prerequisites

1. ClamAV installed and running
2. Python 3.8+
3. Required Python packages installed

### Setup Steps

1. **Install ClamAV:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install clamav clamav-daemon
   
   # CentOS/RHEL
   sudo yum install clamav clamav-update
   ```

2. **Update Virus Definitions:**
   ```bash
   sudo freshclam
   ```

3. **Start ClamAV Daemon:**
   ```bash
   sudo systemctl start clamav-daemon
   sudo systemctl enable clamav-daemon
   ```

4. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Paths:**
   - Set `SECURITY_SCAN_DATA_PATH` environment variable
   - Ensure proper file system permissions

6. **Start Scheduler:**
   - Call `POST /security/start-scheduler` on application startup
   - Verify job is scheduled with `GET /security/scheduler-status`

## Performance Considerations

- **Concurrent Scans**: Module supports concurrent file scanning
- **File Size Limits**: Enforced to prevent resource exhaustion
- **Database Updates**: Scheduled during low-usage hours (00:00)
- **Log Rotation**: Implement log rotation for production systems

## Future Enhancements

- Integration with additional antivirus engines
- Real-time scanning for high-priority files
- Advanced threat detection and reporting
- Integration with SIEM systems
- Machine learning-based threat detection