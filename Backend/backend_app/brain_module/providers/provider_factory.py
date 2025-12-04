# Backend/backend_app/brain_module/providers/provider_factory.py

import os
from .gemini_provider import GeminiProvider
from .groq_provider import GroqProvider
from .openrouter_provider import OpenRouterProvider

_PROVIDER_MAP = {
    "gemini": GeminiProvider,
    "groq": GroqProvider,
    "openrouter": OpenRouterProvider,
}

def create_provider_from_env(slot_index: int):
    t = os.getenv(f"PROVIDER{slot_index}_TYPE", "").strip().lower()
    key = os.getenv(f"PROVIDER{slot_index}_KEY", "").strip()
    model = os.getenv(f"PROVIDER{slot_index}_MODEL", "").strip()
    base_url = os.getenv(f"PROVIDER{slot_index}_BASEURL", "").strip()

    if not t or not key:
        return None

    cls = _PROVIDER_MAP.get(t)
    if not cls:
        raise ValueError(f"Unsupported provider type '{t}' for slot {slot_index}")

    # OpenRouter needs base_url
    if t == "openrouter":
        return cls(api_key=key, model=model, base_url=base_url)

    # Other providers only need api_key + model
    return cls(api_key=key, model=model)
