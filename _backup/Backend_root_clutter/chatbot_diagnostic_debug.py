#!/usr/bin/env python3
"""
Chatbot Diagnostic Debug Script
Comprehensive analysis with detailed logging to identify root causes
"""

import sys
import logging
import os
import traceback
from typing import Dict, Any, List

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

def log_section(title: str):
    """Log section divider"""
    print(f"\n{'='*60}")
    print(f"DEBUGGING: {title}")
    print('='*60)

def log_subsection(title: str):
    """Log subsection divider"""
    print(f"\n{'-'*40}")
    print(f"SUBSECTION: {title}")
    print('-'*40)

def test_environment_variables():
    """Test environment variable configuration"""
    log_section("ENVIRONMENT VARIABLES")
    
    env_vars = {
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'ASYNC_DATABASE_URL': os.environ.get('ASYNC_DATABASE_URL'),
        'PYTHONPATH': os.environ.get('PYTHONPATH'),
        'PATH': os.environ.get('PATH', '')[:100] + '...' if os.environ.get('PATH') else None
    }
    
    for var, value in env_vars.items():
        print(f"{var}: {value}")
        logger.info(f"{var}: {value}")
    
    return env_vars

def test_python_path():
    """Test Python path configuration"""
    log_section("PYTHON PATH")
    
    print("Python executable:", sys.executable)
    print("Python version:", sys.version)
    print("Python path:")
    for path in sys.path:
        print(f"  {path}")
    
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Python version: {sys.version}")

def test_driver_availability():
    """Test database driver availability"""
    log_section("DATABASE DRIVER AVAILABILITY")
    
    drivers = {}
    
    # Test asyncpg
    try:
        import asyncpg
        drivers['asyncpg'] = {
            'available': True,
            'version': getattr(asyncpg, '__version__', 'unknown'),
            'path': asyncpg.__file__
        }
        print("✓ asyncpg available")
        logger.info("asyncpg imported successfully")
    except ImportError as e:
        drivers['asyncpg'] = {
            'available': False,
            'error': str(e)
        }
        print(f"✗ asyncpg not available: {e}")
        logger.error(f"asyncpg import failed: {e}")
    
    # Test psycopg2
    try:
        import psycopg2
        drivers['psycopg2'] = {
            'available': True,
            'version': getattr(psycopg2, '__version__', 'unknown'),
            'path': psycopg2.__file__
        }
        print("✓ psycopg2 available")
        logger.info("psycopg2 imported successfully")
    except ImportError as e:
        drivers['psycopg2'] = {
            'available': False,
            'error': str(e)
        }
        print(f"✗ psycopg2 not available: {e}")
        logger.error(f"psycopg2 import failed: {e}")
    
    # Test SQLAlchemy
    try:
        import sqlalchemy
        drivers['sqlalchemy'] = {
            'available': True,
            'version': sqlalchemy.__version__,
            'path': sqlalchemy.__file__
        }
        print(f"✓ SQLAlchemy available: {sqlalchemy.__version__}")
        logger.info(f"SQLAlchemy imported: {sqlalchemy.__version__}")
    except ImportError as e:
        drivers['sqlalchemy'] = {
            'available': False,
            'error': str(e)
        }
        print(f"✗ SQLAlchemy not available: {e}")
        logger.error(f"SQLAlchemy import failed: {e}")
    
    return drivers

def test_database_url_parsing():
    """Test database URL parsing and driver selection"""
    log_section("DATABASE URL PARSING")
    
    env_vars = test_environment_variables()
    
    urls_to_test = []
    if env_vars.get('DATABASE_URL'):
        urls_to_test.append(('DATABASE_URL', env_vars['DATABASE_URL']))
    if env_vars.get('ASYNC_DATABASE_URL'):
        urls_to_test.append(('ASYNC_DATABASE_URL', env_vars['ASYNC_DATABASE_URL']))
    
    # Default URL from config
    default_url = "postgresql://user:password@localhost:5432/recruitment_db"
    urls_to_test.append(('DEFAULT_CONFIG', default_url))
    
    url_analysis = {}
    
    for source, url in urls_to_test:
        print(f"\nAnalyzing {source}: {url}")
        
        analysis = {
            'source': source,
            'url': url,
            'has_asyncpg': 'asyncpg' in url,
            'has_psycopg2': 'psycopg2' in url,
            'is_postgresql': 'postgresql' in url,
            'has_credentials': '@' in url and '://' in url,
            'driver_suggestion': None
        }
        
        if 'asyncpg' in url:
            analysis['driver_suggestion'] = 'asyncpg'
            print(f"  → Uses asyncpg driver")
        elif 'psycopg2' in url:
            analysis['driver_suggestion'] = 'psycopg2'
            print(f"  → Uses psycopg2 driver")
        elif 'postgresql' in url:
            analysis['driver_suggestion'] = 'asyncpg (recommended for async)'
            print(f"  → PostgreSQL URL, recommends asyncpg for async")
        else:
            analysis['driver_suggestion'] = 'Unknown driver'
            print(f"  → Unknown driver")
        
        url_analysis[source] = analysis
        logger.info(f"URL analysis for {source}: {analysis}")
    
    return url_analysis

