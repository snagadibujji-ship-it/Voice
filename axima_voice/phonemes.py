from __future__ import annotations

from typing import Any, Dict, List


def text_to_phonemes(text: str, prosody: Dict[str, Any] | None = None) -> List[str]:
    """Convert text into a very small phoneme-like token stream."""
    _ = prosody
    return [ch.lower() for ch in text if ch.strip()]
