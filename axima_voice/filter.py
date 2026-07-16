from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class VocalTractFilter:
    """Shape excitation into speech-like output."""

    def apply(self, excitation: List[float]) -> List[float]:
        return excitation