def test_import_chain():
    """Test the import chain for chatbot components"""
    log_section("IMPORT CHAIN ANALYSIS")
    
    imports_to_test = [
        ('backend_app.config', 'settings'),
        ('backend_app.db.connection', 'engine'),
        ('backend_app.db.models', 'Base'),
        ('backend_app.chatbot.skill_registry', 'get_skill_registry'),
        ('backend_app.chatbot.controller', 'ChatbotController'),
        ('backend_app.api.v1.chatbot', 'router'),
        ('backend_app.api.v1.whatsapp', 'router'),
        ('backend_app.api.v1.telegram', 'router')
    ]
    
    import_results = {}
    
    for module_name, attribute in imports_to_test:
        try:
            log_subsection(f"Testing {module_name}.{attribute}")
            
            # Import module
            module = __import__(module_name, fromlist=[attribute])
            
            # Get attribute if specified
            if attribute:
                attr = getattr(module, attribute)
                import_results[module_name] = {
                    'success': True,
                    'attribute': attribute,
                    'type': type(attr).__name__,
                    'path': getattr(module, '__file__', 'built-in')
                }
                print(f"✓ {module_name}.{attribute} imported successfully")
                logger.info(f"✓ {module_name}.{attribute} imported")
            else:
                import_results[module_name] = {
                    'success': True,
                    'path': getattr(module, '__file__', 'built-in')
                }
                print(f"✓ {module_name} imported successfully")
                logger.info(f"✓ {module_name} imported")
                
        except Exception as e:
            import_results[module_name] = {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            print(f"✗ {module_name} failed: {e}")
            logger.error(f"✗ {module_name} failed: {e}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
    
    return import_results

def test_database_engine_creation():
    """Test database engine creation"""
    log_section("DATABASE ENGINE CREATION")
    
    try:
        from backend_app.config import settings
        from sqlalchemy.ext.asyncio import create_async_engine
        
        print(f"Using DATABASE_URL: {settings.DATABASE_URL}")
        
        # Test engine creation
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=True,  # Enable echo for debugging
            future=True
        )
        
        print("✓ Async engine created successfully")
        logger.info("Async engine created successfully")
        
        # Test if we can inspect the engine
        print(f"Engine URL: {engine.url}")
        print(f"Engine dialect: {engine.dialect.name}")
        print(f"Engine driver: {engine.dialect.driver}")
        
        return {
            'success': True,
            'url': str(engine.url),
            'dialect': engine.dialect.name,
            'driver': engine.dialect.driver
        }
        
    except Exception as e:
        print(f"✗ Engine creation failed: {e}")
        logger.error(f"Engine creation failed: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def test_skill_registry_initialization():
    """Test skill registry initialization"""
    log_section("SKILL REGISTRY INITIALIZATION")
    
    try:
        from backend_app.chatbot.skill_registry import initialize_chatbot_system, get_skill_registry
        
        print("Testing skill registry initialization...")
        
        # Initialize system
        success = initialize_chatbot_system()
        print(f"System initialization: {'✓' if success else '✗'}")
        
        if success:
            registry = get_skill_registry()
            if registry:
                skills = registry.get_all()
                print(f"Found {len(skills)} skills: {[skill.name for skill in skills]}")
                
                # Test each skill
                skill_details = {}
                for skill in skills:
                    try:
                        skill_details[skill.name] = {
                            'can_handle_method': hasattr(skill, 'can_handle'),
                            'handle_method': hasattr(skill, 'handle'),
                            'name': skill.name,
                            'priority': getattr(skill, 'priority', 'unknown')
                        }
                    except Exception as e:
                        skill_details[skill.name] = {'error': str(e)}
                
                return {
                    'success': True,
                    'skills_count': len(skills),
                    'skills': skill_details
                }
            else:
                print("✗ Could not get skill registry")
                return {'success': False, 'error': 'No registry'}
        else:
            print("✗ System initialization failed")
            return {'success': False, 'error': 'Initialization failed'}
            
    except Exception as e:
        print(f"✗ Skill registry test failed: {e}")
        logger.error(f"Skill registry test failed: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def test_controller_initialization():
    """Test controller initialization"""
    log_section("CONTROLLER INITIALIZATION")
    
    try:
        from backend_app.chatbot.controller import ChatbotController
        
        print("Testing controller initialization...")
        
        # This will test all dependencies
        controller = ChatbotController()
        
        print("✓ Controller initialized successfully")
        
        # Check methods
        methods = ['start_session', 'process_message', 'get_session', 'update_session_state']
        method_details = {}
        
        for method in methods:
            has_method = hasattr(controller, method)
            method_details[method] = has_method
            print(f"  {method}: {'✓' if has_method else '✗'}")
        
        return {
            'success': True,
            'methods': method_details
        }
        
    except Exception as e:
        print(f"✗ Controller initialization failed: {e}")
        logger.error(f"Controller initialization failed: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def main():
    """Main diagnostic function"""
    print("CHATBOT SYSTEM DIAGNOSTIC DEBUG")
    print("="*60)
    print("This script will identify the root cause of chatbot issues")
    print("="*60)
    
    # Run all diagnostic tests
    results = {}
    
    try:
        results['environment'] = test_environment_variables()
        results['python_path'] = test_python_path()
        results['drivers'] = test_driver_availability()
        results['url_parsing'] = test_database_url_parsing()
        results['imports'] = test_import_chain()
        results['engine'] = test_database_engine_creation()
        results['skill_registry'] = test_skill_registry_initialization()
        results['controller'] = test_controller_initialization()
        
    except Exception as e:
        print(f"\nFatal error during diagnostics: {e}")
        logger.error(f"Fatal error: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        results['fatal_error'] = str(e)
    
    # Generate summary report
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY REPORT")
    print("="*60)
    
    # Analyze results for common issues
    issues_found = []
    
    # Check for asyncpg availability
    if 'drivers' in results:
        if not results['drivers'].get('asyncpg', {}).get('available', False):
            issues_found.append("MISSING: asyncpg driver not installed")
        
        if results['drivers'].get('psycopg2', {}).get('available', False):
            issues_found.append("CONFLICT: psycopg2 (sync driver) may conflict with async setup")
    
    # Check for environment variables
    if 'environment' in results:
        env = results['environment']
        if not env.get('DATABASE_URL'):
            issues_found.append("MISSING: DATABASE_URL environment variable")
        if not env.get('ASYNC_DATABASE_URL'):
            issues_found.append("MISSING: ASYNC_DATABASE_URL environment variable")
    
    # Check import failures
    if 'imports' in results:
        failed_imports = [name for name, result in results['imports'].items() if not result.get('success', False)]
        if failed_imports:
            issues_found.append(f"IMPORT FAILURES: {', '.join(failed_imports)}")
    
    # Check engine creation
    if 'engine' in results and not results['engine'].get('success', False):
        issues_found.append(f"ENGINE FAILURE: {results['engine'].get('error', 'Unknown')}")
    
    # Check skill registry
    if 'skill_registry' in results and not results['skill_registry'].get('success', False):
        issues_found.append(f"SKILL REGISTRY FAILURE: {results['skill_registry'].get('error', 'Unknown')}")
    
    # Check controller
    if 'controller' in results and not results['controller'].get('success', False):
        issues_found.append(f"CONTROLLER FAILURE: {results['controller'].get('error', 'Unknown')}")
    
    # Print issues
    if issues_found:
        print("\n🚨 ISSUES IDENTIFIED:")
        for i, issue in enumerate(issues_found, 1):
            print(f"  {i}. {issue}")
    else:
        print("\n✅ No critical issues found")
    
    # Save detailed results
    try:
        import json
        with open('chatbot_diagnostic_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Detailed results saved to: chatbot_diagnostic_results.json")
    except Exception as e:
        print(f"\n⚠️  Could not save results file: {e}")
    
    # Final recommendation
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    if "MISSING: asyncpg driver not installed" in issues_found:
        print("1. Install asyncpg: pip install asyncpg==0.29.0")
    
    if "CONFLICT: psycopg2 (sync driver) may conflict with async setup" in issues_found:
        print("2. Remove psycopg2 from requirements or use only asyncpg")
    
    if any("MISSING: " in issue for issue in issues_found):
        print("3. Set environment variables: DATABASE_URL and ASYNC_DATABASE_URL")
        print("   Example: export DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db")
    
    if any("IMPORT FAILURES" in issue for issue in issues_found):
        print("4. Fix import errors by checking module paths and dependencies")
    
    if any("ENGINE FAILURE" in issue for issue in issues_found):
        print("5. Check database connection and credentials")
    
    return len(issues_found)

if __name__ == "__main__":
    try:
        issue_count = main()
        if issue_count == 0:
            print("\n🎉 System appears to be working correctly!")
            sys.exit(0)
        else:
            print(f"\n❌ Found {issue_count} issue(s) that need attention")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Diagnostic script failed: {e}")
        traceback.print_exc()
        sys.exit(1)