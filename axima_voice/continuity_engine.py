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
        # Runtime continuity modifies samples rather than metadata: emotion/energy/pitch
        # shape the waveform, pause carry inserts silence, and the first samples are
        # cross-faded from the previous state to avoid chunk-edge discontinuities.
        shaped = [sample * energy_gain * pitch_gain for sample in chunk_audio]
        if abs(pitch_gain - 1.0) > 1e-9 and len(shaped) > 2:
            shaped = self._pitch_resample(shaped, pitch_gain)
        if previous_state.carry_emotion != emotion:
            emotion_tilt = 1.015 if emotion in {"excited", "urgent"} else 0.985
            shaped = [sample * emotion_tilt for sample in shaped]
        fade_count = min(32, len(shaped))
        for index in range(fade_count):
            shaped[index] *= (index + 1) / fade_count
        pause_samples = max(0, int(22050 * previous_state.carry_pause))
        return ([0.0] * pause_samples) + shaped

    def _pitch_resample(self, audio: List[float], pitch_gain: float) -> List[float]:
        output: List[float] = []
        cursor = 0.0
        step = max(0.5, min(1.5, pitch_gain))
        while int(cursor) < len(audio):
            output.append(audio[int(cursor)])
            cursor += step
        return output or [0.0]

    def next_state(
        self, emotion: str, energy: float = 1.0, pitch: float = 1.0, pause: float = 0.0
    ) -> ContinuityState:
        return ContinuityState(
            carry_energy=energy,
            carry_pitch=pitch,
            carry_pause=pause,
            carry_emotion=emotion,
        )
