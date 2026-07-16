from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List

from .performance_graph import PerformanceGraph


@dataclass
class SimpleSynthesizer:
    sample_rate: int = 22050
    phoneme_seconds: float = 0.09

    def synthesize(self, phonemes: Iterable[str], performance_graph: PerformanceGraph | None = None) -> List[float]:
        phoneme_list = list(phonemes)
        if not phoneme_list:
            return [0.0]

        energy = 1.0
        pitch = 1.0
        if performance_graph and performance_graph.nodes:
            energy = sum(node.energy for node in performance_graph.nodes) / len(performance_graph.nodes)
            pitch = sum(node.pitch for node in performance_graph.nodes) / len(performance_graph.nodes)

        base_freq = 140.0 * pitch
        samples: List[float] = []

        for index, token in enumerate(phoneme_list):
            freq = base_freq + (ord(token[0]) % 24) * 8.0 if token else base_freq
            duration = self.phoneme_seconds
            count = max(1, int(self.sample_rate * duration))
            for n in range(count):
                t = n / self.sample_rate
                tone = math.sin(2.0 * math.pi * freq * t)
                harmonic = 0.35 * math.sin(2.0 * math.pi * (freq * 2.0) * t)
                envelope = self._envelope(n, count)
                value = (tone + harmonic) * envelope * 0.18 * energy
                samples.append(value)

            if performance_graph and index < len(performance_graph.nodes):
                pause = performance_graph.nodes[index].pause_after
                samples.extend(self._silence(pause))
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
