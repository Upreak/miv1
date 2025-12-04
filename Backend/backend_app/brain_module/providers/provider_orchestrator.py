"""
ProviderOrchestrator:
 - Reads BRAIN_PROVIDER_COUNT and builds list of active providers from env
 - On generate(text/payload) it tries providers in order:
   - checks usage manager (can_use)
   - calls provider.generate(...)
   - on success returns standardized result
   - on failure sets cooldown for provider and continues to next
 - Supports automatic daily reset via ProviderUsageManager
 - Persists usage state to JSON file
"""

import os
from typing import Dict, Any, List, Optional
from .provider_factory import create_provider_from_env
from .provider_usage import ProviderUsageManager
from ..utils.logger import get_logger

logger = get_logger("provider_orchestrator")

DEFAULT_COUNT = int(os.getenv("BRAIN_PROVIDER_COUNT", "5"))
DEFAULT_DAILY_LIMIT = int(os.getenv("BRAIN_PROVIDER_DAILY_LIMIT", "1000"))
COOLDOWN_SECONDS_ON_ERROR = int(os.getenv("BRAIN_PROVIDER_COOLDOWN_SECONDS", str(24 * 3600)))  # 24h

class ProviderOrchestrator:
    def __init__(self, provider_count: int = DEFAULT_COUNT, daily_limit: int = DEFAULT_DAILY_LIMIT):
        self.provider_count = provider_count
        self.daily_limit = daily_limit
        self.usage = ProviderUsageManager()
        self.providers = self._load_providers()

    def _load_providers(self) -> List[Dict[str, Any]]:
        providers = []
        for i in range(1, self.provider_count + 1):
            try:
                inst = create_provider_from_env(i)
                if inst:
                    providers.append({"slot": i, "inst": inst, "type": inst.name, "model": inst.model})
                else:
                    logger.info(f"No provider configured at slot {i}")
            except Exception as e:
                logger.exception("Failed to create provider at slot %s: %s", i, e)
        return providers

    def generate(self, payload: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
        """
        payload: provider-format payload (messages OR prompt)
        returns standardized response dict:
          {"success": bool, "provider": provider_id, "model": model_name, "text": ..., "usage": {...}, "error": ...}
        """
        last_error = None
        for p in self.providers:
            slot = p["slot"]
            inst = p["inst"]
            provider_id = f"provider{slot}_{inst.name}"

            # check usage/cooldown
            if not self.usage.can_use(provider_id, self.daily_limit):
                logger.info("Skipping %s (limit or cooldown)", provider_id)
                continue

            try:
                logger.info("Attempting provider %s (slot %s, model %s)", inst.name, slot, inst.model)
                res = inst.generate(payload, timeout=timeout)
                if res.get("success"):
                    # record usage and return normalized result
                    self.usage.record_success(provider_id)
                    return {
                        "success": True,
                        "provider": provider_id,
                        "model": inst.model,
                        "response": res.get("text", ""),
                        "usage": res.get("usage", {})
                    }
                else:
                    # provider returned failure; set cooldown and continue
                    err = res.get("error", "unknown")
                    logger.warning("Provider %s failed: %s", provider_id, err)
                    last_error = err
                    self.usage.set_cooldown(provider_id, COOLDOWN_SECONDS_ON_ERROR)
                    continue
            except Exception as e:
                logger.exception("Provider %s raised exception: %s", provider_id, e)
                last_error = str(e)
                self.usage.set_cooldown(provider_id, COOLDOWN_SECONDS_ON_ERROR)
                continue

        # if all providers exhausted
        return {"success": False, "provider": None, "model": None, "response": "", "usage": {}, "error": last_error or "All providers failed"}