from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .performance_graph import PerformanceGraph
from .phase8 import AudioControlMap, AudioControlPoint, AudioRenderingProfile, Phase8Plan


@dataclass
class SimpleSynthesizer:
    sample_rate: int = 22050
    phoneme_seconds: float = 0.09

    def synthesize(
        self,
        phonemes: Iterable[str],
        performance_graph: PerformanceGraph | None = None,
        phase8_plan: Phase8Plan | None = None,
    ) -> List[float]:
        phoneme_list = list(phonemes)
        if not phoneme_list:
            return [0.0]

        energy = 1.0
        pitch = 1.0
        pause_points: Sequence[float] = []
        pitch_points: Sequence[float] = []
        energy_points: Sequence[float] = []
        duration_points: Sequence[float] = []
        rendering_profile = AudioRenderingProfile(sample_rate=self.sample_rate)
        control_map: AudioControlMap | None = None

        if performance_graph and performance_graph.nodes:
            energy = sum(node.energy for node in performance_graph.nodes) / len(performance_graph.nodes)
            pitch = sum(node.pitch for node in performance_graph.nodes) / len(performance_graph.nodes)

        if phase8_plan is not None:
            control_map = phase8_plan.control_map
            rendering_profile = phase8_plan.rendering_profile
            pause_points = [c.pause_after for c in control_map.controls]
            pitch_points = [c.pitch_scale for c in control_map.controls]
            energy_points = [c.energy_scale for c in control_map.controls]
            duration_points = [c.duration_scale for c in control_map.controls]
            energy *= rendering_profile.expressive_range
            pitch *= 1.0 + (rendering_profile.base_voice_frequency - 145.0) / 1450.0

        base_freq = rendering_profile.base_voice_frequency * pitch
        samples: List[float] = []

        for index, token in enumerate(phoneme_list):
            control = control_map.controls[index] if control_map and index < len(control_map.controls) else None
            token_pitch = pitch_points[index] if index < len(pitch_points) else 1.0
            token_energy = energy_points[index] if index < len(energy_points) else 1.0
            token_duration = duration_points[index] if index < len(duration_points) else self.phoneme_seconds
            pause_after = pause_points[index] if index < len(pause_points) else None

            freq = base_freq + (ord(token[0]) % 24) * 8.0 if token else base_freq
            freq *= token_pitch if control else 1.0
            duration = max(0.04, token_duration * (0.85 if token in {"_", "~"} else 1.0))
            count = max(1, int(rendering_profile.sample_rate * duration))
            formant_shift = 1.0 + rendering_profile.harmonic_depth * 0.02

            for n in range(count):
                t = n / rendering_profile.sample_rate
                tone = math.sin(2.0 * math.pi * freq * t)
                harmonic = rendering_profile.harmonic_depth * math.sin(2.0 * math.pi * (freq * 2.0 * formant_shift) * t)
                breath = rendering_profile.breathiness * math.sin(2.0 * math.pi * (freq * 0.5) * t)
                envelope = self._envelope(n, count)
                emphasis = control.emphasis if control else 1.0
                value = (tone + harmonic + breath) * envelope * 0.18 * energy * token_energy * emphasis
                samples.append(value)

            if pause_after is not None:
                samples.extend(self._silence(max(rendering_profile.silence_padding, pause_after)))
            elif performance_graph and index < len(performance_graph.nodes):
                samples.extend(self._silence(performance_graph.nodes[index].pause_after))
            else:
                samples.extend(self._silence(0.01))

        return samples

    def _silence(self, seconds: float) -> List[float]:
        count = max(0, int(self.sample_rate * seconds))
        return [0.0] * count

    def _envelope(self, n: int, total: int) -> float:
        if total <= 1:
            return 1.0
        x = n / (total - 1)
        if x < 0.12:
            return x / 0.12
        if x > 0.88:
            return max(0.0, (1.0 - x) / 0.12)
        return 1.0
