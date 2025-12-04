"""
Convert a rendered prompt string into provider-specific payload.
Provides a simple abstraction:
 - Chat-style providers expect messages: [{"role":"system"}, {"role":"user"}]
 - Completion-style providers accept a single prompt string
"""

from enum import Enum
from typing import Dict, Any, List

class ProviderStyle(Enum):
    CHAT = "chat"
    PROMPT = "prompt"

def format_for_provider(rendered_prompt: str, style: ProviderStyle = ProviderStyle.CHAT) -> Dict[str, Any]:
    """
    Returns a small dict that provider_orchestrator will merge into provider SDK call.
    """
    if style == ProviderStyle.CHAT:
        system_msg = {"role": "system", "content": "You are an expert resume/jd parser. Return JSON with clearly labeled fields."}
        user_msg = {"role": "user", "content": rendered_prompt}
        return {"messages": [system_msg, user_msg]}
    else:
        return {"prompt": rendered_prompt}