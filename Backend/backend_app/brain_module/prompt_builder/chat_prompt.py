"""
Minimal chat prompt helper for interactive chat flows (multi-turn handled externally).
"""

def render_chat_prompt(text: str, meta: dict | None = None) -> str:
    meta = meta or {}
    preamble = meta.get("system", "You are a helpful assistant.")
    return f"{preamble}\n\nUser:\n{text}"