from __future__ import annotations

from typing import Any, Dict


def plan_prosody(meaning: Dict[str, Any]) -> Dict[str, Any]:
    """Plan timing and voice shape from meaning."""
    mood = meaning.get("mood", "neutral")

    if mood == "excited":
        return {"speed": 1.15, "pitch": 1.08, "energy": 1.12, "pause_scale": 0.9}
    if mood == "calm":
        return {"speed": 0.92, "pitch": 0.96, "energy": 0.9, "pause_scale": 1.15}

    return {"speed": 1.0, "pitch": 1.0, "energy": 1.0, "pause_scale": 1.0}
