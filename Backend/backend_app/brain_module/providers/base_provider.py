"""
BaseProvider: abstract minimal base class for provider adapters.
Each provider adapter must implement `generate(prompt_payload, timeout_secs)` which returns (text, usage_info).
"""

from typing import Dict, Any

class BaseProvider:
    def __init__(self, name: str, api_key: str, model: str | None = None):
        self.name = name
        self.api_key = api_key
        self.model = model

    def generate(self, payload: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
        """
        payload: dict returned by provider_formatter (e.g., {"messages": [...] } or {"prompt": "..."}).
        Return: {"success": bool, "text": str, "usage": {...}}
        """
        raise NotImplementedError()