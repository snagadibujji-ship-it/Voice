from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .filter import VocalTractFilter
from .source import VoiceSource


@dataclass
class Synthesizer:
    source: VoiceSource
    filter: VocalTractFilter

    def synthesize(self, phonemes: List[str]) -> List[float]:
        excitation = self.source.generate(phonemes)
        return self.filter.apply(excitation)
