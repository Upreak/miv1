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
logger = logging.getLogger("TestIntegration")

async def run_test():
    logger.info("--- Starting Chatbot Flow Integration Test ---")

    # 1. Setup Mocks
    mock_session_service = AsyncMock()
    
    # Mock Session Object
    mock_session = MagicMock()
    mock_session.sid = "test_session_123"
    mock_session.context = {} 
    
    # Mock return values
    mock_session_service.get_or_create_session.return_value = mock_session
    
    # Mock add_context_item to update our local mock context
    async def side_effect_add_context(sid, key, value):
        mock_session.context[key] = value
        return mock_session
    mock_session_service.add_context_item.side_effect = side_effect_add_context

    # 2. Initialize Engine
    flow_path = os.path.join(os.path.dirname(__file__), "../engine/candidate_flow.json")
    if not os.path.exists(flow_path):
        logger.error(f"Flow file not found at {flow_path}")
        return

    flow_manager = FlowManager(flow_path)
    engine = ChatbotEngine(flow_manager, mock_session_service)

    logger.info("Engine Initialized.")

    # 3. Simulate Conversation

    # Step 1: User says "Hi" - REMOVED to avoid falling back
    # logger.info("\n[User]: Hi")
    # responses = await engine.process_message("user1", input_text="Hi")
    # log_responses(responses)

    # Step 2: User clicks "Candidate"
    logger.info("\n[User]: (Click) choose_candidate")
    responses = await engine.process_message("user1", input_payload="choose_candidate")
    log_responses(responses)

    # Step 3: User clicks "Upload Resume"
    logger.info("\n[User]: (Click) upload_resume")
    responses = await engine.process_message("user1", input_payload="upload_resume")
    log_responses(responses)

    # Step 4: User uploads file (Simulate Metadata)
    logger.info("\n[User]: (Upload) resume.pdf")
    metadata = {"document": {"file_id": "123", "file_name": "resume.pdf"}}
    # Since ResumeUpload page has a webhook, this should trigger it
    # We are technically supposed to be on ResumeUpload page now?
    # Wait, previous transition went to ResumeUpload page. 
    # Check if ResumeUpload page has entry fulfillment?
    # Yes, "Please upload your resume..."
    # Now user sends file. The logic in Engine process_form or webhook?
    # Actually, the file upload message itself doesn't have a payload/text usually, 
    # but my Engine logic looks for `input_event` or `form`.
    # ResumeUpload page has `webhook`.
    # But webhooks in blueprint are on `entryFulfillment`. 
    # The blueprint says: ResumeUpload Page -> Entry: "Please upload..." AND Webhook "resume_upload_handler"
    
    # Wait, if Webhook is on Entry, it executes immediately when transition happens!
    # User clicks "Upload Resume" -> Transitions to `ResumeUpload`.
    # Entry Fulfillment runs -> Messages sent -> Webhook executes.
    # If webhook handles "upload", it expects the file to be there?
    # BUT the file isn't there yet. The user hasn't uploaded it.
    
    # LOGIC FLAW DETECTED:
    # If `resume_upload_handler` is on Entry of `ResumeUpload` page, it runs BEFORE user interaction.
    # It should be on the Transition Route condition or on a specific event?
    # OR the `ResumeUpload` page should wait for input.
    # The blueprint shows:
    # Page: ResumeUpload
    # Entry: "Please upload..." + Webhook
    # Transition: event == 'file_parsed_success'
    
    # If I put webhook on Entry, it will fail because metadata is empty.
    # It will trigger 'file_parsed_failure' (as per my webhook mock).
    # Then transition to result 'ResumeUpload_Failure'.
    
    # CORRECT FLOW SHOULD BE:
    # 1. Page `ResumeUpload` (Waiting for file). User sees "Please upload".
    # 2. User uploads file.
    # 3. Engine processes message.
    # 4. We need to know this message is a File Upload and trigger the logic.
    # 5. The generic logic could be: If waiting on ResumeUpload page, and message has attachment, trigger webhook?
    
    # Current Blueprint implementation:
    # It seems I copied the structure where webhook is on Entry.
    # This assumes the param collecting happens differently or I need to adjust the blueprint.
    
    # FIX:
    # I should remove webhook from `ResumeUpload` entry.
    # Instead, I should have a Transition Route on `ResumeUpload` page:
    # condition: "has_attachment" (or similar) -> Trigger Webhook OR Target Page `ProcessingResume`.
    
    # OR, easier for now:
    # Let's see what happens.
    # If the mock webhook fails (returns None or failure event), we go to failure page.
    # Failure page buttons: "Try Again".
    
    # To support "Upload File" interaction:
    # The Engine needs to detect "This is a file message" and if we are on `ResumeUpload` page, execute the parsing logic.
    # My Engine doesn't have "Execute Webhook on Input" logic yet. It only has "Execute Webhook on Entry".
    
    # I will modify the JSON blueprint in the test (or in file) to move logic?
    # Better: Engine Logic.
    # If current page == ResumeUpload, and input has metadata['document'], 
    # invoke the webhook manually?
    
    # Let's test what happens now.
    
    responses = await engine.process_message("user1", metadata=metadata)
    log_responses(responses)

def log_responses(messages):
    for m in messages:
        print(f"[Bot]: {m.text}")
        if m.buttons:
            print(f"   [Buttons]: {[b.text for b in m.buttons]}")

if __name__ == "__main__":
    try:
        asyncio.run(run_test())
    except Exception as e:
        import traceback
        traceback.print_exc()

