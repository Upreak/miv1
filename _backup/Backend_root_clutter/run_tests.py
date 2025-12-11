#!/usr/bin/env python3
"""
Test runner for the authentication system
"""

import pytest
import sys
import os
import logging
from datetime import datetime
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_results.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_test_suite():
    """Run the complete test suite"""
    logger.info("Starting authentication system test suite...")
    
    # Test configuration
    test_config = {
        "test_date": datetime.now().isoformat(),
        "python_version": sys.version,
        "test_files": [
            "tests/test_auth_integration.py",
            "test_auth_system.py"
        ],
        "test_categories": [
            "otp_service",
            "token_manager", 
            "rate_limiter",
            "totp_service",
            "email_service",
            "social_auth",
            "enhanced_auth_service",
            "api_endpoints",
            "integration_scenarios",
            "error_handling"
        ]
    }
    
    logger.info(f"Test configuration: {json.dumps(test_config, indent=2)}")
    
    # Run tests with coverage
    test_args = [
        "pytest",
        "-v",
        "--tb=short",
        "--cov=backend_app",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--junit-xml=test_results.xml",
        "--html=test_report.html",
        "--self-contained-html",
        "--strict-markers",
        "--disable-warnings",
        "-m", "not slow"
    ]
    
    # Add test files
    test_args.extend(test_config["test_files"])
    
    logger.info(f"Running tests with command: {' '.join(test_args)}")
    
    try:
        # Run tests
        exit_code = pytest.main(test_args)
        
        # Generate test report
        generate_test_report(test_config, exit_code)
        
        logger.info(f"Test suite completed with exit code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        return 1

def run_specific_test_category(category):
    """Run tests for a specific category"""
    logger.info(f"Running tests for category: {category}")
    
    category_mapping = {
        "otp_service": ["-k", "test_otp"],
        "token_manager": ["-k", "test_token"],
        "rate_limiter": ["-k", "test_rate"],
        "totp_service": ["-k", "test_totp"],
        "email_service": ["-k", "test_email"],
        "social_auth": ["-k", "test_social"],
        "enhanced_auth_service": ["-k", "test_enhanced"],
        "api_endpoints": ["-k", "test_api"],
        "integration_scenarios": ["-k", "test_integration"],
        "error_handling": ["-k", "test_error"]
    }
    
    if category not in category_mapping:
        logger.error(f"Unknown test category: {category}")
        return 1
    
    test_args = [
        "pytest",
        "-v",
        "--tb=short",
        "--cov=backend_app",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--junit-xml=test_results.xml",
        "--html=test_report.html",
        "--self-contained-html",
        "-m", "not slow"
    ] + category_mapping[category]
    
    try:
        exit_code = pytest.main(test_args)
        logger.info(f"Tests for {category} completed with exit code: {exit_code}")
        return exit_code
    except Exception as e:
        logger.error(f"Error running tests for {category}: {str(e)}")
        return 1

def generate_test_report(test_config, exit_code):
    """Generate comprehensive test report"""
    report = {
        "test_summary": {
            "date": test_config["test_date"],
            "python_version": test_config["python_version"],
            "exit_code": exit_code,
            "status": "PASSED" if exit_code == 0 else "FAILED",
            "categories": test_config["test_categories"]
        },
        "test_files": test_config["test_files"],
        "configuration": test_config,
        "recommendations": []
    }
    
    # Add recommendations based on exit code
    if exit_code != 0:
        report["recommendations"].append(
            "Some tests failed. Please review the test output and fix the issues."
        )
    
    # Save report
    report_file = "test_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Test report saved to: {report_file}")
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Date: {report['test_summary']['date']}")
    print(f"Python Version: {report['test_summary']['python_version']}")
    print(f"Exit Code: {report['test_summary']['exit_code']}")
    print(f"Status: {report['test_summary']['status']}")
    print(f"Test Categories: {', '.join(report['test_summary']['categories'])}")
    print("="*50)
    
    if report["recommendations"]:
        print("\nRECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"• {rec}")

def validate_test_environment():
    """Validate that the test environment is properly set up"""
    logger.info("Validating test environment...")
    
    # Check required packages
    required_packages = [
        "pytest",
        "pytest-cov",
        "pytest-html",
        "pytest-junitxml",
        "fastapi",
        "sqlalchemy",
        "pyotp",
        "qrcode",
        "requests",
        "python-dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install missing packages using: pip install -r requirements.txt")
        return False
    
    # Check test files
    test_files = [
        "tests/test_auth_integration.py",
        "test_auth_system.py"
    ]
    
    missing_files = []
    for test_file in test_files:
        if not os.path.exists(test_file):
            missing_files.append(test_file)
    
    if missing_files:
        logger.error(f"Missing test files: {', '.join(missing_files)}")
        return False
    
    # Check environment variables
    env_vars = [
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "SMTP_SERVER",
        "SMTP_USERNAME",
        "SMTP_PASSWORD"
    ]
    
    missing_env_vars = []
    for env_var in env_vars:
        if not os.getenv(env_var):
            missing_env_vars.append(env_var)
    
    if missing_env_vars:
        logger.warning(f"Missing environment variables: {', '.join(missing_env_vars)}")
        logger.warning("Some tests may fail due to missing configuration")
    
    logger.info("Test environment validation completed")
    return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run authentication system tests")
    parser.add_argument("--category", type=str, help="Run specific test category")
    parser.add_argument("--validate", action="store_true", help="Validate test environment")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.validate:
        if not validate_test_environment():
            sys.exit(1)
        return
    
    if args.category:
        exit_code = run_specific_test_category(args.category)
    else:
        exit_code = run_test_suite()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()