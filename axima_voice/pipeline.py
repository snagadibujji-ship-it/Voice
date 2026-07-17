from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from .meaning_parser import parse_meaning
from .performance_graph import build_performance_graph
from .phase2 import build_phase2_plan
from .phase3 import build_streaming_plan
from .phase4 import build_live_playback_plan
from .phase5 import build_composition_plan
from .phonemes import text_to_phonemes
from .prosody import plan_prosody
from .simple_synth import SimpleSynthesizer
from .text_normalizer import normalize_text


@dataclass
class AximaVoice:
    """High-level orchestration layer for Axima Voice."""

    synthesizer: SimpleSynthesizer = field(default_factory=SimpleSynthesizer)

    def synthesize(self, text: str) -> Dict[str, Any]:
        normalized = normalize_text(text)
        meaning = parse_meaning(normalized)
        prosody = plan_prosody(meaning)
        performance_plan = build_phase2_plan(normalized, meaning, prosody)
        composition_plan = build_composition_plan(normalized, meaning, performance_plan.to_dict())
        phonemes = text_to_phonemes(normalized, prosody=prosody)
        performance_graph = build_performance_graph(normalized, meaning, prosody)
        streaming_plan = build_streaming_plan(normalized, meaning, performance_plan.to_dict())
        audio = self.synthesizer.synthesize(
            phonemes,
            performance_graph=performance_graph,
        )
        live_playback_plan = build_live_playback_plan(streaming_plan, len(audio), sample_rate=self.synthesizer.sample_rate)

        return {
            "text": text,
            "normalized_text": normalized,
            "meaning": meaning,
            "prosody": prosody,
            "performance_plan": performance_plan.to_dict(),
            "composition_plan": composition_plan.to_dict(),
            "streaming_plan": streaming_plan.to_dict(),
            "live_playback_plan": live_playback_plan.to_dict(),
            "phonemes": phonemes,
            "performance_graph": performance_graph.to_dict(),
            "audio": audio,
        }
