"""
BrainService: simple entry point used by central orchestrator.
Responsibilities:
 - Accept "qitem" with keys: qid, text, intake_type, source, meta
 - Build prompt via PromptBuilder
 - Call ProviderOrchestrator with formatted payload
 - Return standardized output
"""

from typing import Dict, Any
from .providers.provider_orchestrator import ProviderOrchestrator
from .prompt_builder.prompt_builder import PromptBuilder
from .prompt_builder.provider_formatters import ProviderStyle
from .utils.logger import get_logger

logger = get_logger("brain_service")

# instantiate single instances (lightweight)
_provider_orch = ProviderOrchestrator()
_prompt_builder = PromptBuilder()

class BrainService:
    """
    Minimal service class. Orchestrator should instantiate or import BrainService and call .process.
    """

    def process(self, qitem: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
        """
        qitem expected keys:
            qid: str
            text: str (extracted)
            intake_type: 'resume'|'jd'|'chat'
            source: optional
            meta: optional dict

        Returns:
            standardized dict with success/provider/model/response/usage/error
        """
        qid = qitem.get("qid")
        text = qitem.get("text", "")
        intake_type = qitem.get("intake_type", "resume")
        meta = qitem.get("meta", {})

        logger.info("BrainService.process qid=%s intake=%s", qid, intake_type)

        # Step 1: build prompt and provider payload
        provider_style = ProviderStyle.CHAT  # default; could be chosen based on intake_type
        # If you need prompt style mapping, update here (resume->CHAT, jd->PROMPT etc.)
        if intake_type in ("resume", "jd"):
            provider_style = ProviderStyle.CHAT

        built = _prompt_builder.build(text, intake_type=intake_type, provider_style=provider_style, meta=meta)
        payload = built.get("provider_payload")

        # Step 2: call provider orchestrator
        result = _provider_orch.generate(payload, timeout=timeout)

        # Normalize and return with some extra metadata
        return {
            "qid": qid,
            "success": bool(result.get("success")),
            "provider": result.get("provider"),
            "model": result.get("model"),
            "response": result.get("response"),
            "usage": result.get("usage"),
            "error": result.get("error")
        }

# convenience singleton
BrainSvc = BrainService()