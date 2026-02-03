"""
Daily usage limits for AI image providers (ModelScope, Z-Image-Turbo).
Persists counts in a JSON file keyed by date so limits reset each day.
"""

import json
import os
from datetime import date
from typing import Optional

# Per-provider daily limits
DAILY_LIMITS = {
    "ModelScope (AI)": 50,
    "Z-Image-Turbo (AI)": 10,
}

_USAGE_FILE = "ai_image_usage.json"


def _usage_file_path() -> str:
    """Path to the usage JSON file (next to this module / app root)."""
    root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root, _USAGE_FILE)


def _today() -> str:
    return date.today().isoformat()


def _load_usage() -> dict:
    """Load usage data: { "YYYY-MM-DD": { "ModelScope (AI)": n, ... } }."""
    path = _usage_file_path()
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_usage(data: dict) -> None:
    path = _usage_file_path()
    try:
        dirpath = os.path.dirname(path)
        if dirpath and not os.path.isdir(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def get_usage(provider: str) -> int:
    """Return today's usage count for the given provider."""
    if provider not in DAILY_LIMITS:
        return 0
    data = _load_usage()
    day = _today()
    day_data = data.get(day) or {}
    return int(day_data.get(provider, 0))


def get_limit(provider: str) -> int:
    """Return daily limit for the provider, or 0 if not limited."""
    return DAILY_LIMITS.get(provider, 0)


def get_remaining(provider: str) -> Optional[int]:
    """Return remaining quota today, or None if provider has no limit."""
    limit = get_limit(provider)
    if limit <= 0:
        return None
    return max(0, limit - get_usage(provider))


def is_over_limit(provider: str) -> bool:
    """True if provider has a limit and today's usage is already at or over it."""
    limit = get_limit(provider)
    if limit <= 0:
        return False
    return get_usage(provider) >= limit


def increment_usage(provider: str) -> None:
    """Increment today's usage for the provider by 1."""
    if provider not in DAILY_LIMITS:
        return
    data = _load_usage()
    day = _today()
    if day not in data:
        data[day] = {}
    data[day][provider] = data[day].get(provider, 0) + 1
    _save_usage(data)


def reset_today(provider: Optional[str] = None) -> None:
    """Reset today's usage for the given provider, or for all limited providers if provider is None."""
    data = _load_usage()
    day = _today()
    if day not in data:
        return
    if provider:
        if provider in DAILY_LIMITS and provider in data[day]:
            del data[day][provider]
            if not data[day]:
                del data[day]
            _save_usage(data)
    else:
        for p in list(DAILY_LIMITS.keys()):
            data[day].pop(p, None)
        if not data[day]:
            del data[day]
        _save_usage(data)
