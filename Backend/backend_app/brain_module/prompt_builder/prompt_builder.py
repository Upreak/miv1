"""
PromptBuilder:
 - Chooses the correct renderer for intake_type ("resume","jd","chat")
 - Returns rendered prompt + provider payload (via provider_formatters)
 - Uses existing resume_prompt.py and jd_prompt.py if present (import optional)
"""

from typing import Dict, Any
from pathlib import Path
from ..utils.logger import get_logger
from .provider_formatters import format_for_provider, ProviderStyle

logger = get_logger("prompt_builder")

# Try to import existing renderers (your repo already has resume_prompt.py / jd_prompt.py)
try:
    from .resume_prompt import ResumePromptRenderer
except Exception:
    ResumePromptRenderer = None

try:
    from .jd_prompt import JDPromptRenderer
except Exception:
    JDPromptRenderer = None

try:
    from .chat_prompt import render_chat_prompt
except Exception:
    def render_chat_prompt(text: str, meta: dict | None = None) -> str:
        meta = meta or {}
        return f"You are an assistant.\n\nUser:\n{text}"

class PromptBuilder:
    def __init__(self):
        self.resume_renderer = ResumePromptRenderer() if ResumePromptRenderer else None
        self.jd_renderer = JDPromptRenderer() if JDPromptRenderer else None

    def build(self, text: str, intake_type: str = "resume", provider_style: ProviderStyle = ProviderStyle.CHAT, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        meta = meta or {}
        t = (intake_type or "resume").lower()

        if t in ("resume", "cv"):
            if self.resume_renderer:
                rendered = self.resume_renderer.render_prompt(text, meta.get("source"), meta.get("filename"))
            else:
                # fallback generic resume prompt
                rendered = f"Parse this resume and extract structured fields:\n\n{text}"
        elif t in ("jd", "job", "job_description"):
            if self.jd_renderer:
                rendered = self.jd_renderer.render_prompt(text, meta.get("source"), meta.get("filename"))
            else:
                rendered = f"Parse this job description and extract structured fields:\n\n{text}"
        else:
            rendered = render_chat_prompt(text, meta)

        provider_payload = format_for_provider(rendered, provider_style)
        return {
            "rendered_prompt": rendered,
            "provider_payload": provider_payload,
            "meta": meta
        }