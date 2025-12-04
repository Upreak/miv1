# Backend/backend_app/brain_module/providers/groq_provider.py

from typing import Dict, Any
from .base_provider import BaseProvider
from ..utils.logger import get_logger

logger = get_logger("groq_provider")

class GroqProvider(BaseProvider):
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError("GroqProvider requires API key from .env")
        if not model:
            raise ValueError("GroqProvider requires model from .env")

        super().__init__(name="groq", api_key=api_key, model=model)

        try:
            from groq import Groq
            self._client = Groq(api_key=self.api_key)
        except Exception as e:
            logger.exception("Failed to initialize Groq SDK: %s", e)
            raise

    def generate(self, payload: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
        try:
            if "messages" in payload:
                messages = payload["messages"]
            else:
                messages = [{"role": "user", "content": payload.get("prompt", "")}]

            resp = self._client.chat.completions.create(
                model=self.model,
                messages=messages
            )

            text = resp.choices[0].message["content"]
            usage = getattr(resp, "usage", {}) or {}

            return {"success": True, "text": text, "usage": usage}

        except Exception as e:
            logger.exception("Groq generate failed: %s", e)
            return {"success": False, "text": "", "usage": {}, "error": str(e)}
