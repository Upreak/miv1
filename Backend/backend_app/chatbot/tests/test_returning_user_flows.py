import asyncio
import logging
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend_app.chatbot.engine.flow_manager import FlowManager
from backend_app.chatbot.engine.chatbot_engine import ChatbotEngine
from backend_app.chatbot.engine.models import Message

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("TestReturningUser")

async def test_returning_candidate_flow():
    """Test: Returning Candidate sees their menu"""
    logger.info("\n=== TEST: Returning Candidate Flow ===")
    
    # Setup
    mock_session_service = AsyncMock()
    mock_session = MagicMock()
    mock_session.sid = "returning_candidate_123"
    
    # Simulate returning candidate (has full_name but NOT recruiter_name)
    mock_session.context = {
        "flow_state": {
            "current_flow": "UserInitiatedFlow",
            "current_page": "AuthCheckPage",  # Engine will start here
            "session_params": {
                "full_name": "Jane Doe",
                "email": "jane@example.com"
            }
        }
    }
    
    mock_session_service.get_or_create_session.return_value = mock_session
    async def side_effect_add_context(sid, key, value):
        mock_session.context[key] = value
        return mock_session
    mock_session_service.add_context_item.side_effect = side_effect_add_context
    
    # Initialize Engine
    flow_path = os.path.join(os.path.dirname(__file__), "../engine/candidate_flow.json")
    flow_manager = FlowManager(flow_path)
    engine = ChatbotEngine(flow_manager, mock_session_service)
    
    # Test: User opens chatbot (should go to Returning Candidate Menu)
    logger.info("\n[User Opens Chatbot]")
    responses = await engine.process_message("returning_candidate_123")
    log_responses(responses)
    
    # Debug
    logger.info(f"DEBUG: Got {len(responses)} responses")
    for i, r in enumerate(responses):
        logger.info(f"  Response {i}: text='{r.text if r.text else 'None'}', buttons={r.buttons if r.buttons else 'None'}")
    
    # Should see: "Welcome back! What would you like to do today?" with 4 options
    assert any("Welcome back" in r.text for r in responses if r.text), f"Should show returning user welcome. Got: {[r.text for r in responses if r.text]}"
    assert any(r.buttons and len(r.buttons) == 4 for r in responses), "Should show 4 menu options"
    
    # Test: Click "View Applications"
    logger.info("\n[User Clicks]: View Applications")
    responses = await engine.process_message("returning_candidate_123", input_payload="view_applications")
    log_responses(responses)
    
    # Should see their applications
    assert any("applications" in r.text.lower() for r in responses if r.text), "Should show applications"
    
    logger.info("✅ Returning Candidate Flow PASSED")

async def test_recruiter_registration_flow():
    """Test: New Recruiter registration"""
    logger.info("\n=== TEST: Recruiter Registration Flow ===")
    
    # Setup
    mock_session_service = AsyncMock()
    mock_session = MagicMock()
    mock_session.sid = "new_recruiter_456"
    mock_session.context = {}
    
    mock_session_service.get_or_create_session.return_value = mock_session
    async def side_effect_add_context(sid, key, value):
        mock_session.context[key] = value
        return mock_session
    mock_session_service.add_context_item.side_effect = side_effect_add_context
    
    # Initialize Engine
    flow_path = os.path.join(os.path.dirname(__file__), "../engine/candidate_flow.json")
    flow_manager = FlowManager(flow_path)
    engine = ChatbotEngine(flow_manager, mock_session_service)
    
    # Step 1: User is new, clicks Recruiter
    logger.info("\n[User Clicks]: Recruiter")
    responses = await engine.process_message("new_recruiter_456", input_payload="choose_recruiter")
    log_responses(responses)
    
    # Should ask for name
    assert any("name" in r.text.lower() for r in responses if r.text), "Should ask for name"
    
    # Step 2: Provide name
    logger.info("\n[User Types]: John Smith")
    responses = await engine.process_message("new_recruiter_456", input_text="John Smith")
    log_responses(responses)
    
    # Should ask for company
    assert any("company" in r.text.lower() for r in responses if r.text), "Should ask for company"
    
    # Step 3: Provide company
    logger.info("\n[User Types]: TechStartup Inc")
    responses = await engine.process_message("new_recruiter_456", input_text="TechStartup Inc")
    log_responses(responses)
    
    # Should ask for email
    assert any("email" in r.text.lower() for r in responses if r.text), "Should ask for email"
    
    # Step 4: Provide email
    logger.info("\n[User Types]: john@techstartup.com")
    responses = await engine.process_message("new_recruiter_456", input_text="john@techstartup.com")
    log_responses(responses)
    
    # Should ask for mobile
    assert any("mobile" in r.text.lower() or "number" in r.text.lower() for r in responses if r.text), "Should ask for mobile"
    
    # Step 5: Provide mobile
    logger.info("\n[User Types]: 9876543210")
    responses = await engine.process_message("new_recruiter_456", input_text="9876543210")
    log_responses(responses)
    
    # Should show registration complete with Post Job / Dashboard options
    assert any("profile is all set" in r.text.lower() for r in responses if r.text), "Should confirm registration"
    assert any(r.buttons and len(r.buttons) >= 2 for r in responses), "Should show action buttons"
    
    logger.info("✅ Recruiter Registration Flow PASSED")

