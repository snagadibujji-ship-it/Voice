from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .phase7 import RealismPlan


@dataclass
class AudioControlPoint:
    index: int
    pitch_scale: float
    energy_scale: float
    duration_scale: float
    pause_after: float
    emphasis: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class AudioControlMap:
    voice_name: str
    emotion: str
    controls: List[AudioControlPoint] = field(default_factory=list)
    smoothing_window: int = 3
    coarticulation_strength: float = 0.75
    expressive_bias: float = 0.82

    def to_dict(self) -> Dict[str, Any]:
        return {
            "voice_name": self.voice_name,
            "emotion": self.emotion,
            "controls": [control.to_dict() for control in self.controls],
            "smoothing_window": self.smoothing_window,
            "coarticulation_strength": self.coarticulation_strength,
            "expressive_bias": self.expressive_bias,
        }


@dataclass
class AudioRenderingProfile:
    sample_rate: int = 22050
    base_voice_frequency: float = 145.0
    harmonic_depth: float = 0.28
    breathiness: float = 0.08
    formant_stability: float = 0.92
    expressive_range: float = 0.86
    silence_padding: float = 0.02

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class Phase8Plan:
    realism_plan: RealismPlan
    control_map: AudioControlMap
    rendering_profile: AudioRenderingProfile
    articulation_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "realism_plan": self.realism_plan.to_dict(),
            "control_map": self.control_map.to_dict(),
            "rendering_profile": self.rendering_profile.to_dict(),
            "articulation_notes": self.articulation_notes,
        }


def _safe_index_ratio(index: int, total: int) -> float:
    if total <= 1:
        return 0.0
    return index / (total - 1)


def build_audio_control_map(realism_plan: RealismPlan) -> AudioControlMap:
    phoneme_words = realism_plan.phoneme_words
    emotion = realism_plan.emotion_plan.emotion
    controls: List[AudioControlPoint] = []
    for index, word in enumerate(phoneme_words):
        emphasis = 1.08 if word.word.lower() in realism_plan.emotion_plan.emphasis_words else 1.0
        pitch_scale = realism_plan.prosody_curve.pitch_points[index] if index < len(realism_plan.prosody_curve.pitch_points) else 1.0
        energy_scale = realism_plan.prosody_curve.energy_points[index] if index < len(realism_plan.prosody_curve.energy_points) else 1.0
        duration_scale = realism_plan.prosody_curve.duration_points[index] if index < len(realism_plan.prosody_curve.duration_points) else 0.11
        pause_after = realism_plan.prosody_curve.pause_points[index] if index < len(realism_plan.prosody_curve.pause_points) else 0.0
        controls.append(
            AudioControlPoint(
                index=index,
                pitch_scale=pitch_scale,
                energy_scale=energy_scale,
                duration_scale=duration_scale,
                pause_after=pause_after,
                emphasis=emphasis,
            )
        )
    return AudioControlMap(
        voice_name=realism_plan.identity.name,
        emotion=emotion,
        controls=controls,
        smoothing_window=3,
        coarticulation_strength=0.78,
        expressive_bias=0.86,
    )


def build_rendering_profile(realism_plan: RealismPlan, control_map: AudioControlMap) -> AudioRenderingProfile:
    if control_map.emotion == "excited":
        return AudioRenderingProfile(
            sample_rate=22050,
            base_voice_frequency=152.0,
            harmonic_depth=0.34,
            breathiness=0.07,
            formant_stability=0.88,
            expressive_range=0.94,
            silence_padding=0.012,
        )
    if control_map.emotion == "soft":
        return AudioRenderingProfile(
            sample_rate=22050,
            base_voice_frequency=138.0,
            harmonic_depth=0.22,
            breathiness=0.1,
            formant_stability=0.96,
            expressive_range=0.7,
            silence_padding=0.03,
        )
    if control_map.emotion == "urgent":
        return AudioRenderingProfile(
            sample_rate=22050,
            base_voice_frequency=149.0,
            harmonic_depth=0.31,
            breathiness=0.06,
            formant_stability=0.9,
            expressive_range=0.9,
            silence_padding=0.01,
        )
    return AudioRenderingProfile(
        sample_rate=22050,
        base_voice_frequency=145.0,
        harmonic_depth=0.28,
        breathiness=0.08,
        formant_stability=0.92,
        expressive_range=0.86,
        silence_padding=0.02,
    )


def build_phase8_plan(realism_plan: RealismPlan) -> Phase8Plan:
    control_map = build_audio_control_map(realism_plan)
    rendering_profile = build_rendering_profile(realism_plan, control_map)
    articulation_notes = [
        "apply_pitch_to_rendering",
        "shape_energy_per_token",
        "reduce_silence_for_function_words",
        "smooth_neighboring_controls",
        "preserve_axa_identity",
    ]
    return Phase8Plan(
        realism_plan=realism_plan,
        control_map=control_map,
        rendering_profile=rendering_profile,
        articulation_notes=articulation_notes,
    )
