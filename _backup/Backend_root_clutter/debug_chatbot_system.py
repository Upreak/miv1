#!/usr/bin/env python3
"""
Chatbot System Diagnostic Script
Comprehensive validation of all chatbot components and fixes
"""

import sys
import logging
import traceback
from typing import Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChatbotDiagnostic:
    """Comprehensive diagnostic for chatbot system"""
    
    def __init__(self):
        self.results = []
        self.errors = []
    
    def log_result(self, test_name: str, success: bool, message: str, details: Dict[str, Any] = None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {}
        }
        self.results.append(result)
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{status}: {test_name} - {message}")
        if not success:
            self.errors.append(result)
    
    def test_api_route_registration(self) -> bool:
        """Test if chatbot API routes are properly registered"""
        try:
            from backend_app.api import api_router
            
            # Check if chatbot routes are included
            route_paths = [route.path for route in api_router.routes]
            chatbot_routes = [path for path in route_paths if 'chatbot' in path]
            
            if chatbot_routes:
                self.log_result(
                    "API Route Registration",
                    True,
                    f"Found {len(chatbot_routes)} chatbot routes",
                    {'routes': chatbot_routes}
                )
                return True
            else:
                self.log_result(
                    "API Route Registration",
                    False,
                    "No chatbot routes found in main API router",
                    {'all_routes': route_paths}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "API Route Registration",
                False,
                f"Error testing API routes: {str(e)}",
                {'error': str(e)}
            )
            return False
    
    def test_webhook_endpoints(self) -> bool:
        """Test if WhatsApp and Telegram webhook endpoints exist"""
        try:
            # Test WhatsApp webhook
            whatsapp_exists = False
            telegram_exists = False
            
            try:
                from backend_app.api.v1 import whatsapp
                whatsapp_exists = hasattr(whatsapp, 'router')
            except ImportError:
                pass
            
            try:
                from backend_app.api.v1 import telegram
                telegram_exists = hasattr(telegram, 'router')
            except ImportError:
                pass
            
            success = whatsapp_exists and telegram_exists
            
            self.log_result(
                "Webhook Endpoints",
                success,
                f"WhatsApp: {'✓' if whatsapp_exists else '✗'}, Telegram: {'✓' if telegram_exists else '✗'}",
                {'whatsapp_exists': whatsapp_exists, 'telegram_exists': telegram_exists}
            )
            
            return success
            
        except Exception as e:
            self.log_result(
                "Webhook Endpoints",
                False,
                f"Error testing webhook endpoints: {str(e)}",
                {'error': str(e)}
            )
            return False
    
    def test_database_models(self) -> bool:
        """Test if chatbot database models are properly registered"""
        try:
            from backend_app.db.models import Session, MessageLog
            
            # Check if models have required attributes
            session_attrs = hasattr(Session, 'sid') and hasattr(Session, 'channel')
            message_attrs = hasattr(MessageLog, 'id') and hasattr(MessageLog, 'content')
            
            success = session_attrs and message_attrs
            
            self.log_result(
                "Database Models",
                success,
                f"Session: {'✓' if session_attrs else '✗'}, MessageLog: {'✓' if message_attrs else '✗'}",
                {
                    'session_has_sid': session_attrs,
                    'message_has_id': message_attrs
                }
            )
            
            return success
            
        except ImportError as e:
            self.log_result(
                "Database Models",
                False,
                f"Could not import models: {str(e)}",
                {'error': str(e)}
            )
            return False
        except Exception as e:
            self.log_result(
                "Database Models",
                False,
                f"Error testing models: {str(e)}",
                {'error': str(e)}
            )
            return False
    
    def test_skill_registration(self) -> bool:
        """Test if skills are properly registered"""
        try:
            from backend_app.chatbot.skill_registry import (
                get_skill_registry,
                validate_skill_registration
            )
            
            # Get skill registry
            skill_registry = get_skill_registry()
            if not skill_registry:
                self.log_result(
                    "Skill Registration",
                    False,
                    "Could not get skill registry",
                    {}
                )
                return False
            
            # Get registered skills
            registered_skills = skill_registry.get_all()
            skill_names = [skill.name for skill in registered_skills]
            
            # Check for expected skills
            expected_skills = [
                'onboarding_skill',
                'resume_intake_skill'
            ]
            
            missing_skills = [skill for skill in expected_skills if skill not in skill_names]
            success = len(missing_skills) == 0
            
            self.log_result(
                "Skill Registration",
                success,
                f"Registered: {len(registered_skills)}, Missing: {missing_skills}",
                {
                    'registered_skills': skill_names,
                    'missing_skills': missing_skills,
                    'total_registered': len(registered_skills)
                }
            )
            
            return success
            
        except Exception as e:
            self.log_result(
                "Skill Registration",
                False,
                f"Error testing skill registration: {str(e)}",
                {'error': str(e)}
            )
            return False
    
    def test_controller_initialization(self) -> bool:
        """Test if chatbot controller can be initialized"""
        try:
            from backend_app.chatbot.controller import ChatbotController
            
            # Try to initialize controller (this will test all dependencies)
            controller = ChatbotController()
            
            # Check if controller has required attributes
            has_methods = all([
                hasattr(controller, 'start_session'),
                hasattr(controller, 'process_message'),
                hasattr(controller, 'get_session'),
                hasattr(controller, 'update_session_state')
            ])
            
            self.log_result(
                "Controller Initialization",
                has_methods,
                "Controller initialized successfully" if has_methods else "Missing required methods",
                {
                    'has_start_session': hasattr(controller, 'start_session'),
                    'has_process_message': hasattr(controller, 'process_message'),
                    'has_get_session': hasattr(controller, 'get_session'),
                    'has_update_session_state': hasattr(controller, 'update_session_state')
                }
            )
            
            return has_methods
            
        except Exception as e:
            self.log_result(
                "Controller Initialization",
                False,
                f"Error initializing controller: {str(e)}",
                {'error': str(e), 'traceback': traceback.format_exc()}
            )
            return False
    
    def test_skill_dependencies(self) -> bool:
        """Test if all skill dependencies are available"""
        try:
            # Test base skill
            from backend_app.chatbot.services.skills.base_skill import BaseSkill
            base_skill_ok = hasattr(BaseSkill, 'can_handle') and hasattr(BaseSkill, 'handle')
            
            # Test specific skills
            skills_to_test = [
                'onboarding_skill',
                'resume_intake_skill'
            ]
            
            skill_results = {}
            all_skills_ok = True
            
            for skill_name in skills_to_test:
                try:
                    skill_module = __import__(
                        f'backend_app.chatbot.services.skills.{skill_name}',
                        fromlist=[skill_name.title().replace('_', '')]
                    )
                    skill_class = getattr(skill_module, skill_name.title().replace('_', ''))
                    skill_ok = issubclass(skill_class, BaseSkill)
                    skill_results[skill_name] = skill_ok
                    if not skill_ok:
                        all_skills_ok = False
                except Exception as e:
                    skill_results[skill_name] = False
                    all_skills_ok = False
            
            self.log_result(
                "Skill Dependencies",
                all_skills_ok and base_skill_ok,
                f"Base skill: {'✓' if base_skill_ok else '✗'}, Skills: {skill_results}",
                {
                    'base_skill_ok': base_skill_ok,
                    'skill_results': skill_results
                }
            )
            
            return all_skills_ok and base_skill_ok
            
        except Exception as e:
            self.log_result(
                "Skill Dependencies",
                False,
                f"Error testing skill dependencies: {str(e)}",
                {'error': str(e)}
            )
            return False
    
    def test_enum_imports(self) -> bool:
        """Test if required enums are properly imported"""
        try:
            from backend_app.chatbot.models.session_model import UserRole, ConversationState
            
            # Check if enums have required values
            user_roles = [role.value for role in UserRole]
            conversation_states = [state.value for state in ConversationState]
            
            expected_roles = ['candidate', 'recruiter', 'unknown']
            expected_states = ['onboarding', 'awaiting_resume', 'profile_ready']
            
            roles_ok = all(role in user_roles for role in expected_roles)
            states_ok = all(state in conversation_states for state in expected_states)
            
            success = roles_ok and states_ok
            
            self.log_result(
                "Enum Imports",
                success,
                f"UserRoles: {'✓' if roles_ok else '✗'}, States: {'✓' if states_ok else '✗'}",
                {
                    'available_roles': user_roles,
                    'available_states': conversation_states,
                    'roles_ok': roles_ok,
                    'states_ok': states_ok
                }
            )
            
            return success
            
        except Exception as e:
            self.log_result(
                "Enum Imports",
                False,
                f"Error testing enum imports: {str(e)}",
                {'error': str(e)}
            )
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all diagnostic tests"""
        logger.info("Starting chatbot system diagnostic...")
        
        tests = [
            ("API Route Registration", self.test_api_route_registration),
            ("Webhook Endpoints", self.test_webhook_endpoints),
            ("Database Models", self.test_database_models),
            ("Skill Registration", self.test_skill_registration),
            ("Controller Initialization", self.test_controller_initialization),
            ("Skill Dependencies", self.test_skill_dependencies),
            ("Enum Imports", self.test_enum_imports)
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}")
                results[test_name] = False
                self.log_result(test_name, False, f"Exception: {str(e)}", {'error': str(e)})
        
        # Summary
        total_tests = len(tests)
        passed_tests = sum(1 for result in results.values() if result)
        failed_tests = total_tests - passed_tests
        
        logger.info(f"\nDiagnostic Summary:")
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            logger.warning("Failed tests:")
            for test_name, result in results.items():
                if not result:
                    logger.warning(f"  - {test_name}")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'test_results': results,
            'detailed_results': self.results,
            'errors': self.errors
        }


def main():
    """Main diagnostic function"""
    try:
        diagnostic = ChatbotDiagnostic()
        results = diagnostic.run_all_tests()
        
        # Print detailed results
        print("\n" + "="*60)
        print("DETAILED DIAGNOSTIC RESULTS")
        print("="*60)
        
        for result in diagnostic.results:
            status = "PASS" if result['success'] else "FAIL"
            # Use ASCII characters only to avoid encoding issues
            status_symbol = "[PASS]" if result['success'] else "[FAIL]"
            print(f"\n{status_symbol} {status}: {result['test']}")
            print(f"  Message: {result['message']}")
            if result['details']:
                print(f"  Details: {result['details']}")
        
        # Exit with appropriate code
        if results['failed_tests'] == 0:
            print(f"\n🎉 All tests passed! Chatbot system is ready.")
            sys.exit(0)
        else:
            print(f"\n❌ {results['failed_tests']} test(s) failed. Please review the issues above.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Diagnostic failed with exception: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()