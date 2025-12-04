#!/usr/bin/env python3
"""
Comprehensive Test Suite for Chat Bot/Co-Pilot Module
Tests chat functionality, skills, and integration
"""

import sys
import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ChatBotTestSuite:
    """
    Comprehensive test suite for chat bot/co-pilot module
    """
    
    def __init__(self):
        """Initialize test suite"""
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.start_time = None
        
        # Test data
        self.test_messages = [
            # Onboarding tests
            {"message": "hello", "expected_intent": "welcome", "context": {"is_first_message": True}},
            {"message": "hi there", "expected_intent": "welcome", "context": {"is_first_message": True}},
            {"message": "I'm a candidate looking for a job", "expected_intent": "role_selected", "context": {"session_state": "ONBOARDING"}},
            {"message": "I'm a recruiter", "expected_intent": "role_selected", "context": {"session_state": "ONBOARDING"}},
            {"message": "My name is John", "expected_intent": "name_collected", "context": {"session_state": "ONBOARDING", "setup_step": "name"}},
            {"message": "john.doe@example.com", "expected_intent": "email_collected", "context": {"session_state": "ONBOARDING", "setup_step": "email"}},
            
            # Resume intake tests
            {"message": "I want to upload my resume", "expected_intent": "resume_upload_request", "context": {"user_role": "candidate"}},
            {"message": "send my resume", "expected_intent": "resume_upload_request", "context": {"user_role": "candidate"}},
            {"message": "upload cv", "expected_intent": "resume_upload_request", "context": {"user_role": "candidate"}},
            
            # Job creation tests
            {"message": "I want to post a job", "expected_intent": "job_creation_start", "context": {"user_role": "recruiter"}},
            {"message": "create a new job posting", "expected_intent": "job_creation_start", "context": {"user_role": "recruiter"}},
            {"message": "hiring for software engineer", "expected_intent": "job_title_collected", "context": {"user_role": "recruiter", "session_state": "JOB_CREATION"}},
            
            # Candidate matching tests
            {"message": "find candidates for software engineer", "expected_intent": "candidate_search_start", "context": {"user_role": "recruiter"}},
            {"message": "show me candidates", "expected_intent": "candidate_search_start", "context": {"user_role": "recruiter"}},
            
            # Application status tests
            {"message": "what's my application status", "expected_intent": "application_status_check", "context": {"user_role": "candidate"}},
            {"message": "check my application", "expected_intent": "application_status_check", "context": {"user_role": "candidate"}},
            
            # General help tests
            {"message": "help", "expected_intent": "help_request", "context": {}},
            {"message": "what can you do", "expected_intent": "help_request", "context": {}},
            {"message": "how do I use this", "expected_intent": "help_request", "context": {}},
        ]
        
        self.error_scenarios = [
            {"message": "", "expected_error": "empty_message"},
            {"message": "   ", "expected_error": "empty_message"},
            {"message": "invalid role xyz", "expected_error": "role_invalid"},
            {"message": "invalid email format", "expected_error": "email_validation_error"},
            {"message": "very long message that might cause issues " * 100, "expected_error": "message_too_long"},
        ]
    
    def setup_test_environment(self):
        """Setup test environment with mocked dependencies"""
        logger.info("Setting up test environment...")
        
        try:
            # Mock database session
            self.mock_db_session = Mock()
            
            # Mock LLM service
            self.mock_llm_service = Mock()
            self.mock_llm_service.generate_response.return_value = {
                "text": "Mocked response",
                "intent": "mock_intent",
                "confidence": 0.9
            }
            
            # Mock skill registry
            self.mock_skill_registry = Mock()
            self.mock_skill_registry.get_skill.return_value = Mock()
            self.mock_skill_registry.get_skill.return_value.handle.return_value = {
                "text": "Skill response",
                "intent": "skill_intent",
                "confidence": 0.8
            }
            
            # Mock session service
            self.mock_session_service = Mock()
            self.mock_session_service.get_or_create.return_value = Mock(
                sid="test_session_123",
                state="IDLE",
                user_role=None
            )
            
            # Mock message repository
            self.mock_message_repo = Mock()
            self.mock_message_repo.create.return_value = Mock(
                id="msg_123",
                sid="test_session_123"
            )
            
            logger.info("Test environment setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup test environment: {e}")
            return False
    
    def test_onboarding_skill(self):
        """Test onboarding skill functionality"""
        logger.info("Testing onboarding skill...")
        
        test_cases = [
            {
                "name": "Welcome message",
                "message": "hello",
                "context": {"is_first_message": True},
                "expected": {
                    "intent": "welcome",
                    "contains": ["Welcome", "AI Recruitment Assistant"]
                }
            },
            {
                "name": "Role selection - candidate",
                "message": "I'm a candidate looking for a job",
                "context": {"session_state": "ONBOARDING"},
                "expected": {
                    "intent": "role_selected",
                    "contains": ["candidate", "job match"],
                    "metadata": {"user_role": "candidate"}
                }
            },
            {
                "name": "Role selection - recruiter",
                "message": "I'm a recruiter",
                "context": {"session_state": "ONBOARDING"},
                "expected": {
                    "intent": "role_selected",
                    "contains": ["recruiter", "candidates"],
                    "metadata": {"user_role": "recruiter"}
                }
            },
            {
                "name": "Invalid role",
                "message": "I'm something else",
                "context": {"session_state": "ONBOARDING"},
                "expected": {
                    "intent": "role_invalid",
                    "contains": ["didn't understand", "Candidate or Recruiter"]
                }
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                # Import the skill
                from backend_app.chatbot.services.skills.onboarding_skill import OnboardingSkill
                
                skill = OnboardingSkill()
                
                # Test if skill can handle
                can_handle = skill.can_handle(
                    test_case["context"].get("session_state"),
                    test_case["message"],
                    test_case["context"]
                )
                
                if not can_handle:
                    results.append({
                        "test": test_case["name"],
                        "status": "FAILED",
                        "reason": "Skill cannot handle the message"
                    })
                    continue
                
                # Test skill handling
                response = skill.handle(
                    "test_session_123",
                    test_case["message"],
                    test_case["context"]
                )
                
                # Validate response
                success = True
                validation_details = []
                
                # Check intent
                if response.get("intent") != test_case["expected"]["intent"]:
                    success = False
                    validation_details.append(f"Intent mismatch: expected {test_case['expected']['intent']}, got {response.get('intent')}")
                
                # Check required content
                for content in test_case["expected"].get("contains", []):
                    if content.lower() not in response.get("text", "").lower():
                        success = False
                        validation_details.append(f"Missing content: '{content}'")
                
                # Check metadata
                if "metadata" in test_case["expected"]:
                    for key, value in test_case["expected"]["metadata"].items():
                        if response.get("metadata", {}).get(key) != value:
                            success = False
                            validation_details.append(f"Metadata mismatch: {key}={value}")
                
                results.append({
                    "test": test_case["name"],
                    "status": "PASSED" if success else "FAILED",
                    "details": validation_details if not success else "All validations passed",
                    "response": response
                })
                
            except Exception as e:
                results.append({
                    "test": test_case["name"],
                    "status": "ERROR",
                    "details": str(e)
                })
        
        return results
    
    def test_resume_intake_skill(self):
        """Test resume intake skill functionality"""
        logger.info("Testing resume intake skill...")
        
        test_cases = [
            {
                "name": "Resume upload request",
                "message": "I want to upload my resume",
                "context": {"user_role": "candidate"},
                "expected": {
                    "intent": "resume_upload_request",
                    "contains": ["upload", "resume", "PDF", "DOC"]
                }
            },
            {
                "name": "CV upload request",
                "message": "send my cv",
                "context": {"user_role": "candidate"},
                "expected": {
                    "intent": "resume_upload_request",
                    "contains": ["upload", "resume", "PDF", "DOC"]
                }
            },
            {
                "name": "File validation success",
                "message": "resume.pdf",
                "context": {"user_role": "candidate", "session_state": "AWAITING_RESUME"},
                "expected": {
                    "intent": "file_validation_success",
                    "contains": ["Great", "received", "resume"]
                }
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                # Import the skill
                from backend_app.chatbot.services.skills.resume_intake_skill import ResumeIntakeSkill
                
                skill = ResumeIntakeSkill()
                
                # Test if skill can handle
                can_handle = skill.can_handle(
                    test_case["context"].get("session_state"),
                    test_case["message"],
                    test_case["context"]
                )
                
                if not can_handle:
                    results.append({
                        "test": test_case["name"],
                        "status": "FAILED",
                        "reason": "Skill cannot handle the message"
                    })
                    continue
                
                # Test skill handling
                response = skill.handle(
                    "test_session_123",
                    test_case["message"],
                    test_case["context"]
                )
                
                # Validate response
                success = True
                validation_details = []
                
                # Check intent
                if response.get("intent") != test_case["expected"]["intent"]:
                    success = False
                    validation_details.append(f"Intent mismatch: expected {test_case['expected']['intent']}, got {response.get('intent')}")
                
                # Check required content
                for content in test_case["expected"].get("contains", []):
                    if content.lower() not in response.get("text", "").lower():
                        success = False
                        validation_details.append(f"Missing content: '{content}'")
                
                results.append({
                    "test": test_case["name"],
                    "status": "PASSED" if success else "FAILED",
                    "details": validation_details if not success else "All validations passed",
                    "response": response
                })
                
            except Exception as e:
                results.append({
                    "test": test_case["name"],
                    "status": "ERROR",
                    "details": str(e)
                })
        
        return results
    
    def test_job_creation_skill(self):
        """Test job creation skill functionality"""
        logger.info("Testing job creation skill...")
        
        test_cases = [
            {
                "name": "Job creation start",
                "message": "I want to post a job",
                "context": {"user_role": "recruiter"},
                "expected": {
                    "intent": "job_creation_start",
                    "contains": ["job", "post", "create", "position"]
                }
            },
            {
                "name": "Job title collection",
                "message": "Software Engineer",
                "context": {"user_role": "recruiter", "session_state": "JOB_CREATION"},
                "expected": {
                    "intent": "job_title_collected",
                    "contains": ["title", "software engineer", "next step"]
                }
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                # Import the skill
                from backend_app.chatbot.services.skills.job_creation_skill import JobCreationSkill
                
                skill = JobCreationSkill()
                
                # Test if skill can handle
                can_handle = skill.can_handle(
                    test_case["context"].get("session_state"),
                    test_case["message"],
                    test_case["context"]
                )
                
                if not can_handle:
                    results.append({
                        "test": test_case["name"],
                        "status": "FAILED",
                        "reason": "Skill cannot handle the message"
                    })
                    continue
                
                # Test skill handling
                response = skill.handle(
                    "test_session_123",
                    test_case["message"],
                    test_case["context"]
                )
                
                # Validate response
                success = True
                validation_details = []
                
                # Check intent
                if response.get("intent") != test_case["expected"]["intent"]:
                    success = False
                    validation_details.append(f"Intent mismatch: expected {test_case['expected']['intent']}, got {response.get('intent')}")
                
                # Check required content
                for content in test_case["expected"].get("contains", []):
                    if content.lower() not in response.get("text", "").lower():
                        success = False
                        validation_details.append(f"Missing content: '{content}'")
                
                results.append({
                    "test": test_case["name"],
                    "status": "PASSED" if success else "FAILED",
                    "details": validation_details if not success else "All validations passed",
                    "response": response
                })
                
            except Exception as e:
                results.append({
                    "test": test_case["name"],
                    "status": "ERROR",
                    "details": str(e)
                })
        
        return results
    
    def test_candidate_matching_skill(self):
        """Test candidate matching skill functionality"""
        logger.info("Testing candidate matching skill...")
        
        test_cases = [
            {
                "name": "Candidate search start",
                "message": "find candidates for software engineer",
                "context": {"user_role": "recruiter"},
                "expected": {
                    "intent": "candidate_search_start",
                    "contains": ["candidates", "find", "search", "software engineer"]
                }
            },
            {
                "name": "Skill-based matching",
                "message": "candidates with Python and React skills",
                "context": {"user_role": "recruiter", "session_state": "CANDIDATE_MATCHING"},
                "expected": {
                    "intent": "skill_based_matching",
                    "contains": ["skills", "python", "react", "matching"]
                }
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                # Import the skill
                from backend_app.chatbot.services.skills.candidate_matching_skill import CandidateMatchingSkill
                
                skill = CandidateMatchingSkill()
                
                # Test if skill can handle
                can_handle = skill.can_handle(
                    test_case["context"].get("session_state"),
                    test_case["message"],
                    test_case["context"]
                )
                
                if not can_handle:
                    results.append({
                        "test": test_case["name"],
                        "status": "FAILED",
                        "reason": "Skill cannot handle the message"
                    })
                    continue
                
                # Test skill handling
                response = skill.handle(
                    "test_session_123",
                    test_case["message"],
                    test_case["context"]
                )
                
                # Validate response
                success = True
                validation_details = []
                
                # Check intent
                if response.get("intent") != test_case["expected"]["intent"]:
                    success = False
                    validation_details.append(f"Intent mismatch: expected {test_case['expected']['intent']}, got {response.get('intent')}")
                
                # Check required content
                for content in test_case["expected"].get("contains", []):
                    if content.lower() not in response.get("text", "").lower():
                        success = False
                        validation_details.append(f"Missing content: '{content}'")
                
                results.append({
                    "test": test_case["name"],
                    "status": "PASSED" if success else "FAILED",
                    "details": validation_details if not success else "All validations passed",
                    "response": response
                })
                
            except Exception as e:
                results.append({
                    "test": test_case["name"],
                    "status": "ERROR",
                    "details": str(e)
                })
        
        return results
    
    def test_application_status_skill(self):
        """Test application status skill functionality"""
        logger.info("Testing application status skill...")
        
        test_cases = [
            {
                "name": "Application status check",
                "message": "what's my application status",
                "context": {"user_role": "candidate"},
                "expected": {
                    "intent": "application_status_check",
                    "contains": ["application", "status", "check", "track"]
                }
            },
            {
                "name": "Interview scheduling",
                "message": "schedule an interview",
                "context": {"user_role": "candidate", "session_state": "APPLICATION_STATUS"},
                "expected": {
                    "intent": "interview_scheduling",
                    "contains": ["interview", "schedule", "available", "time"]
                }
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                # Import the skill
                from backend_app.chatbot.services.skills.application_status_skill import ApplicationStatusSkill
                
                skill = ApplicationStatusSkill()
                
                # Test if skill can handle
                can_handle = skill.can_handle(
                    test_case["context"].get("session_state"),
                    test_case["message"],
                    test_case["context"]
                )
                
                if not can_handle:
                    results.append({
                        "test": test_case["name"],
                        "status": "FAILED",
                        "reason": "Skill cannot handle the message"
                    })
                    continue
                
                # Test skill handling
                response = skill.handle(
                    "test_session_123",
                    test_case["message"],
                    test_case["context"]
                )
                
                # Validate response
                success = True
                validation_details = []
                
                # Check intent
                if response.get("intent") != test_case["expected"]["intent"]:
                    success = False
                    validation_details.append(f"Intent mismatch: expected {test_case['expected']['intent']}, got {response.get('intent')}")
                
                # Check required content
                for content in test_case["expected"].get("contains", []):
                    if content.lower() not in response.get("text", "").lower():
                        success = False
                        validation_details.append(f"Missing content: '{content}'")
                
                results.append({
                    "test": test_case["name"],
                    "status": "PASSED" if success else "FAILED",
                    "details": validation_details if not success else "All validations passed",
                    "response": response
                })
                
            except Exception as e:
                results.append({
                    "test": test_case["name"],
                    "status": "ERROR",
                    "details": str(e)
                })
        
        return results
    
    def test_message_router(self):
        """Test message router functionality"""
        logger.info("Testing message router...")
        
        try:
            from backend_app.chatbot.services.message_router import MessageRouter
            from backend_app.chatbot.models.conversation_state import ConversationState
            
            router = MessageRouter()
            
            test_cases = [
                {
                    "name": "Route onboarding message",
                    "message": "hello",
                    "state": ConversationState.IDLE,
                    "context": {"is_first_message": True},
                    "expected_skill": "onboarding_skill"
                },
                {
                    "name": "Route resume upload message",
                    "message": "upload resume",
                    "state": ConversationState.CANDIDATE_FLOW,
                    "context": {"user_role": "candidate"},
                    "expected_skill": "resume_intake_skill"
                },
                {
                    "name": "Route job creation message",
                    "message": "post a job",
                    "state": ConversationState.RECRUITER_FLOW,
                    "context": {"user_role": "recruiter"},
                    "expected_skill": "job_creation_skill"
                }
            ]
            
            results = []
            for test_case in test_cases:
                try:
                    # Mock skill registry
                    with patch.object(router, 'skill_registry') as mock_registry:
                        mock_skill = Mock()
                        mock_skill.handle.return_value = {
                            "text": "Mocked response",
                            "intent": "mock_intent",
                            "confidence": 0.9
                        }
                        mock_registry.get_skill.return_value = mock_skill
                        
                        # Route message
                        result = router.route_message(
                            test_case["message"],
                            test_case["state"],
                            test_case["context"]
                        )
                        
                        # Check if correct skill was selected
                        if mock_registry.get_skill.called:
                            called_skill = mock_registry.get_skill.call_args[0][0]
                            if called_skill == test_case["expected_skill"]:
                                results.append({
                                    "test": test_case["name"],
                                    "status": "PASSED",
                                    "details": f"Correctly routed to {called_skill}"
                                })
                            else:
                                results.append({
                                    "test": test_case["name"],
                                    "status": "FAILED",
                                    "details": f"Expected {test_case['expected_skill']}, got {called_skill}"
                                })
                        else:
                            results.append({
                                "test": test_case["name"],
                                "status": "FAILED",
                                "details": "No skill was called"
                            })
                
                except Exception as e:
                    results.append({
                        "test": test_case["name"],
                        "status": "ERROR",
                        "details": str(e)
                    })
            
            return results
            
        except Exception as e:
            return [{
                "test": "Message Router Test",
                "status": "ERROR",
                "details": str(e)
            }]
    
    def test_copilot_service(self):
        """Test copilot service functionality"""
        logger.info("Testing copilot service...")
        
        try:
            from backend_app.chatbot.services.copilot_service import CopilotService
            
            copilot = CopilotService()
            
            test_cases = [
                {
                    "name": "Process welcome message",
                    "message": "hello",
                    "context": {"is_first_message": True},
                    "expected": {
                        "intent": "welcome",
                        "has_response": True
                    }
                },
                {
                    "name": "Process role selection",
                    "message": "I'm a candidate",
                    "context": {"session_state": "ONBOARDING"},
                    "expected": {
                        "intent": "role_selected",
                        "has_response": True
                    }
                },
                {
                    "name": "Process help request",
                    "message": "help",
                    "context": {},
                    "expected": {
                        "intent": "help_request",
                        "has_response": True
                    }
                }
            ]
            
            results = []
            for test_case in test_cases:
                try:
                    # Mock dependencies
                    with patch.object(copilot, 'message_router') as mock_router, \
                         patch.object(copilot, 'session_service') as mock_session, \
                         patch.object(copilot, 'message_repository') as mock_message_repo:
                        
                        # Setup mocks
                        mock_session.get_or_create.return_value = Mock(
                            sid="test_session_123",
                            state="IDLE",
                            user_role=None
                        )
                        
                        mock_router.route_message.return_value = {
                            "text": "Mocked response",
                            "intent": test_case["expected"]["intent"],
                            "confidence": 0.9
                        }
                        
                        # Process message
                        result = copilot.process_message(
                            "test_session_123",
                            test_case["message"],
                            test_case["context"]
                        )
                        
                        # Validate result
                        success = True
                        validation_details = []
                        
                        if not result.get("has_response", False):
                            success = False
                            validation_details.append("No response generated")
                        
                        if result.get("intent") != test_case["expected"]["intent"]:
                            success = False
                            validation_details.append(f"Intent mismatch")
                        
                        results.append({
                            "test": test_case["name"],
                            "status": "PASSED" if success else "FAILED",
                            "details": validation_details if not success else "All validations passed",
                            "response": result
                        })
                
                except Exception as e:
                    results.append({
                        "test": test_case["name"],
                        "status": "ERROR",
                        "details": str(e)
                    })
            
            return results
            
        except Exception as e:
            return [{
                "test": "Copilot Service Test",
                "status": "ERROR",
                "details": str(e)
            }]
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        logger.info("Testing error handling...")
        
        test_cases = [
            {
                "name": "Empty message",
                "message": "",
                "expected_error": "empty_message"
            },
            {
                "name": "Whitespace only message",
                "message": "   ",
                "expected_error": "empty_message"
            },
            {
                "name": "Invalid role",
                "message": "I'm an alien",
                "context": {"session_state": "ONBOARDING"},
                "expected_error": "role_invalid"
            },
            {
                "name": "Invalid email",
                "message": "not_an_email",
                "context": {"session_state": "ONBOARDING", "setup_step": "email"},
                "expected_error": "email_validation_error"
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                # Test with onboarding skill
                from backend_app.chatbot.services.skills.onboarding_skill import OnboardingSkill
                
                skill = OnboardingSkill()
                
                # Try to handle the message
                response = skill.handle(
                    "test_session_123",
                    test_case["message"],
                    test_case.get("context", {})
                )
                
                # Check if error was handled properly
                if test_case["expected_error"] in response.get("text", "").lower():
                    results.append({
                        "test": test_case["name"],
                        "status": "PASSED",
                        "details": f"Error handled properly: {test_case['expected_error']}"
                    })
                else:
                    results.append({
                        "test": test_case["name"],
                        "status": "FAILED",
                        "details": f"Expected error {test_case['expected_error']}, but got: {response.get('text', 'No response')}"
                    })
                
            except Exception as e:
                results.append({
                    "test": test_case["name"],
                    "status": "ERROR",
                    "details": str(e)
                })
        
        return results
    
    def test_integration_scenarios(self):
        """Test complete conversation scenarios"""
        logger.info("Testing integration scenarios...")
        
        scenarios = [
            {
                "name": "Complete candidate onboarding",
                "messages": [
                    {"message": "hello", "expected_intent": "welcome"},
                    {"message": "I'm a candidate", "expected_intent": "role_selected"},
                    {"message": "John Doe", "expected_intent": "name_collected"},
                    {"message": "john.doe@example.com", "expected_intent": "email_collected"},
                    {"message": "I want to upload my resume", "expected_intent": "resume_upload_request"}
                ]
            },
            {
                "name": "Complete recruiter workflow",
                "messages": [
                    {"message": "hi", "expected_intent": "welcome"},
                    {"message": "I'm a recruiter", "expected_intent": "role_selected"},
                    {"message": "I want to post a job", "expected_intent": "job_creation_start"},
                    {"message": "Software Engineer", "expected_intent": "job_title_collected"},
                    {"message": "find candidates", "expected_intent": "candidate_search_start"}
                ]
            },
            {
                "name": "Mixed conversation flow",
                "messages": [
                    {"message": "help", "expected_intent": "help_request"},
                    {"message": "I'm a candidate", "expected_intent": "role_selected"},
                    {"message": "what's my application status", "expected_intent": "application_status_check"}
                ]
            }
        ]
        
        results = []
        for scenario in scenarios:
            try:
                # Simulate conversation
                conversation_results = []
                session_context = {"is_first_message": True}
                
                for i, msg_data in enumerate(scenario["messages"]):
                    try:
                        # Import and use onboarding skill for simplicity
                        from backend_app.chatbot.services.skills.onboarding_skill import OnboardingSkill
                        
                        skill = OnboardingSkill()
                        
                        # Update context based on previous messages
                        if i > 0:
                            session_context["session_state"] = "ONBOARDING"
                        
                        # Handle message
                        response = skill.handle(
                            f"test_session_{scenario['name']}",
                            msg_data["message"],
                            session_context
                        )
                        
                        # Check response
                        if response.get("intent") == msg_data["expected_intent"]:
                            conversation_results.append({
                                "message": msg_data["message"],
                                "status": "PASSED",
                                "intent": response.get("intent")
                            })
                        else:
                            conversation_results.append({
                                "message": msg_data["message"],
                                "status": "FAILED",
                                "expected": msg_data["expected_intent"],
                                "actual": response.get("intent")
                            })
                        
                        # Update context for next message
                        if response.get("metadata"):
                            session_context.update(response.get("metadata", {}))
                        
                    except Exception as e:
                        conversation_results.append({
                            "message": msg_data["message"],
                            "status": "ERROR",
                            "details": str(e)
                        })
                
                # Calculate scenario success rate
                passed = sum(1 for result in conversation_results if result["status"] == "PASSED")
                total = len(conversation_results)
                success_rate = (passed / total) * 100 if total > 0 else 0
                
                results.append({
                    "test": scenario["name"],
                    "status": "PASSED" if success_rate >= 80 else "FAILED",
                    "success_rate": f"{success_rate:.1f}%",
                    "details": f"{passed}/{total} messages processed correctly",
                    "conversation": conversation_results
                })
                
            except Exception as e:
                results.append({
                    "test": scenario["name"],
                    "status": "ERROR",
                    "details": str(e)
                })
        
        return results
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        logger.info("Starting comprehensive chat bot test suite...")
        
        self.start_time = time.time()
        
        # Setup test environment
        if not self.setup_test_environment():
            logger.error("Failed to setup test environment. Aborting tests.")
            return
        
        # Run individual skill tests
        logger.info("Running individual skill tests...")
        onboarding_results = self.test_onboarding_skill()
        resume_results = self.test_resume_intake_skill()
        job_creation_results = self.test_job_creation_skill()
        candidate_matching_results = self.test_candidate_matching_skill()
        application_status_results = self.test_application_status_skill()
        
        # Run service tests
        logger.info("Running service tests...")
        message_router_results = self.test_message_router()
        copilot_service_results = self.test_copilot_service()
        
        # Run error handling tests
        logger.info("Running error handling tests...")
        error_handling_results = self.test_error_handling()
        
        # Run integration tests
        logger.info("Running integration tests...")
        integration_results = self.test_integration_scenarios()
        
        # Compile all results
        all_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_environment": "development",
            "skills": {
                "onboarding_skill": onboarding_results,
                "resume_intake_skill": resume_results,
                "job_creation_skill": job_creation_results,
                "candidate_matching_skill": candidate_matching_results,
                "application_status_skill": application_status_results
            },
            "services": {
                "message_router": message_router_results,
                "copilot_service": copilot_service_results
            },
            "error_handling": error_handling_results,
            "integration_scenarios": integration_results
        }
        
        # Calculate statistics
        total_tests = sum(len(results) for results in all_results.values() if isinstance(results, list))
        passed_tests = sum(1 for result in all_results.values() if isinstance(result, list) 
                          for test in result if test.get("status") == "PASSED")
        failed_tests = sum(1 for result in all_results.values() if isinstance(result, list) 
                          for test in result if test.get("status") == "FAILED")
        error_tests = sum(1 for result in all_results.values() if isinstance(result, list) 
                         for test in result if test.get("status") == "ERROR")
        
        execution_time = time.time() - self.start_time
        
        # Generate report
        report = {
            "executive_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "error_tests": error_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "execution_time": f"{execution_time:.2f} seconds",
                "overall_status": "SUCCESS" if failed_tests + error_tests == 0 else "PARTIAL_SUCCESS"
            },
            "detailed_results": all_results,
            "recommendations": self.generate_recommendations(all_results)
        }
        
        # Save report
        with open('chatbot_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save log file
        with open('chatbot_test_detailed.log', 'w') as f:
            f.write(f"Chat Bot Test Suite Report\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Execution Time: {execution_time:.2f} seconds\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Passed: {passed_tests}\n")
            f.write(f"Failed: {failed_tests}\n")
            f.write(f"Errors: {error_tests}\n")
            f.write(f"Success Rate: {passed_tests / total_tests * 100:.1f}%\n")
            f.write("=" * 50 + "\n\n")
            
            # Add detailed results
            for category, tests in all_results.items():
                if isinstance(tests, list):
                    f.write(f"{category.upper()} RESULTS:\n")
                    f.write("-" * 30 + "\n")
                    for test in tests:
                        if isinstance(test, dict):
                            f.write(f"Test: {test.get('test', 'Unknown')}\n")
                            f.write(f"Status: {test.get('status', 'Unknown')}\n")
                            if test.get('details'):
                                f.write(f"Details: {test['details']}\n")
                            if test.get('response'):
                                f.write(f"Response: {test['response']}\n")
                            f.write("\n")
                        else:
                            f.write(f"Test: {test}\n")
                            f.write("Status: Unknown\n\n")
                else:
                    f.write(f"{category.upper()}: {tests}\n\n")
        
        logger.info(f"Test suite completed. Report saved to 'chatbot_test_report.json'")
        logger.info(f"Success Rate: {passed_tests / total_tests * 100:.1f}%")
        
        return report
    
    def generate_recommendations(self, results):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze skill performance
        skill_results = results.get("skills", {})
        for skill_name, skill_tests in skill_results.items():
            passed = sum(1 for test in skill_tests if test.get("status") == "PASSED")
            total = len(skill_tests)
            if total > 0:
                success_rate = passed / total * 100
                if success_rate < 80:
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "Skill Performance",
                        "issue": f"{skill_name} has low success rate ({success_rate:.1f}%)",
                        "recommendation": f"Review and improve {skill_name} implementation"
                    })
        
        # Analyze service performance
        service_results = results.get("services", {})
        for service_name, service_tests in service_results.items():
            passed = sum(1 for test in service_tests if test.get("status") == "PASSED")
            total = len(service_tests)
            if total > 0:
                success_rate = passed / total * 100
                if success_rate < 80:
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "Service Performance",
                        "issue": f"{service_name} has low success rate ({success_rate:.1f}%)",
                        "recommendation": f"Review and improve {service_name} implementation"
                    })
        
        # Check error handling
        error_results = results.get("error_handling", [])
        if error_results:
            passed_error_tests = sum(1 for test in error_results if test.get("status") == "PASSED")
            if passed_error_tests < len(error_results):
                recommendations.append({
                    "priority": "MEDIUM",
                    "category": "Error Handling",
                    "issue": "Error handling needs improvement",
                    "recommendation": "Enhance error handling and validation"
                })
        
        # Check integration scenarios
        integration_results = results.get("integration_scenarios", [])
        if integration_results:
            passed_integration = sum(1 for test in integration_results if test.get("status") == "PASSED")
            if passed_integration < len(integration_results):
                recommendations.append({
                    "priority": "MEDIUM",
                    "category": "Integration",
                    "issue": "Integration scenarios need improvement",
                    "recommendation": "Improve conversation flow and context management"
                })
        
        # General recommendations
        recommendations.extend([
            {
                "priority": "LOW",
                "category": "Testing",
                "issue": "Limited test coverage",
                "recommendation": "Add more comprehensive unit tests"
            },
            {
                "priority": "LOW",
                "category": "Performance",
                "issue": "Performance optimization needed",
                "recommendation": "Optimize database queries and caching"
            }
        ])
        
        return recommendations

def main():
    """Main function to run the test suite"""
    print("Chat Bot/Co-Pilot Module Test Suite")
    print("=" * 50)
    
    test_suite = ChatBotTestSuite()
    report = test_suite.run_all_tests()
    
    if report:
        print("\nTest Results Summary:")
        print(f"Total Tests: {report['executive_summary']['total_tests']}")
        print(f"Passed: {report['executive_summary']['passed_tests']}")
        print(f"Failed: {report['executive_summary']['failed_tests']}")
        print(f"Errors: {report['executive_summary']['error_tests']}")
        print(f"Success Rate: {report['executive_summary']['success_rate']:.1f}%")
        print(f"Overall Status: {report['executive_summary']['overall_status']}")
        print(f"Execution Time: {report['executive_summary']['execution_time']}")
        
        print("\nRecommendations:")
        for rec in report['recommendations'][:5]:  # Show top 5 recommendations
            print(f"- {rec['priority']}: {rec['issue']}")
        
        print("\nDetailed report saved to: chatbot_test_report.json")
        print("Detailed log saved to: chatbot_test_detailed.log")
    else:
        print("Test suite failed to execute")

if __name__ == "__main__":
    main()