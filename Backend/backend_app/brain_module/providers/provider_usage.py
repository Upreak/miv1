"""
ProviderUsage: simple persistence for daily counters and cooldowns.
This implementation saves state to a JSON file under brain_module/providers/provider_usage_state.json
It supports:
 - incrementing request counts
 - checking can_use() which respects cooldown and daily limits
 - automatic daily reset when day changes
"""

import json
from pathlib import Path
from typing import Dict, Any
from ..utils.time_utils import today_date_str, now_ts
from ..utils.logger import get_logger

logger = get_logger("provider_usage")

STATE_FILE = Path(__file__).resolve().parent / "provider_usage_state.json"

class ProviderUsageManager:
    def __init__(self):
        self._load()

    def _load(self):
        if STATE_FILE.exists():
            try:
                raw = json.loads(STATE_FILE.read_text())
            except Exception:
                raw = {}
        else:
            raw = {}
        # Ensure structure: { provider_key: { date: "YYYY-MM-DD", count: int, cooldown_until: ts } }
        self.state: Dict[str, Dict[str, Any]] = raw

    def _save(self):
        try:
            STATE_FILE.write_text(json.dumps(self.state))
        except Exception:
            logger.exception("Failed to persist provider usage state")

    def ensure_provider(self, provider_id: str):
        if provider_id not in self.state:
            self.state[provider_id] = {"date": today_date_str(), "count": 0, "cooldown_until": 0}

        # auto reset if date differs
        if self.state[provider_id].get("date") != today_date_str():
            self.state[provider_id]["date"] = today_date_str()
            self.state[provider_id]["count"] = 0
            # do not reset cooldown here (cooldown is time-based)

    def can_use(self, provider_id: str, daily_limit: int) -> bool:
        self.ensure_provider(provider_id)
        rec = self.state[provider_id]
        now = now_ts()
        if rec.get("cooldown_until", 0) > now:
            return False
        return rec.get("count", 0) < daily_limit

    def record_success(self, provider_id: str):
        self.ensure_provider(provider_id)
        self.state[provider_id]["count"] = self.state[provider_id].get("count", 0) + 1
        self._save()

    def set_cooldown(self, provider_id: str, seconds: int):
        self.ensure_provider(provider_id)
        self.state[provider_id]["cooldown_until"] = now_ts() + seconds
        self._save()

    def get_state(self, provider_id: str):
        self.ensure_provider(provider_id)
        return self.state[provider_id]