from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .phase5 import CompositionPlan


@dataclass
class MusicRenderer:
    sample_rate: int = 22050
    beat_seconds: float = 0.25

    def render(self, composition_plan: CompositionPlan) -> List[float]:
        audio: List[float] = []
        for bar in composition_plan.bars:
            chord_base = self._chord_base_frequency(bar.chord, composition_plan.music_dna.key)
            bar_samples = int(self.sample_rate * self.beat_seconds * bar.duration_beats)
            for n in range(bar_samples):
                t = n / self.sample_rate
                carrier = math.sin(2.0 * math.pi * chord_base * t)
                harmonic = 0.35 * math.sin(2.0 * math.pi * (chord_base * 2.0) * t)
                rhythm = 0.12 * math.sin(2.0 * math.pi * (composition_plan.music_dna.tempo / 60.0) * t)
                envelope = self._envelope(n, bar_samples)
                intensity = composition_plan.music_dna.intensity
                audio.append((carrier + harmonic + rhythm) * envelope * 0.16 * intensity)
            audio.extend([0.0] * int(self.sample_rate * 0.03))
        return audio

    def _chord_base_frequency(self, chord: str, key: str) -> float:
        root_map = {
            "C": 261.63,
            "D": 293.66,
            "E": 329.63,
            "F": 349.23,
            "G": 392.00,
            "A": 440.00,
            "B": 493.88,
        }
        base = root_map.get(key[:1].upper(), 261.63)
        if chord.endswith("m") or "m7" in chord:
            return base * 0.97
        if chord.endswith("sus4"):
            return base * 1.05
        if chord.endswith("add9"):
            return base * 1.08
        return base

    def _envelope(self, n: int, total: int) -> float:
        if total <= 1:
            return 1.0
        x = n / (total - 1)
        if x < 0.08:
            return x / 0.08
        if x > 0.92:
            return max(0.0, (1.0 - x) / 0.08)
        return 1.0


@dataclass
class SingingPlan:
    lyrics: str
    notes: List[str] = field(default_factory=list)
    syllable_durations: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lyrics": self.lyrics,
            "notes": self.notes,
            "syllable_durations": self.syllable_durations,
        }


def build_singing_plan(lyrics: str, composition_plan: CompositionPlan) -> SingingPlan:
    words = [w for w in lyrics.split() if w]
    notes = []
    durations = []
    scale = ["1", "2", "3", "5", "6", "5", "3", "2"]
    for index, word in enumerate(words):
        notes.append(f"{composition_plan.music_dna.key}{scale[index % len(scale)]}")
        durations.append(0.22 if len(word) <= 4 else 0.28)
    return SingingPlan(lyrics=lyrics, notes=notes, syllable_durations=durations)


@dataclass
class FusionPlan:
    speech_text: str
    music_audio_hint: str
    overlay_mode: str = "speech_with_soft_music"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "speech_text": self.speech_text,
            "music_audio_hint": self.music_audio_hint,
            "overlay_mode": self.overlay_mode,
        }


def build_fusion_plan(speech_text: str, composition_plan: CompositionPlan) -> FusionPlan:
    mood = composition_plan.music_dna.mood
    return FusionPlan(
        speech_text=speech_text,
        music_audio_hint=f"soft-{mood}-pad",
        overlay_mode="speech_with_soft_music" if composition_plan.can_instrumentalize else "speech_only",
    )


@dataclass
class PersonalityMemory:
    preferred_style: str = "friendly"
    preferred_energy: float = 0.7
    favorite_voice: str = "axima"
    favorite_music_mood: str = "neutral"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "preferred_style": self.preferred_style,
            "preferred_energy": self.preferred_energy,
            "favorite_voice": self.favorite_voice,
            "favorite_music_mood": self.favorite_music_mood,
        }
