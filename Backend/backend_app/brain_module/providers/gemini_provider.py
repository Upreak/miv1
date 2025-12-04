# Backend/backend_app/brain_module/providers/gemini_provider.py

from typing import Dict, Any
from .base_provider import BaseProvider
from ..utils.logger import get_logger

logger = get_logger("gemini_provider")

class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError("GeminiProvider requires API key from .env")
        if not model:
            raise ValueError("GeminiProvider requires model from .env")

        super().__init__(name="gemini", api_key=api_key, model=model)

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._model_obj = genai.GenerativeModel(self.model)
        except Exception as e:
            logger.exception("Failed to initialize Gemini SDK: %s", e)
            raise

    def generate(self, payload: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
        try:
            if "messages" in payload:
                msgs = payload["messages"]
                user_texts = [m["content"] for m in msgs]
                prompt = "\n".join(user_texts)
            else:
                prompt = payload.get("prompt", "")

            resp = self._model_obj.generate_content(prompt)
            text = getattr(resp, "text", None) or str(resp)

            return {"success": True, "text": text, "usage": {}}

        except Exception as e:
            logger.exception("Gemini generate failed: %s", e)
            return {"success": False, "text": "", "usage": {}, "error": str(e)}
