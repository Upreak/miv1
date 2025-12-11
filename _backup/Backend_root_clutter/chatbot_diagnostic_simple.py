#!/usr/bin/env python3
"""
Simple Chatbot Diagnostic Script
Identifies root causes without encoding issues
"""

import sys
import os
import traceback

def test_asyncpg():
    """Test asyncpg availability"""
    print("Testing asyncpg...")
    try:
        import asyncpg
        print("SUCCESS: asyncpg is available")
        return True
    except ImportError as e:
        print(f"FAILED: asyncpg not available - {e}")
        return False

def test_psycopg2():
    """Test psycopg2 availability"""
    print("Testing psycopg2...")
    try:
        import psycopg2
        print("SUCCESS: psycopg2 is available")
        return True
    except ImportError as e:
        print(f"FAILED: psycopg2 not available - {e}")
        return False

def test_sqlalchemy():
    """Test SQLAlchemy"""
    print("Testing SQLAlchemy...")
    try:
        import sqlalchemy
        print(f"SUCCESS: SQLAlchemy {sqlalchemy.__version__} available")
        return True
    except ImportError as e:
        print(f"FAILED: SQLAlchemy not available - {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("Testing environment variables...")
    db_url = os.environ.get('DATABASE_URL')
    async_db_url = os.environ.get('ASYNC_DATABASE_URL')
    
    print(f"DATABASE_URL: {db_url}")
    print(f"ASYNC_DATABASE_URL: {async_db_url}")
    
    if not db_url:
        print("WARNING: DATABASE_URL not set")
    if not async_db_url:
        print("WARNING: ASYNC_DATABASE_URL not set")
    
    return db_url is not None or async_db_url is not None

def test_config():
    """Test config loading"""
    print("Testing config...")
    try:
        from backend_app.config import settings
        print(f"SUCCESS: Config loaded, DATABASE_URL={settings.DATABASE_URL}")
        return True
    except Exception as e:
        print(f"FAILED: Config loading failed - {e}")
        return False

def test_db_connection():
    """Test database connection"""
    print("Testing database connection...")
    try:
        from backend_app.db.connection import engine
        print("SUCCESS: Database engine created")
        return True
    except Exception as e:
        print(f"FAILED: Database connection failed - {e}")
        return False

def test_chatbot_controller():
    """Test chatbot controller"""
    print("Testing chatbot controller...")
    try:
        from backend_app.chatbot.controller import ChatbotController
        print("SUCCESS: ChatbotController imported")
        return True
    except Exception as e:
        print(f"FAILED: ChatbotController import failed - {e}")
        return False

def test_skill_registry():
    """Test skill registry"""
    print("Testing skill registry...")
    try:
        from backend_app.chatbot.skill_registry import initialize_chatbot_system
        success = initialize_chatbot_system()
        if success:
            print("SUCCESS: Skill registry initialized")
        else:
            print("FAILED: Skill registry initialization failed")
        return success
    except Exception as e:
        print(f"FAILED: Skill registry test failed - {e}")
        return False

def main():
    """Main test function"""
    print("="*60)
    print("CHATBOT DIAGNOSTIC - SIMPLE VERSION")
    print("="*60)
    
    tests = [
        ("asyncpg driver", test_asyncpg),
        ("psycopg2 driver", test_psycopg2),
        ("SQLAlchemy", test_sqlalchemy),
        ("Environment", test_environment),
        ("Config", test_config),
        ("Database Connection", test_db_connection),
        ("Chatbot Controller", test_chatbot_controller),
        ("Skill Registry", test_skill_registry)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"EXCEPTION: {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    print("\nDetailed results:")
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
    
    # Identify issues
    issues = []
    if not any(name == "asyncpg driver" and result for name, result in results):
        issues.append("MISSING: asyncpg driver")
    
    if not any(name == "Config" and result for name, result in results):
        issues.append("MISSING: Config loading")
    
    if not any(name == "Database Connection" and result for name, result in results):
        issues.append("MISSING: Database connection")
    
    if issues:
        print(f"\nISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    
    return len(issues)

if __name__ == "__main__":
    try:
        issue_count = main()
        if issue_count == 0:
            print("\nSystem appears to be working!")
            sys.exit(0)
        else:
            print(f"\nFound {issue_count} issue(s)")
            sys.exit(1)
    except Exception as e:
        print(f"Script failed: {e}")
        traceback.print_exc()
        sys.exit(1)