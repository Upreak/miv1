# Backend/backend_app/brain_module/providers/openrouter_provider.py

from typing import Dict, Any
from .base_provider import BaseProvider
from ..utils.logger import get_logger

logger = get_logger("openrouter_provider")

class OpenRouterProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, base_url: str):
        if not api_key:
            raise ValueError("OpenRouterProvider requires API key from .env")
        if not model:
            raise ValueError("OpenRouterProvider requires model from .env")
        if not base_url:
            raise ValueError("OpenRouterProvider requires BASEURL from .env")

        super().__init__(name="openrouter", api_key=api_key, model=model)

        try:
            import openai
            # Use new client if available
            try:
                self._client = openai.OpenAI(api_key=self.api_key, base_url=base_url)
            except Exception:
                # fallback older style
                openai.api_key = api_key
                openai.base_url = base_url
                self._client = openai
        except Exception as e:
            logger.exception("Failed to initialize OpenRouter client: %s", e)
            raise

    def generate(self, payload: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
        try:
            if "messages" in payload:
                resp = self._client.chat.completions.create(
                    model=self.model,
                    messages=payload["messages"],
                    timeout=timeout
                )
            else:
                resp = self._client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": payload.get("prompt", "")}],
                    timeout=timeout
                )

            text = resp.choices[0].message.content
            usage = getattr(resp, "usage", {}) or {}

            return {"success": True, "text": text, "usage": usage}

        except Exception as e:
            logger.exception("OpenRouter generate failed: %s", e)
            return {"success": False, "text": "", "usage": {}, "error": str(e)}
