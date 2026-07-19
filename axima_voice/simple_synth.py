from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .emotion_engine import EmotionProfile
from .performance_graph import PerformanceGraph
from .phase8 import AudioControlMap, AudioRenderingProfile, Phase8Plan
from .phase9 import Phase9Plan
from .runtime_engine import (
    RuntimeExecutionController,
    RuntimeExecutionResult,
    interleave_runtime_breathing,
)
from .voice_identity import VoiceProfile


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
        runtime_controller: RuntimeExecutionController | None = None,
        voice_profile: VoiceProfile | None = None,
        emotion_profile: EmotionProfile | None = None,
        vocal_events: dict[str, int] | None = None,
    ) -> RuntimeExecutionResult:
        phoneme_list = list(phonemes)
        if voice_profile is not None and voice_profile.pronunciation_preferences:
            phoneme_list = [
                voice_profile.pronunciation_preferences.get(token, token)
                for token in phoneme_list
            ]
        if not phoneme_list:
            controller = runtime_controller or RuntimeExecutionController()
            controller.begin_generation()
            controller.mark_first_audio()
            controller.finish_generation()
            return RuntimeExecutionResult(
                audio=[0.0], state=controller.state, metrics=controller.metrics
            )

        controller = runtime_controller or RuntimeExecutionController()
        controller.begin_generation()

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
            energy = sum(node.energy for node in performance_graph.nodes) / len(
                performance_graph.nodes
            )
            pitch = sum(node.pitch for node in performance_graph.nodes) / len(
                performance_graph.nodes
            )

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
                energy *= 1.08
                pitch *= 1.025
            elif runtime_control.emotion == "soft":
                energy *= 0.9
                pitch *= 0.97
            rendering_profile = phase9_plan.phase8_plan.rendering_profile

        if emotion_profile is not None:
            energy *= emotion_profile.energy * (1.0 + emotion_profile.intensity * 0.08)
            pitch *= 1.0 + emotion_profile.pitch_bias

        if voice_profile is not None:
            rendering_profile.sample_rate = voice_profile.sample_rate
            rendering_profile.base_voice_frequency = voice_profile.base_pitch
            energy *= voice_profile.energy
            pitch *= voice_profile.pitch_range
            if runtime_control is not None and runtime_control.emotion == "neutral":
                runtime_control.emotion = voice_profile.emotion_bias

        base_freq = rendering_profile.base_voice_frequency * pitch
        samples: List[float] = []
        word_count = max(1, len(phoneme_list))
        runtime_pause_map = self._build_runtime_pause_map(phase9_plan, word_count)
        runtime_frame_map = self._build_runtime_frame_map(phase9_plan, word_count)
        first_audio_emitted = False

        for index, token in enumerate(phoneme_list):
            if controller.interrupted:
                controller.finish_generation()
                audio = interleave_runtime_breathing(
                    samples,
                    sentence_length=word_count,
                    emotion=runtime_control.emotion if runtime_control else "neutral",
                )
                return RuntimeExecutionResult(
                    audio=audio,
                    state=controller.state,
                    metrics=controller.metrics,
                    interrupted=True,
                    stop_reason=controller.stop_reason,
                )

            if controller.paused:
                controller.finish_generation()
                audio = interleave_runtime_breathing(
                    samples,
                    sentence_length=word_count,
                    emotion=runtime_control.emotion if runtime_control else "neutral",
                )
                return RuntimeExecutionResult(
                    audio=audio,
                    state=controller.state,
                    metrics=controller.metrics,
                    paused=True,
                    stop_reason=controller.stop_reason,
                )

            control = (
                control_map.controls[index]
                if control_map and index < len(control_map.controls)
                else None
            )
            token_pitch = pitch_points[index] if index < len(pitch_points) else 1.0
            token_energy = energy_points[index] if index < len(energy_points) else 1.0
            token_duration = (
                duration_points[index]
                if index < len(duration_points)
                else self.phoneme_seconds
                / (
                    (voice_profile.speaking_rate if voice_profile else 1.0)
                    * (emotion_profile.speaking_rate if emotion_profile else 1.0)
                )
            )
            pause_after = pause_points[index] if index < len(pause_points) else None
            runtime_frame = (
                runtime_frame_map[index] if index < len(runtime_frame_map) else None
            )

            if runtime_frame is not None:
                token_pitch *= runtime_frame["pitch_scale"]
                token_energy *= runtime_frame["energy_scale"]
                token_duration *= runtime_frame["duration_scale"]
                if pause_after is None:
                    pause_after = (
                        runtime_frame["pause_scale"]
                        * 0.01
                        * (voice_profile.pause_style if voice_profile else 1.0)
                        * (emotion_profile.pause_behavior if emotion_profile else 1.0)
                    )

            if runtime_control is not None:
                if token in {"_", "~"}:
                    token_duration *= 0.8
                if index in runtime_pause_map:
                    pause_after = max(
                        pause_after or 0.0,
                        runtime_pause_map[index]
                        * (voice_profile.pause_style if voice_profile else 1.0)
                        * (emotion_profile.pause_behavior if emotion_profile else 1.0),
                    )
                if runtime_control.emotion == "soft":
                    token_duration *= 1.05
                elif runtime_control.emotion in {"excited", "urgent"}:
                    token_duration *= 0.95

            freq = base_freq + (ord(token[0]) % 24) * 8.0 if token else base_freq
            freq *= token_pitch
            duration = max(
                0.032, token_duration * (0.82 if token in {"_", "~"} else 1.0)
            )
            count = max(1, int(rendering_profile.sample_rate * duration))
            formant_shift = 1.0 + rendering_profile.harmonic_depth * 0.02
            breathiness_boost = (
                rendering_profile.breathiness
                * (voice_profile.breathing_style if voice_profile else 1.0)
                * (emotion_profile.breathing_frequency if emotion_profile else 1.0)
            )
            if runtime_control is not None and runtime_control.emotion == "soft":
                breathiness_boost *= 1.55
            elif runtime_control is not None and runtime_control.emotion in {
                "excited",
                "urgent",
            }:
                breathiness_boost *= 0.82

            token_runtime_energy = token_energy
            if runtime_control is not None:
                token_runtime_energy *= self._runtime_energy_boost(
                    runtime_control.emotion, index, word_count
                )
                token_runtime_energy *= self._presence_boost(
                    runtime_control.emotion, index, word_count
                )
                token_runtime_energy *= self._breath_boost(runtime_pause_map, index)

            for n in range(count):
                if controller.interrupted:
                    controller.finish_generation()
                    audio = interleave_runtime_breathing(
                        samples,
                        sentence_length=word_count,
                        emotion=runtime_control.emotion
                        if runtime_control
                        else "neutral",
                    )
                    return RuntimeExecutionResult(
                        audio=audio,
                        state=controller.state,
                        metrics=controller.metrics,
                        interrupted=True,
                        stop_reason=controller.stop_reason,
                    )
                t = n / rendering_profile.sample_rate
                tone = math.sin(2.0 * math.pi * freq * t)
                harmonic = rendering_profile.harmonic_depth * math.sin(
                    2.0 * math.pi * (freq * 2.0 * formant_shift) * t
                )
                breath = breathiness_boost * math.sin(2.0 * math.pi * (freq * 0.5) * t)
                runtime_motion = (
                    self._sentence_motion(runtime_control.emotion, index, word_count)
                    if runtime_control is not None
                    else 1.0
                )
                envelope = self._envelope(n, count)
                emphasis = control.emphasis if control else 1.0
                attack = 1.0
                if emotion_profile is not None and n < max(1, int(count * 0.08)):
                    attack = 1.0 + emotion_profile.intensity * 0.05
                value = (
                    (tone + harmonic + breath)
                    * envelope
                    * 0.18
                    * energy
                    * token_energy
                    * emphasis
                    * runtime_motion
                    * token_runtime_energy
                    * (emotion_profile.emphasis if emotion_profile else 1.0)
                    * attack
                )
                if not first_audio_emitted and abs(value) > 1e-9:
                    controller.mark_first_audio()
                    first_audio_emitted = True
                samples.append(value)

            if pause_after is not None:
                samples.extend(
                    self._silence(max(rendering_profile.silence_padding, pause_after))
                )
            elif performance_graph and index < len(performance_graph.nodes):
                samples.extend(
                    self._silence(performance_graph.nodes[index].pause_after)
                )
            else:
                samples.extend(self._silence(0.01))

        if vocal_events:
            samples = self._insert_vocal_events(samples, vocal_events, emotion_profile)

        controller.finish_generation()
        audio = interleave_runtime_breathing(
            samples,
            sentence_length=word_count,
            emotion=runtime_control.emotion if runtime_control else "neutral",
        )
        return RuntimeExecutionResult(
            audio=audio, state=controller.state, metrics=controller.metrics
        )

    def _insert_vocal_events(
        self,
        samples: List[float],
        vocal_events: dict[str, int],
        emotion_profile: EmotionProfile | None,
    ) -> List[float]:
        output = list(samples)
        midpoint = max(1, len(output) // 2)
        breath = [0.0] * int(self.sample_rate * 0.025)
        hesitation = [0.0] * int(self.sample_rate * 0.06)
        laugh = [
            0.035 * math.sin(2.0 * math.pi * 9.0 * (n / self.sample_rate))
            for n in range(int(self.sample_rate * 0.08))
        ]
        if vocal_events.get("breaths", 0) > 0:
            output = output[:midpoint] + breath + output[midpoint:]
        if vocal_events.get("hesitations", 0) > 0:
            quarter = max(1, len(output) // 4)
            output = output[:quarter] + hesitation + output[quarter:]
        if vocal_events.get("laughter", 0) > 0:
            output = laugh + output
        if emotion_profile is not None and emotion_profile.name == "whisper":
            output = [sample * 0.45 for sample in output]
        return output

    def _build_runtime_pause_map(
        self, phase9_plan: Phase9Plan | None, word_count: int
    ) -> dict[int, float]:
        if phase9_plan is None:
            return {}
        pause_map: dict[int, float] = {}
        for breath in phase9_plan.runtime_control.breath_events:
            if 0 <= breath.index < word_count:
                pause_map[breath.index] = max(
                    pause_map.get(breath.index, 0.0), breath.pause_seconds
                )
        for cue in phase9_plan.runtime_control.presence_cues:
            if cue.enabled and 0 <= cue.index < word_count:
                pause_map[cue.index] = max(
                    pause_map.get(cue.index, 0.0), cue.duration_seconds
                )
        return pause_map

    def _build_runtime_frame_map(
        self, phase9_plan: Phase9Plan | None, word_count: int
    ) -> dict[int, dict[str, float]]:
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

    def _runtime_energy_boost(self, emotion: str, index: int, total: int) -> float:
        if total <= 1:
            return 1.0
        ratio = index / max(1, total - 1)
        if emotion == "excited":
            return 1.0 + 0.05 * ratio
        if emotion == "soft":
            return 0.95 - 0.02 * ratio
        if emotion == "urgent":
            return 1.05 + 0.03 * ratio
        return 1.0 + 0.01 * (0.5 - ratio)

    def _presence_boost(self, emotion: str, index: int, total: int) -> float:
        if total <= 1:
            return 1.0
        if index == 0 and total > 2:
            return 0.98 if emotion in {"soft", "neutral"} else 1.01
        if index == total - 1:
            return 1.02 if emotion in {"excited", "urgent"} else 1.0
        return 1.0

    def _breath_boost(self, pause_map: dict[int, float], index: int) -> float:
        if index in pause_map:
            return 1.0 + min(0.08, pause_map[index] * 0.15)
        return 1.0

    def _sentence_motion(self, emotion: str | None, index: int, total: int) -> float:
        if emotion is None or total <= 1:
            return 1.0
        ratio = index / max(1, total - 1)
        if emotion == "excited":
            return 1.02 + 0.05 * ratio
        if emotion == "soft":
            return 0.98 - 0.02 * ratio
        if emotion == "urgent":
            return 1.03 + 0.02 * ratio
        return 1.0 + 0.01 * (0.5 - ratio)

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
