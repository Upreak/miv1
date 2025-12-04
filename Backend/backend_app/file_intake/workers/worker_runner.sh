#!/bin/bash

# Worker Runner Script for File Intake System
# This script starts Celery workers for the file intake system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
CELERY_APP="backend_app.file_intake.workers.celery_app"
CELERY_WORKER_NAME="file_intake_worker"
LOG_LEVEL="info"
WORKER_COUNT=$(nproc)  # Use all available CPU cores
CELERY_OPTS="--loglevel=$LOG_LEVEL --concurrency=$WORKER_COUNT --max-tasks-per-child=1000 --max-memory-per-child=300MB"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required commands exist
check_requirements() {
    print_status "Checking requirements..."
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_PATH" ]; then
        print_warning "Virtual environment not found at $VENV_PATH"
        print_status "Creating virtual environment..."
        python3 -m venv "$VENV_PATH"
    fi
    
    # Check if celery is installed
    if ! "$VENV_PATH/bin/celery" --version &> /dev/null; then
        print_error "Celery is not installed in virtual environment"
        exit 1
    fi
    
    # Check if Redis is running
    if ! redis-cli ping &> /dev/null; then
        print_error "Redis is not running. Please start Redis first."
        exit 1
    fi
    
    print_success "Requirements check passed"
}

# Function to activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
}

# Function to start Celery worker
start_worker() {
    local worker_name=$1
    local queue=$2
    local extra_opts=$3
    
    print_status "Starting Celery worker: $worker_name (Queue: $queue)"
    
    # Start worker in background
    nohup "$VENV_PATH/bin/celery" -A "$CELERY_APP" worker \
        --name="$worker_name" \
        --queue="$queue" \
        --loglevel="$LOG_LEVEL" \
        --concurrency="$WORKER_COUNT" \
        --max-tasks-per-child=1000 \
        --max-memory-per-child=300MB \
        --pidfile="/tmp/${worker_name}.pid" \
        --logfile="/tmp/${worker_name}.log" \
        $extra_opts \
        > /dev/null 2>&1 &
    
    # Check if worker started successfully
    sleep 2
    if pgrep -f "$worker_name" > /dev/null; then
        print_success "Worker $worker_name started successfully"
    else
        print_error "Failed to start worker $worker_name"
        print_error "Check log: /tmp/${worker_name}.log"
    fi
}

# Function to stop Celery worker
stop_worker() {
    local worker_name=$1
    
    print_status "Stopping Celery worker: $worker_name"
    
    # Check if worker is running
    if pgrep -f "$worker_name" > /dev/null; then
        # Get PID file
        local pid_file="/tmp/${worker_name}.pid"
        
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            if ps -p $pid > /dev/null; then
                kill -TERM $pid
                print_success "Worker $worker_name stopped gracefully"
            else
                rm -f "$pid_file"
                print_warning "Worker $worker_name was not running"
            fi
        else
            # Kill by name if no PID file
            pkill -f "$worker_name"
            print_success "Worker $worker_name stopped forcefully"
        fi
    else
        print_warning "Worker $worker_name is not running"
    fi
}

# Function to restart Celery worker
restart_worker() {
    local worker_name=$1
    local queue=$2
    local extra_opts=$3
    
    stop_worker "$worker_name"
    sleep 2
    start_worker "$worker_name" "$queue" "$extra_opts"
}

# Function to show worker status
show_worker_status() {
    print_status "Celery Worker Status"
    echo "===================="
    
    # Check if Celery is installed
    if ! command -v celery &> /dev/null; then
        print_error "Celery is not installed"
        return 1
    fi
    
    # Show active workers
    print_status "Active Workers:"
    celery -A "$CELERY_APP" inspect active --timeout=10
    
    # Show scheduled tasks
    print_status "Scheduled Tasks:"
    celery -A "$CELERY_APP" inspect scheduled --timeout=10
    
    # Show stats
    print_status "Worker Statistics:"
    celery -A "$CELERY_APP" inspect stats --timeout=10
}

# Function to show worker logs
show_worker_logs() {
    local worker_name=$1
    
    if [ -z "$worker_name" ]; then
        print_error "Please specify worker name"
        return 1
    fi
    
    local log_file="/tmp/${worker_name}.log"
    
    if [ -f "$log_file" ]; then
        print_status "Showing logs for $worker_name (Ctrl+C to exit)"
        echo "========================================"
        tail -f "$log_file"
    else
        print_error "Log file not found: $log_file"
    fi
}

# Function to clean up worker processes
cleanup_workers() {
    print_status "Cleaning up worker processes..."
    
    # Kill all worker processes
    pkill -f "celery.*worker.*file_intake"
    
    # Remove PID files
    rm -f /tmp/file_intake_*.pid
    
    print_success "Worker cleanup completed"
}

