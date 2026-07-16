from __future__ import annotations

from typing import Any, Dict


def parse_meaning(text: str) -> Dict[str, Any]:
    """Extract a minimal meaning representation from text.

    This is intentionally simple for the first bootstrap phase.
    """
    return {
        "intent": "statement",
        "confidence": 1.0,
        "content": text,
        "mood": "neutral",
    }
