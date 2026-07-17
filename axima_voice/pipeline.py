from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .meaning_parser import parse_meaning
from .performance_graph import build_performance_graph
from .phonemes import text_to_phonemes
from .prosody import plan_prosody
from .simple_synth import SimpleSynthesizer
from .text_normalizer import normalize_text


@dataclass
class AximaVoice:
    """High-level orchestration layer for Axima Voice."""

    synthesizer: SimpleSynthesizer = SimpleSynthesizer()

    def synthesize(self, text: str) -> Dict[str, Any]:
        normalized = normalize_text(text)
        meaning = parse_meaning(normalized)
        prosody = plan_prosody(meaning)
        phonemes = text_to_phonemes(normalized, prosody=prosody)
        performance_graph = build_performance_graph(normalized, meaning, prosody)
        audio = self.synthesizer.synthesize(phonemes, performance_graph=performance_graph)

        return {
            "text": text,
            "normalized_text": normalized,
            "meaning": meaning,
            "prosody": prosody,
            "phonemes": phonemes,
            "performance_graph": performance_graph.to_dict(),
            "audio": audio,
        }
