from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class VoiceSource:
    """Generate a simple excitation signal for synthesis."""

    sample_rate: int = 22050

    def generate(self, phonemes: List[str]) -> List[float]:
        return [0.0 for _ in phonemes]
