@echo off
setlocal enabledelayedexpansion

REM Worker Runner Script for File Intake System (Windows)
REM This script starts Celery workers for the file intake system

REM Configuration
set PROJECT_ROOT=%~dp0..\..\..
set VENV_PATH=%PROJECT_ROOT%\.venv
set CELERY_APP=backend_app.file_intake.workers.celery_app
set CELERY_WORKER_NAME=file_intake_worker
set LOG_LEVEL=info
set WORKER_COUNT=1

REM Function to print status
:print_status
echo [INFO] %~1
goto :eof

REM Function to print success
:print_success
echo [SUCCESS] %~1
goto :eof

REM Function to print warning
:print_warning
echo [WARNING] %~1
goto :eof

REM Function to print error
:print_error
echo [ERROR] %~1
goto :eof

REM Function to check requirements
:check_requirements
call :print_status "Checking requirements..."

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python is not installed"
    exit /b 1
)

REM Check if virtual environment exists
if not exist "%VENV_PATH%" (
    call :print_warning "Virtual environment not found at %VENV_PATH%"
    call :print_status "Creating virtual environment..."
    python -m venv "%VENV_PATH%"
)

REM Check if celery is installed
"%VENV_PATH%\Scripts\celery" --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Celery is not installed in virtual environment"
    exit /b 1
)

REM Check if Redis is running
redis-cli ping >nul 2>&1
if errorlevel 1 (
    call :print_error "Redis is not running. Please start Redis first."
    exit /b 1
)

call :print_success "Requirements check passed"
goto :eof

REM Function to activate virtual environment
:activate_venv
call :print_status "Activating virtual environment..."
call "%VENV_PATH%\Scripts\activate.bat"
goto :eof

REM Function to start Celery worker
:start_worker
set worker_name=%~1
set queue=%~2
set extra_opts=%~3

call :print_status "Starting Celery worker: %worker_name% (Queue: %queue%)"

REM Start worker in background
start "Celery Worker - %worker_name%" /B "%VENV_PATH%\Scripts\celery" -A "%CELERY_APP%" worker ^
    --name="%worker_name%" ^
    --queue="%queue%" ^
    --loglevel="%LOG_LEVEL%" ^
    --concurrency="%WORKER_COUNT%" ^
    --max-tasks-per-child=1000 ^
    --max-memory-per-child=300MB ^
    --pidfile="tmp\%worker_name%.pid" ^
    --logfile="tmp\%worker_name%.log" ^
    %extra_opts%

REM Check if worker started successfully
timeout /t 2 /nobreak >nul
tasklist /FI "WINDOWTITLE eq Celery Worker - %worker_name%" | find "celery" >nul
if errorlevel 1 (
    call :print_error "Failed to start worker %worker_name%"
    call :print_error "Check log: tmp\%worker_name%.log"
) else (
    call :print_success "Worker %worker_name% started successfully"
)
goto :eof

REM Function to stop Celery worker
:stop_worker
set worker_name=%~1

call :print_status "Stopping Celery worker: %worker_name%"

REM Check if worker is running
tasklist /FI "WINDOWTITLE eq Celery Worker - %worker_name%" | find "celery" >nul
if errorlevel 1 (
    call :print_warning "Worker %worker_name% is not running"
) else (
    REM Kill worker by window title
    taskkill /FI "WINDOWTITLE eq Celery Worker - %worker_name%" /F >nul 2>&1
    call :print_success "Worker %worker_name% stopped"
)

REM Remove PID file
if exist "tmp\%worker_name%.pid" del "tmp\%worker_name%.pid"
goto :eof

REM Function to restart Celery worker
:restart_worker
set worker_name=%~1
set queue=%~2
set extra_opts=%~3

call :stop_worker "%worker_name%"
timeout /t 2 /nobreak >nul
call :start_worker "%worker_name%" "%queue%" "%extra_opts%"
goto :eof

REM Function to show worker status
:show_worker_status
call :print_status "Celery Worker Status"
echo ====================

REM Show active workers
call :print_status "Active Workers:"
"%VENV_PATH%\Scripts\celery" -A "%CELERY_APP%" inspect active --timeout=10

REM Show scheduled tasks
call :print_status "Scheduled Tasks:"
"%VENV_PATH%\Scripts\celery" -A "%CELERY_APP%" inspect scheduled --timeout=10

REM Show stats
call :print_status "Worker Statistics:"
"%VENV_PATH%\Scripts\celery" -A "%CELERY_APP%" inspect stats --timeout=10
goto :eof

REM Function to show worker logs
:show_worker_logs
set worker_name=%~1

if "%worker_name%"=="" (
    call :print_error "Please specify worker name"
    exit /b 1
)

set log_file=tmp\%worker_name%.log

if exist "%log_file%" (
    call :print_status "Showing logs for %worker_name% (Press Ctrl+C to exit)"
    echo ========================================
    type "%log_file%"
) else (
    call :print_error "Log file not found: %log_file%"
)
goto :eof

REM Function to clean up worker processes
:cleanup_workers
call :print_status "Cleaning up worker processes..."

REM Kill all worker processes
taskkill /FI "WINDOWTITLE eq Celery Worker*" /F >nul 2>&1

REM Remove PID files
if exist tmp\file_intake_*.pid del tmp\file_intake_*.pid

call :print_success "Worker cleanup completed"
goto :eof

