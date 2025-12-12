import json
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from .models import FlowConfig, Page, Flow, Route

logger = logging.getLogger(__name__)

class FlowManager:
    def __init__(self, flow_file_path: str):
        self.config: FlowConfig = self._load_flow(flow_file_path)
        self.flow_map: Dict[str, Flow] = {f.name: f for f in self.config.flows}
        # Assuming single flow for now or default to first
        self.default_flow = self.config.flows[0]
        self.page_map: Dict[str, Page] = {p.pageId: p for p in self.default_flow.pages}

    def _load_flow(self, path: str) -> FlowConfig:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return FlowConfig(**data)
        except Exception as e:
            logger.error(f"Failed to load flow config from {path}: {e}")
            raise

    def get_start_page(self) -> Page:
        return self.page_map.get(self.default_flow.startPage)

    def get_page(self, page_id: str) -> Optional[Page]:
        return self.page_map.get(page_id)

    def evaluate_transition(self, current_page: Page, intent: str = None, event: str = None, 
                          session_params: Dict[str, Any] = None, form_valid: bool = False) -> Optional[str]:
        """
        Evaluate transition routes for the current page.
        Returns the targetPage ID if a condition matches, else None.
        """
        if not current_page.transitionRoutes:
            return None
            
        session = type('obj', (object,), {'params': session_params or {}})
        
        for route in current_page.transitionRoutes:
            # Event match
            if event and route.condition == f"event == '{event}'":
                return route.targetPage
            
            # Intent match
            if intent and route.condition == f"intent == '{intent}'":
                return route.targetPage
            
            # Form validity
            if form_valid and route.condition == "form.valid":
                return route.targetPage

            # Simple boolean evaluation (EXTREMELY BASIC for now - can use simpleeval later)
            if route.condition == "true":
                return route.targetPage
            
            # Check for Session Param logic (e.g. session.params.x == 'y')
            # For robustness, we should use a safe eval library, but strict string matching for now
            # as per the limited blueprint complexity.
            # TODO: Implement expression engine
            if "session.params" in route.condition and session_params:
                try:
                    # Very unsafe - allow simple equality checks for MVP
                    # In prod, use `simpleeval` or writing a mini-parser
                    # Hacky replacement for "session.params.highest_education" -> "value"
                    # Only supporting == for now
                    if "==" in route.condition:
                        left, right = route.condition.split("==")
                        left = left.strip()
                        right = right.strip().strip("'").strip('"')
                        
                        param_key = left.replace("session.params.", "")
                        param_value = session_params.get(param_key)
                        
                        if str(param_value) == right:
                            return route.targetPage
                        
                        # Handle multiple OR logic? (||)
                        # The blueprint has: session.params.x == '10th' || session.params.x == '12th'
                        # This requires split by ||
                        
                except Exception as e:
                    logger.warning(f"Condition eval failed: {route.condition} - {e}")

        return None

    def get_next_form_prompt(self, page: Page, collected_params: Dict[str, Any]) -> Optional[str]:
        """
        If the page has a form, return the prompt for the first missing required parameter.
        """
        if not page.form or not page.form.parameters:
            return None
            
        for param in page.form.parameters:
            if param.required and param.name not in collected_params:
                # Return the first prompt
                return param.prompts[0]
        return None
