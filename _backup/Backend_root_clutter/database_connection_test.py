#!/usr/bin/env python3
"""
Database Connection Diagnostic Script
Tests database connectivity and configuration
"""

import sys
import logging
import os

# Configure logging with ASCII-only format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


def test_database_config():
    """Test database configuration"""
    print("Testing database configuration...")
    
    # Check environment variables
    db_url = os.environ.get('DATABASE_URL')
    async_db_url = os.environ.get('ASYNC_DATABASE_URL')
    
    print(f"DATABASE_URL: {db_url}")
    print(f"ASYNC_DATABASE_URL: {async_db_url}")
    
    # Check if URLs contain async driver
    if db_url and 'asyncpg' in db_url:
        print("DATABASE_URL uses asyncpg")
    elif db_url and 'psycopg2' in db_url:
        print("DATABASE_URL uses psycopg2 (sync driver)")
    else:
        print("DATABASE_URL driver unknown")
    
    if async_db_url and 'asyncpg' in async_db_url:
        print("ASYNC_DATABASE_URL uses asyncpg")
    elif async_db_url and 'psycopg2' in async_db_url:
        print("ASYNC_DATABASE_URL uses psycopg2 (sync driver)")
    else:
        print("ASYNC_DATABASE_URL driver unknown")


def test_sqlalchemy_imports():
    """Test SQLAlchemy imports"""
    print("\nTesting SQLAlchemy imports...")
    
    try:
        import sqlalchemy
        print(f"SQLAlchemy version: {sqlalchemy.__version__}")
    except ImportError as e:
        print(f"Failed to import SQLAlchemy: {e}")
        return False
    
    try:
        import sqlalchemy.ext.asyncio
        print("SQLAlchemy async extension available")
    except ImportError as e:
        print(f"SQLAlchemy async extension not available: {e}")
        return False
    
    return True


def test_asyncpg_import():
    """Test asyncpg import"""
    print("\nTesting asyncpg import...")
    
    try:
        import asyncpg
        print("asyncpg is available")
        return True
    except ImportError as e:
        print(f"asyncpg not available: {e}")
        return False


def test_psycopg2_import():
    """Test psycopg2 import"""
    print("\nTesting psycopg2 import...")
    
    try:
        import psycopg2
        print("psycopg2 is available")
        return True
    except ImportError as e:
        print(f"psycopg2 not available: {e}")
        return False


def test_database_connection():
    """Test actual database connection"""
    print("\nTesting database connection...")
    
    try:
        from backend_app.db.connection import get_db
        print("Database connection module imported")
        
        # Try to get database session
        db_gen = get_db()
        try:
            db = next(db_gen)
            print("Database session created successfully")
            return True
        except Exception as e:
            print(f"Failed to create database session: {e}")
            return False
        finally:
            db_gen.close()
            
    except Exception as e:
        print(f"Failed to import database connection: {e}")
        return False


def main():
    """Main test function"""
    print("="*60)
    print("DATABASE CONNECTION DIAGNOSTIC")
    print("="*60)
    
    tests = [
        ("Database Configuration", test_database_config),
        ("SQLAlchemy Imports", test_sqlalchemy_imports),
        ("asyncpg Import", test_asyncpg_import),
        ("psycopg2 Import", test_psycopg2_import),
        ("Database Connection", test_database_connection)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"{test_name} failed with exception: {e}")
            results.append(False)
    
    # Summary
    total_tests = len(tests)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests
    
    print("\n" + "="*60)
    print("DATABASE DIAGNOSTIC SUMMARY")
    print("="*60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\nAll database tests passed!")
        return 0
    else:
        print(f"\n{failed_tests} test(s) failed.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Database diagnostic failed with exception: {e}")
        sys.exit(1)