# Function to show help
show_help() {
    echo "File Intake Worker Runner"
    echo "========================"
    echo
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  start [worker_type]    Start Celery workers"
    echo "                         worker_type: all (default), virus_scan, sanitize, extraction, parsing, finalize"
    echo "  stop [worker_type]     Stop Celery workers"
    echo "  restart [worker_type]  Restart Celery workers"
    echo "  status                 Show worker status"
    echo "  logs [worker_name]     Show worker logs"
    echo "  cleanup                Clean up worker processes"
    echo "  help                   Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start all           # Start all workers"
    echo "  $0 start virus_scan    # Start only virus scan workers"
    echo "  $0 stop extraction     # Stop extraction workers"
    echo "  $0 logs file_intake_virus_scan  # Show virus scan worker logs"
    echo
    echo "Environment Variables:"
    echo "  CELERY_BROKER_URL      Redis broker URL (default: redis://localhost:6379/0)"
    echo "  CELERY_RESULT_BACKEND  Redis result backend URL (default: redis://localhost:6379/1)"
    echo "  WORKER_COUNT           Number of worker processes (default: CPU cores)"
    echo "  LOG_LEVEL              Log level (default: info)"
}

# Main script logic
main() {
    case "${1:-help}" in
        start)
            check_requirements
            activate_venv
            
            local worker_type="${2:-all}"
            
            case $worker_type in
                all)
                    start_worker "file_intake_virus_scan" "virus_scan" "--prefetch-multiplier=1"
                    start_worker "file_intake_sanitize" "sanitize" "--prefetch-multiplier=2"
                    start_worker "file_intake_extraction" "extraction" "--prefetch-multiplier=1"
                    start_worker "file_intake_parsing" "parsing" "--prefetch-multiplier=1"
                    start_worker "file_intake_finalize" "finalize" "--prefetch-multiplier=1"
                    ;;
                virus_scan)
                    start_worker "file_intake_virus_scan" "virus_scan" "--prefetch-multiplier=1"
                    ;;
                sanitize)
                    start_worker "file_intake_sanitize" "sanitize" "--prefetch-multiplier=2"
                    ;;
                extraction)
                    start_worker "file_intake_extraction" "extraction" "--prefetch-multiplier=1"
                    ;;
                parsing)
                    start_worker "file_intake_parsing" "parsing" "--prefetch-multiplier=1"
                    ;;
                finalize)
                    start_worker "file_intake_finalize" "finalize" "--prefetch-multiplier=1"
                    ;;
                *)
                    print_error "Unknown worker type: $worker_type"
                    show_help
                    exit 1
                    ;;
            esac
            ;;
            
        stop)
            local worker_type="${2:-all}"
            
            case $worker_type in
                all)
                    stop_worker "file_intake_virus_scan"
                    stop_worker "file_intake_sanitize"
                    stop_worker "file_intake_extraction"
                    stop_worker "file_intake_parsing"
                    stop_worker "file_intake_finalize"
                    ;;
                virus_scan)
                    stop_worker "file_intake_virus_scan"
                    ;;
                sanitize)
                    stop_worker "file_intake_sanitize"
                    ;;
                extraction)
                    stop_worker "file_intake_extraction"
                    ;;
                parsing)
                    stop_worker "file_intake_parsing"
                    ;;
                finalize)
                    stop_worker "file_intake_finalize"
                    ;;
                *)
                    print_error "Unknown worker type: $worker_type"
                    show_help
                    exit 1
                    ;;
            esac
            ;;
            
        restart)
            check_requirements
            activate_venv
            
            local worker_type="${2:-all}"
            
            case $worker_type in
                all)
                    restart_worker "file_intake_virus_scan" "virus_scan" "--prefetch-multiplier=1"
                    restart_worker "file_intake_sanitize" "sanitize" "--prefetch-multiplier=2"
                    restart_worker "file_intake_extraction" "extraction" "--prefetch-multiplier=1"
                    restart_worker "file_intake_parsing" "parsing" "--prefetch-multiplier=1"
                    restart_worker "file_intake_finalize" "finalize" "--prefetch-multiplier=1"
                    ;;
                virus_scan)
                    restart_worker "file_intake_virus_scan" "virus_scan" "--prefetch-multiplier=1"
                    ;;
                sanitize)
                    restart_worker "file_intake_sanitize" "sanitize" "--prefetch-multiplier=2"
                    ;;
                extraction)
                    restart_worker "file_intake_extraction" "extraction" "--prefetch-multiplier=1"
                    ;;
                parsing)
                    restart_worker "file_intake_parsing" "parsing" "--prefetch-multiplier=1"
                    ;;
                finalize)
                    restart_worker "file_intake_finalize" "finalize" "--prefetch-multiplier=1"
                    ;;
                *)
                    print_error "Unknown worker type: $worker_type"
                    show_help
                    exit 1
                    ;;
            esac
            ;;
            
        status)
            activate_venv
            show_worker_status
            ;;
            
        logs)
            show_worker_logs "$2"
            ;;
            
        cleanup)
            cleanup_workers
            ;;
            
        help|--help|-h)
            show_help
            ;;
            
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"