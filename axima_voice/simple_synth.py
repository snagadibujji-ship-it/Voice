from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .performance_graph import PerformanceGraph
from .phase8 import AudioControlMap, AudioRenderingProfile, Phase8Plan
from .phase9 import Phase9Plan


@dataclass
class SimpleSynthesizer:
    sample_rate: int = 22050
    phoneme_seconds: float = 0.09

    def synthesize(
        self,
        phonemes: Iterable[str],
        performance_graph: PerformanceGraph | None = None,
        phase8_plan: Phase8Plan | None = None,
        phase9_plan: Phase9Plan | None = None,
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
        runtime_control = None

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

        if phase9_plan is not None:
            runtime_control = phase9_plan.runtime_control
            if runtime_control.emotion in {"excited", "urgent"}:
                energy *= 1.06
                pitch *= 1.02
            elif runtime_control.emotion == "soft":
                energy *= 0.92
                pitch *= 0.98
            else:
                energy *= 1.0
            rendering_profile = phase9_plan.phase8_plan.rendering_profile

        base_freq = rendering_profile.base_voice_frequency * pitch
        samples: List[float] = []
        word_count = max(1, len(phoneme_list))
        runtime_pause_map = self._build_runtime_pause_map(phase9_plan, word_count)
        runtime_frame_map = self._build_runtime_frame_map(phase9_plan, word_count)

        for index, token in enumerate(phoneme_list):
            control = control_map.controls[index] if control_map and index < len(control_map.controls) else None
            token_pitch = pitch_points[index] if index < len(pitch_points) else 1.0
            token_energy = energy_points[index] if index < len(energy_points) else 1.0
            token_duration = duration_points[index] if index < len(duration_points) else self.phoneme_seconds
            pause_after = pause_points[index] if index < len(pause_points) else None
            runtime_frame = runtime_frame_map[index] if index < len(runtime_frame_map) else None

            if runtime_frame is not None:
                token_pitch *= runtime_frame["pitch_scale"]
                token_energy *= runtime_frame["energy_scale"]
                token_duration *= runtime_frame["duration_scale"]
                if pause_after is None:
                    pause_after = runtime_frame["pause_scale"] * 0.01

            if runtime_control is not None:
                if token in {"_", "~"}:
                    token_duration *= 0.82
                if index in runtime_pause_map:
                    pause_after = max(pause_after or 0.0, runtime_pause_map[index])

            freq = base_freq + (ord(token[0]) % 24) * 8.0 if token else base_freq
            freq *= token_pitch if control else token_pitch
            duration = max(0.035, token_duration * (0.82 if token in {"_", "~"} else 1.0))
            count = max(1, int(rendering_profile.sample_rate * duration))
            formant_shift = 1.0 + rendering_profile.harmonic_depth * 0.02
            breathiness_boost = rendering_profile.breathiness
            if runtime_control is not None and runtime_control.emotion == "soft":
                breathiness_boost *= 1.5
            elif runtime_control is not None and runtime_control.emotion in {"excited", "urgent"}:
                breathiness_boost *= 0.85

            for n in range(count):
                t = n / rendering_profile.sample_rate
                tone = math.sin(2.0 * math.pi * freq * t)
                harmonic = rendering_profile.harmonic_depth * math.sin(2.0 * math.pi * (freq * 2.0 * formant_shift) * t)
                breath = breathiness_boost * math.sin(2.0 * math.pi * (freq * 0.5) * t)
                envelope = self._envelope(n, count)
                emphasis = control.emphasis if control else 1.0
                runtime_emphasis = runtime_frame["energy_scale"] if runtime_frame is not None else 1.0
                value = (tone + harmonic + breath) * envelope * 0.18 * energy * token_energy * emphasis * runtime_emphasis
                samples.append(value)

            if pause_after is not None:
                samples.extend(self._silence(max(rendering_profile.silence_padding, pause_after)))
            elif performance_graph and index < len(performance_graph.nodes):
                samples.extend(self._silence(performance_graph.nodes[index].pause_after))
            else:
                samples.extend(self._silence(0.01))

        return samples

    def _build_runtime_pause_map(self, phase9_plan: Phase9Plan | None, word_count: int) -> dict[int, float]:
        if phase9_plan is None:
            return {}
        pause_map: dict[int, float] = {}
        for breath in phase9_plan.runtime_control.breath_events:
            if 0 <= breath.index < word_count:
                pause_map[breath.index] = max(pause_map.get(breath.index, 0.0), breath.pause_seconds)
        for cue in phase9_plan.runtime_control.presence_cues:
            if cue.enabled and 0 <= cue.index < word_count:
                pause_map[cue.index] = max(pause_map.get(cue.index, 0.0), cue.duration_seconds)
        return pause_map

    def _build_runtime_frame_map(self, phase9_plan: Phase9Plan | None, word_count: int) -> dict[int, dict[str, float]]:
        if phase9_plan is None:
            return {}
        frame_map: dict[int, dict[str, float]] = {}
        for frame in phase9_plan.runtime_control.emotion_frames:
            if 0 <= frame.index < word_count:
                frame_map[frame.index] = {
                    "pitch_scale": frame.pitch_scale,
                    "energy_scale": frame.energy_scale,
                    "duration_scale": frame.duration_scale,
                    "pause_scale": frame.pause_scale,
                }
        return frame_map

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