REM Function to show help
:show_help
echo File Intake Worker Runner (Windows)
echo ===================================
echo.
echo Usage: %~n0 [command] [options]
echo.
echo Commands:
echo   start [worker_type]    Start Celery workers
echo                          worker_type: all (default), virus_scan, sanitize, extraction, parsing, finalize
echo   stop [worker_type]     Stop Celery workers
echo   restart [worker_type]  Restart Celery workers
echo   status                 Show worker status
echo   logs [worker_name]     Show worker logs
echo   cleanup                Clean up worker processes
echo   help                   Show this help message
echo.
echo Examples:
echo   %~n0 start all           # Start all workers
echo   %~n0 start virus_scan    # Start only virus scan workers
echo   %~n0 stop extraction     # Stop extraction workers
echo   %~n0 logs file_intake_virus_scan  # Show virus scan worker logs
echo.
echo Environment Variables:
echo   CELERY_BROKER_URL      Redis broker URL (default: redis://localhost:6379/0)
echo   CELERY_RESULT_BACKEND  Redis result backend URL (default: redis://localhost:6379/1)
echo   WORKER_COUNT           Number of worker processes (default: 1)
echo   LOG_LEVEL              Log level (default: info)
goto :eof

REM Main script logic
if "%~1"=="" goto show_help

set command=%~1
set worker_type=%~2

if "%command%"=="start" (
    call :check_requirements
    call :activate_venv
    
    if "%worker_type%"=="" set worker_type=all
    
    if "%worker_type%"=="all" (
        call :start_worker "file_intake_virus_scan" "virus_scan" "--prefetch-multiplier=1"
        call :start_worker "file_intake_sanitize" "sanitize" "--prefetch-multiplier=2"
        call :start_worker "file_intake_extraction" "extraction" "--prefetch-multiplier=1"
        call :start_worker "file_intake_parsing" "parsing" "--prefetch-multiplier=1"
        call :start_worker "file_intake_finalize" "finalize" "--prefetch-multiplier=1"
    ) else if "%worker_type%"=="virus_scan" (
        call :start_worker "file_intake_virus_scan" "virus_scan" "--prefetch-multiplier=1"
    ) else if "%worker_type%"=="sanitize" (
        call :start_worker "file_intake_sanitize" "sanitize" "--prefetch-multiplier=2"
    ) else if "%worker_type%"=="extraction" (
        call :start_worker "file_intake_extraction" "extraction" "--prefetch-multiplier=1"
    ) else if "%worker_type%"=="parsing" (
        call :start_worker "file_intake_parsing" "parsing" "--prefetch-multiplier=1"
    ) else if "%worker_type%"=="finalize" (
        call :start_worker "file_intake_finalize" "finalize" "--prefetch-multiplier=1"
    ) else (
        call :print_error "Unknown worker type: %worker_type%"
        goto show_help
    )
) else if "%command%"=="stop" (
    if "%worker_type%"=="" set worker_type=all
    
    if "%worker_type%"=="all" (
        call :stop_worker "file_intake_virus_scan"
        call :stop_worker "file_intake_sanitize"
        call :stop_worker "file_intake_extraction"
        call :stop_worker "file_intake_parsing"
        call :stop_worker "file_intake_finalize"
    ) else if "%worker_type%"=="virus_scan" (
        call :stop_worker "file_intake_virus_scan"
    ) else if "%worker_type%"=="sanitize" (
        call :stop_worker "file_intake_sanitize"
    ) else if "%worker_type%"=="extraction" (
        call :stop_worker "file_intake_extraction"
    ) else if "%worker_type%"=="parsing" (
        call :stop_worker "file_intake_parsing"
    ) else if "%worker_type%"=="finalize" (
        call :stop_worker "file_intake_finalize"
    ) else (
        call :print_error "Unknown worker type: %worker_type%"
        goto show_help
    )
) else if "%command%"=="restart" (
    call :check_requirements
    call :activate_venv
    
    if "%worker_type%"=="" set worker_type=all
    
    if "%worker_type%"=="all" (
        call :restart_worker "file_intake_virus_scan" "virus_scan" "--prefetch-multiplier=1"
        call :restart_worker "file_intake_sanitize" "sanitize" "--prefetch-multiplier=2"
        call :restart_worker "file_intake_extraction" "extraction" "--prefetch-multiplier=1"
        call :restart_worker "file_intake_parsing" "parsing" "--prefetch-multiplier=1"
        call :restart_worker "file_intake_finalize" "finalize" "--prefetch-multiplier=1"
    ) else if "%worker_type%"=="virus_scan" (
        call :restart_worker "file_intake_virus_scan" "virus_scan" "--prefetch-multiplier=1"
    ) else if "%worker_type%"=="sanitize" (
        call :restart_worker "file_intake_sanitize" "sanitize" "--prefetch-multiplier=2"
    ) else if "%worker_type%"=="extraction" (
        call :restart_worker "file_intake_extraction" "extraction" "--prefetch-multiplier=1"
    ) else if "%worker_type%"=="parsing" (
        call :restart_worker "file_intake_parsing" "parsing" "--prefetch-multiplier=1"
    ) else if "%worker_type%"=="finalize" (
        call :restart_worker "file_intake_finalize" "finalize" "--prefetch-multiplier=1"
    ) else (
        call :print_error "Unknown worker type: %worker_type%"
        goto show_help
    )
) else if "%command%"=="status" (
    call :activate_venv
    call :show_worker_status
) else if "%command%"=="logs" (
    call :show_worker_logs "%worker_type%"
) else if "%command%"=="cleanup" (
    call :cleanup_workers
) else if "%command%"=="help" (
    goto show_help
) else (
    call :print_error "Unknown command: %command%"
    goto show_help
)

endlocal