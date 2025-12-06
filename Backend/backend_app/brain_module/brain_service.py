"""
BrainService: Entry point used by API endpoint.
Responsibilities:
 - Accept mode + text + metadata
 - Route to mode-specific builder
 - Call ProviderOrchestrator
 - Parse response into structured data
 - Build FULL Brain Output Contract
"""

from typing import Dict, Any
from .providers.provider_orchestrator import ProviderOrchestrator
from .prompt_builder.prompt_builder import PromptBuilder
from .prompt_builder.provider_formatters import ProviderStyle
from .utils.logger import get_logger
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = get_logger("brain_service")

# instantiate single instances (lightweight)
_provider_orch = ProviderOrchestrator()
_prompt_builder = PromptBuilder()

class BrainService:
    """
    Brain service for processing different modes:
    - resume_parse: Parse resume text into structured data
    - jd_parse: Parse job description into structured data  
    - match: Match candidate profile against job requirements
    - chat: General conversational processing
    """

    async def process(self, qitem: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
        """
        Process brain request with frozen interface
        
        qitem expected keys:
            qid: str
            text: str (input text)
            intake_type: 'resume_parse'|'jd_parse'|'match'|'chat'
            meta: optional dict (contains mode-specific data)

        Returns:
            standardized dict with provider response and metadata
        """
        qid = qitem.get("qid", f"brain_{int(asyncio.get_event_loop().time() * 1000)}")
        text = qitem.get("text", "")
        intake_type = qitem.get("intake_type", "resume_parse")
        meta = qitem.get("meta", {})

        logger.info("BrainService.process qid=%s intake=%s", qid, intake_type)

        # Step 1: Validate intake_type and build appropriate prompt
        provider_payload = await self._build_prompt_for_mode(text, intake_type, meta)
        
        # Step 2: Call provider orchestrator (make async)
        result = await asyncio.wait_for(
            self._call_provider_orchestrator(provider_payload),
            timeout=timeout
        )

        # Step 3: Normalize and return with metadata
        return {
            "qid": qid,
            "success": bool(result.get("success", False)),
            "provider": result.get("provider", "unknown"),
            "model": result.get("model", "unknown"),
            "response": result.get("response", ""),
            "usage": result.get("usage", {}),
            "error": result.get("error")
        }

    async def _build_prompt_for_mode(self, text: str, intake_type: str, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Build provider payload based on mode"""
        
        if intake_type == "match":
            # For match mode, use special metadata handling
            candidate_data = meta.get("candidate_data", "")
            jd_data = meta.get("jd_data", "")
            if not candidate_data or not jd_data:
                raise ValueError("Match mode requires 'candidate_data' and 'jd_data' in metadata")
            
            # Build prompt for matching
            built = _prompt_builder.build(
                text=f"Candidate: {candidate_data}\n\nJob: {jd_data}",
                intake_type="match",
                provider_style=ProviderStyle.CHAT,
                meta=meta
            )
        else:
            # For other modes, use standard processing
            built = _prompt_builder.build(
                text=text,
                intake_type=intake_type,
                provider_style=ProviderStyle.CHAT,
                meta=meta
            )
        
        return built.get("provider_payload", {})

    async def _call_provider_orchestrator(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call provider orchestrator (wrapped in async)"""
        # For now, run the synchronous call in a thread pool
        # This allows us to maintain compatibility while making the interface async
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _provider_orch.generate, payload)

# convenience singleton
BrainSvc = BrainService()