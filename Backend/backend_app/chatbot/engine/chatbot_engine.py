from typing import List, Dict, Any, Optional, Tuple
import logging
from .flow_manager import FlowManager
from .models import Page, Message
from .webhook_dispatcher import WebhookDispatcher
from ..services.session_service import SessionService
from ..services.analytics_service import AnalyticsService
from ..models.session_model import Session

logger = logging.getLogger(__name__)

class ChatbotEngine:
    def __init__(self, flow_manager: FlowManager, session_service: SessionService, analytics_service: AnalyticsService = None):
        self.flow_manager = flow_manager
        self.session_service = session_service
        self.webhook_dispatcher = WebhookDispatcher(session_service)
        self.analytics_service = analytics_service or AnalyticsService()

    async def process_message(self, user_id: str, input_text: str = None, 
                            input_payload: str = None, input_event: str = None,
                            platform: str = "telegram", metadata: Dict[str, Any] = None) -> List[Message]:
        
        # 1. Get or Create Session
        session = await self.session_service.get_or_create_session(
            user_id=user_id,
            platform=platform,
            platform_user_id=user_id
        )

        context = session.context or {}
        flow_state = context.get("flow_state", {})
        
        current_flow_name = flow_state.get("current_flow", "UserInitiatedFlow")
        current_page_id = flow_state.get("current_page", "StartPage")
        session_params = flow_state.get("session_params", {})
        
        # Helper to get page object
        current_page = self.flow_manager.get_page(current_page_id)
        if not current_page:
            current_page = self.flow_manager.get_start_page()
            current_page_id = current_page.pageId

        response_messages = []
        
        # Check if this is initial page load (no input from user, just landing on page)
        # If we're on a page with entry fulfillment and no user input, execute it
        is_initial_load = not (input_text or input_payload or input_event or metadata)
        
        if is_initial_load and current_page.entryFulfillment:
            # Execute entry fulfillment for the current page
            for msg in current_page.entryFulfillment.messages:
                rendered_text = self._render_text(msg.text, session_params)
                response_messages.append(Message(
                    text=rendered_text,
                    buttons=msg.buttons,
                    webhook=msg.webhook
                ))
            
            # Execute webhook if present
            if current_page.entryFulfillment.webhook:
                logger.info(f"Trigger webhook on initial load: {current_page.entryFulfillment.webhook.call}")
                
                event_triggered = await self.webhook_dispatcher.dispatch(
                    current_page.entryFulfillment.webhook.call,
                    session.sid,
                    session_params,
                    metadata
                )
                
                if event_triggered:
                    logger.info(f"Webhook triggered event: {event_triggered}")
                    # Process the event immediately by setting it for the next iteration
                    input_event = event_triggered
                    # Continue with the loop below
        
        # Loop variables
        # We start with the inputs provided by the user
        loop_intent = input_payload
        loop_event = input_event
        loop_text = input_text
        
        # Auto-detect file upload (Only on first pass)
        if metadata and ("document" in metadata or "photos" in metadata):
             if not loop_intent:
                 loop_intent = "std.file_uploaded"

        # Max hops to prevent infinite loops (e.g. A->B->A)
        max_hops = 5
        hops = 0

        while hops < max_hops:
            hops += 1
            transition_target = None
            form_valid = False

            # 3. Form Filling Logic (Only applies if we have user input text/payload and NOT an event)
            # If we are looping due to an event, we skip form filling on the new page usually
            # unless the definition says otherwise. For MVP, skip form if processing event.
            if not loop_event and current_page.form and (loop_text or loop_intent):
                prompt, updated_params = self._process_form(current_page, session_params, loop_text, loop_intent)
                session_params.update(updated_params)
                
                if prompt:
                    # Still missing params, stay on page and ask prompt
                    response_messages.append(Message(text=prompt))
                    break # Stop processing, wait for user
                else:
                    form_valid = True

            # 4. Evaluate Transition
            transition_target = self.flow_manager.evaluate_transition(
                current_page, 
                intent=loop_intent, 
                event=loop_event,
                session_params=session_params,
                form_valid=form_valid
            )

            if transition_target:
                next_page = self.flow_manager.get_page(transition_target)
                if next_page:
                    logger.info(f"Transitioning: {current_page.displayName} -> {next_page.displayName}")
                    current_page = next_page
                    current_page_id = next_page.pageId
                    
                    # Clear inputs for the new page (unless we want to carry over?)
                    # Usually inputs are consumed by the transition.
                    loop_intent = None
                    loop_text = None
                    loop_event = None
                    
                    # Add Entry Messages
                    if next_page.entryFulfillment:
                        for msg in next_page.entryFulfillment.messages:
                            # Render text with params
                            rendered_text = self._render_text(msg.text, session_params)
                            # Create new Message object to avoid mutating the blueprint
                            response_messages.append(Message(
                                text=rendered_text,
                                buttons=msg.buttons,
                                webhook=msg.webhook
                            ))

                        if next_page.entryFulfillment.webhook:
                             # Handle webhook

                             logger.info(f"Trigger webhook: {next_page.entryFulfillment.webhook.call}")
                             
                             event_triggered = await self.webhook_dispatcher.dispatch(
                                 next_page.entryFulfillment.webhook.call,
                                 session.sid,
                                 session_params,
                                 metadata
                             )
                             
                             if event_triggered:
                                 logger.info(f"Webhook triggered event: {event_triggered}")
                                 loop_event = event_triggered
                                 # Loop continues to handle this event immediately in the *new* page context
                                 # But wait, we just entered 'next_page'. 
                                 # Does 'next_page' transition based on this event?
                                 # Yes, that's the logic.
                                 continue 
                    
                    # If we transitioned but no event triggered, we stop here 
                    # and wait for user input on the new page.
                    break 

            else:
                # No transition matches. 
                # If we were processing an event or form complete, and no transition, we stay here.
                # If it was user input and no transition/form, it's a Fallback.
                # But typically 'true' condition handles matches.
                break

        # 6. Save State
        await self._update_state(session.sid, current_flow_name, current_page_id, session_params)
        
        # 7. Track Analytics
        # Track page view
        await self.analytics_service.track_page_view(
            user_id=user_id,
            page_id=current_page_id,
            flow_name=current_flow_name,
            session_id=session.sid
        )
        
        # Track button click if present
        if input_payload:
            await self.analytics_service.track_button_click(
                user_id=user_id,
                button_payload=input_payload,
                button_text=input_payload,  # In real app, map payload to button text
                page_id=current_page_id,
                session_id=session.sid
            )
        
        return response_messages



    def _render_text(self, text: str, params: Dict[str, Any]) -> str:
        """
        Replace {{session.params.key}} with value from params.
        """
        if not text:
            return ""
        
        result = text
        # Simple find and replace for known keys or via regex
        # Using regex for robustness
        import re
        pattern = r"\{\{session\.params\.([a-zA-Z0-9_]+)\}\}"
        
        def replace_match(match):
            key = match.group(1)
            val = params.get(key, "")
            return str(val)
        
        result = re.sub(pattern, replace_match, result)
        return result

    async def _update_state(self, session_id: str, flow: str, page: str, params: Dict):
        state = {
            "current_flow": flow,
            "current_page": page,
            "session_params": params
        }
        await self.session_service.add_context_item(session_id, "flow_state", state)

    def _process_form(self, page: Page, params: Dict, text: str, payload: str) -> Tuple[Optional[str], Dict]:
        """
        Process input against the current form.
        Returns (next_prompt, updated_params_dict).
        If next_prompt is None, form is complete.
        """
        if not page.form:
            return None, {}

        # 1. Identify which param we are filling
        # Simple logic: Find first missing param
        target_param = None
        for param in page.form.parameters:
            if param.required and param.name not in params:
                target_param = param
                break
        
        if not target_param:
            return None, {}

        # 2. If we have input, try to fill it
        # NOTE: This logic assumes the User just replied to the prompt for target_param
        # Ideally, we should track "awaiting_param" in state
        
        updated = {}
        if text or payload:
            val = payload if payload else text
            # Basic validation
            # Type conversion? 
            updated[target_param.name] = val
            
            # Check for next param
            next_param = None
            found_current = False
            for param in page.form.parameters:
                if param.name == target_param.name:
                    found_current = True
                    continue
                if found_current and param.required and param.name not in params:
                    next_param = param
                    break
            
            if next_param:
                return next_param.prompts[0], updated
            else:
                return None, updated # All done
        
        # 3. If no input (entering page first time) or input rejected (not impl), return prompt
        return target_param.prompts[0], {}
