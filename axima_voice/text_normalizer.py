from __future__ import annotations

import re

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Normalize raw input before meaning and phoneme planning."""
    text = text.strip()
    text = _WHITESPACE_RE.sub(" ", text)
    return text
