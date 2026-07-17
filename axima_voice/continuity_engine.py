from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ContinuityState:
    carry_energy: float = 1.0
    carry_pitch: float = 1.0
    carry_pause: float = 0.0
    carry_emotion: str = "neutral"

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


class ContinuityEngine:
    def blend_chunk_audio(
        self,
        chunk_audio: List[float],
        previous_state: ContinuityState,
        emotion: str,
    ) -> List[float]:
        if not chunk_audio:
            return [0.0]
        energy_gain = previous_state.carry_energy
        pitch_gain = previous_state.carry_pitch
        if emotion == "excited":
            energy_gain *= 1.04
            pitch_gain *= 1.02
        elif emotion == "soft":
            energy_gain *= 0.96
            pitch_gain *= 0.99
        elif emotion == "urgent":
            energy_gain *= 1.06
            pitch_gain *= 1.01
        # Lightweight continuity: carry-over is applied as a subtle gain envelope.
        blended = [sample * energy_gain * pitch_gain for sample in chunk_audio]
        return blended

    def next_state(self, emotion: str, energy: float = 1.0, pitch: float = 1.0, pause: float = 0.0) -> ContinuityState:
        return ContinuityState(
            carry_energy=energy,
            carry_pitch=pitch,
            carry_pause=pause,
            carry_emotion=emotion,
        )
