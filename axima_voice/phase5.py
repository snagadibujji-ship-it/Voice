from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class MusicDNA:
    mood: str = "neutral"
    tempo: int = 120
    key: str = "C"
    scale: str = "major"
    intensity: float = 0.5
    brightness: float = 0.5


@dataclass
class CompositionBar:
    index: int
    chord: str
    melody_hint: str
    rhythm_hint: str
    duration_beats: float = 4.0


@dataclass
class CompositionPlan:
    music_dna: MusicDNA
    bars: List[CompositionBar] = field(default_factory=list)
    can_sing: bool = True
    can_instrumentalize: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "music_dna": self.music_dna.__dict__,
            "bars": [bar.__dict__ for bar in self.bars],
            "can_sing": self.can_sing,
            "can_instrumentalize": self.can_instrumentalize,
        }


def infer_music_dna(text: str, meaning: Dict[str, Any], performance_plan: Dict[str, Any]) -> MusicDNA:
    mood = performance_plan.get("mood", meaning.get("mood", "neutral"))
    if mood == "excited":
        return MusicDNA(mood=mood, tempo=148, key="D", scale="minor", intensity=0.85, brightness=0.72)
    if mood == "soft":
        return MusicDNA(mood=mood, tempo=84, key="A", scale="minor", intensity=0.35, brightness=0.32)
    if mood == "urgent":
        return MusicDNA(mood=mood, tempo=136, key="E", scale="minor", intensity=0.78, brightness=0.68)
    if "music" in text.lower() or meaning.get("intent") == "music":
        return MusicDNA(mood=mood, tempo=128, key="F", scale="major", intensity=0.65, brightness=0.6)
    return MusicDNA(mood=mood)


def build_composition_plan(text: str, meaning: Dict[str, Any], performance_plan: Dict[str, Any]) -> CompositionPlan:
    music_dna = infer_music_dna(text, meaning, performance_plan)
    words = [w for w in text.split() if w]

    chords = [
        f"{music_dna.key}{'m' if music_dna.scale == 'minor' else ''}",
        f"{music_dna.key}{'m' if music_dna.scale == 'minor' else ''}7",
        f"{music_dna.key}sus4",
        f"{music_dna.key}add9",
    ]

    bars: List[CompositionBar] = []
    bar_count = max(2, min(8, len(words) // 2 + 1))
    for index in range(bar_count):
        chord = chords[index % len(chords)]
        melody_hint = f"rise-{index % 3}" if music_dna.intensity > 0.6 else f"step-{index % 2}"
        rhythm_hint = "driving" if music_dna.tempo >= 130 else "gentle"
        bars.append(
            CompositionBar(
                index=index,
                chord=chord,
                melody_hint=melody_hint,
                rhythm_hint=rhythm_hint,
                duration_beats=4.0,
            )
        )

    return CompositionPlan(music_dna=music_dna, bars=bars)
