import os
import requests
from datetime import datetime, timezone
from typing import Any, Dict

FORTNITE_STATS_URL = "https://fortniteapi.io/v1/stats"
API_TIMEOUT = 15


class FortniteApiError(Exception):
    pass


def _get_api_key() -> str:
    api_key = os.getenv("FORTNITE_API_KEY", "").strip()
    if not api_key:
        raise FortniteApiError(
            "No Fortnite API key found. Set FORTNITE_API_KEY in your .env for live progress."
        )
    return api_key


def _sample_progress(username: str, platform: str) -> Dict[str, Any]:
    return {
        "source": "sample",
        "display_name": username,
        "platform": platform,
        "level": 72,
        "battle_pass_tier": 85,
        "xp_to_next": 14230,
        "sprite_name": "Shadow Pulse",
        "sprite_progress": 56,
        "next_reward": "Epic Harvesting Tool",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "note": (
            "Fortnite API key not configured.\n"
            "Install a provider API key in .env to fetch real progress."
        ),
    }


def _normalize_response(
    username: str, platform: str, data: Dict[str, Any]
) -> Dict[str, Any]:
    result = data.get("result", data)
    display_name = result.get("displayName") or result.get("username") or username
    level = result.get("level") or result.get("accountLevel") or 0
    battle_pass = result.get("battlePass") or result.get("battlepass") or {}
    battle_pass_tier = (
        result.get("battlePassLevel") or result.get("battle_pass", {}).get("tier")
        if isinstance(result.get("battle_pass"), dict)
        else result.get("battlePassLevel") or 0
    )
    if not battle_pass_tier and isinstance(battle_pass, dict):
        battle_pass_tier = battle_pass.get("level") or battle_pass.get("tier") or 0
    sprite_progress = result.get("spriteProgress") or result.get("sprite_progress") or 0
    xp_to_next = (
        result.get("xpToNext")
        or result.get("xp_to_next")
        or result.get("xp_needed")
        or 0
    )

    return {
        "source": "fortniteapi",
        "display_name": display_name,
        "platform": platform,
        "level": (
            int(level)
            if isinstance(level, (int, float, str)) and str(level).isdigit()
            else 0
        ),
        "battle_pass_tier": (
            int(battle_pass_tier)
            if isinstance(battle_pass_tier, (int, float, str))
            and str(battle_pass_tier).isdigit()
            else 0
        ),
        "xp_to_next": (
            int(xp_to_next)
            if isinstance(xp_to_next, (int, float, str)) and str(xp_to_next).isdigit()
            else 0
        ),
        "sprite_name": result.get("spriteName")
        or result.get("sprite_name")
        or "Battle Pass Sprite",
        "sprite_progress": (
            int(sprite_progress)
            if isinstance(sprite_progress, (int, float, str))
            and str(sprite_progress).isdigit()
            else 0
        ),
        "next_reward": result.get("nextReward")
        or result.get("next_reward")
        or "Next Battle Pass item",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "note": "Live Fortnite data fetched from the provider.",
    }


def _fetch_live_progress(username: str, platform: str) -> Dict[str, Any]:
    api_key = _get_api_key()
    params = {"username": username, "platform": platform}
    headers = {"Authorization": api_key, "Content-Type": "application/json"}

    try:
        response = requests.get(
            FORTNITE_STATS_URL, headers=headers, params=params, timeout=API_TIMEOUT
        )
    except requests.RequestException as exc:
        raise FortniteApiError(f"Fortnite API request failed: {exc}")

    if response.status_code != 200:
        raise FortniteApiError(
            f"Fortnite API returned {response.status_code}: {response.text}"
        )

    payload = response.json()
    if not isinstance(payload, dict):
        raise FortniteApiError("Fortnite API response was not JSON object.")

    return _normalize_response(username, platform, payload)


def fetch_progress(username: str, platform: str) -> Dict[str, Any]:
    if not username:
        raise FortniteApiError("Epic username is required for progress lookup.")

    platform_value = platform.lower() if platform else "pc"
    if platform_value not in {"pc", "psn", "xbl"}:
        platform_value = "pc"

    try:
        return _fetch_live_progress(username, platform_value)
    except FortniteApiError as exc:
        sample = _sample_progress(username, platform_value)
        sample["note"] = (
            f"Could not fetch live progress: {exc}.\nShowing sample progress instead."
        )
        return sample