async def test_returning_recruiter_post_job():
    """Test: Returning Recruiter posts a job"""
    logger.info("\n=== TEST: Returning Recruiter Post Job ===")
    
    # Setup
    mock_session_service = AsyncMock()
    mock_session = MagicMock()
    mock_session.sid = "returning_recruiter_789"
    
    # Simulate returning recruiter
    mock_session.context = {
        "flow_state": {
            "current_flow": "UserInitiatedFlow",
            "current_page": "AuthCheckPage",
            "session_params": {
                "recruiter_name": "Alice Johnson",
                "company_name": "BigCorp",
                "full_name": "Alice Johnson"  # Triggers returning user logic
            }
        }
    }
    
    mock_session_service.get_or_create_session.return_value = mock_session
    async def side_effect_add_context(sid, key, value):
        mock_session.context[key] = value
        return mock_session
    mock_session_service.add_context_item.side_effect = side_effect_add_context
    
    # Initialize Engine
    flow_path = os.path.join(os.path.dirname(__file__), "../engine/candidate_flow.json")
    flow_manager = FlowManager(flow_path)
    engine = ChatbotEngine(flow_manager, mock_session_service)
    
    # Test: User opens chatbot (should go to Returning Recruiter Menu)
    logger.info("\n[User Opens Chatbot]")
    responses = await engine.process_message("returning_recruiter_789")
    log_responses(responses)
    
    # Should see recruiter menu
    assert any(r.buttons and len(r.buttons) == 3 for r in responses), "Should show 3 recruiter menu options"
    
    # Click "Post a Job"
    logger.info("\n[User Clicks]: Post a Job")
    responses = await engine.process_message("returning_recruiter_789", input_payload="post_job")
    log_responses(responses)
    
    # Should ask for job title
    assert any("job title" in r.text.lower() for r in responses if r.text), "Should ask for job title"
    
    # Provide job title
    logger.info("\n[User Types]: Senior Backend Developer")
    responses = await engine.process_message("returning_recruiter_789", input_text="Senior Backend Developer")
    log_responses(responses)
    
    # Should ask for location
    assert any("location" in r.text.lower() for r in responses if r.text), "Should ask for location"
    
    # Provide location
    logger.info("\n[User Types]: Remote")
    responses = await engine.process_message("returning_recruiter_789", input_text="Remote")
    log_responses(responses)
    
    # Should ask for description
    assert any("description" in r.text.lower() for r in responses if r.text), "Should ask for description"
    
    # Provide description
    logger.info("\n[User Types]: We need an expert in Python and FastAPI")
    responses = await engine.process_message("returning_recruiter_789", input_text="We need an expert in Python and FastAPI")
    log_responses(responses)
    
    # Should confirm job posted
    assert any("created successfully" in r.text.lower() or "posted" in r.text.lower() for r in responses if r.text), "Should confirm job posting"
    
    logger.info("✅ Returning Recruiter Post Job PASSED")

def log_responses(messages):
    for m in messages:
        if m.text:
            print(f"[Bot]: {m.text}")
        if m.buttons:
            print(f"   [Buttons]: {[b.text for b in m.buttons]}")

async def run_all_tests():
    try:
        await test_returning_candidate_flow()
        await test_recruiter_registration_flow()
        await test_returning_recruiter_post_job()
        logger.info("\n🎉 ALL TESTS PASSED!")
    except AssertionError as e:
        logger.error(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(run_all_tests())
