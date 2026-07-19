from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class VoiceDNA:
    warmth: float = 0.7
    curiosity: float = 0.6
    confidence: float = 0.8
    energy: float = 0.6
    humor: float = 0.2


@dataclass
class PerformancePlan:
    mood: str
    speaking_rate: float
    pitch_multiplier: float
    energy_multiplier: float
    pauses: List[float] = field(default_factory=list)
    emphasis_tokens: List[str] = field(default_factory=list)
    voice_dna: VoiceDNA = field(default_factory=VoiceDNA)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mood": self.mood,
            "speaking_rate": self.speaking_rate,
            "pitch_multiplier": self.pitch_multiplier,
            "energy_multiplier": self.energy_multiplier,
            "pauses": self.pauses,
            "emphasis_tokens": self.emphasis_tokens,
            "voice_dna": self.voice_dna.__dict__,
        }


def infer_mood(text: str, meaning: Dict[str, Any]) -> str:
    text_l = text.lower()
    if "!" in text_l or meaning.get("emotion") == "excited":
        return "excited"
    if any(word in text_l for word in ["sorry", "sad", "unfortunately"]):
        return "soft"
    if any(word in text_l for word in ["now", "urgent", "fast"]):
        return "urgent"
    return meaning.get("mood", "neutral")


def build_phase2_plan(
    text: str, meaning: Dict[str, Any], prosody: Dict[str, Any]
) -> PerformancePlan:
    mood = infer_mood(text, meaning)
    base_speed = float(prosody.get("speed", 1.0))
    base_pitch = float(prosody.get("pitch", 1.0))
    base_energy = float(prosody.get("energy", 1.0))

    if mood == "excited":
        return PerformancePlan(
            mood=mood,
            speaking_rate=base_speed * 1.12,
            pitch_multiplier=base_pitch * 1.08,
            energy_multiplier=base_energy * 1.15,
            pauses=[0.015, 0.02],
            emphasis_tokens=[text.split(" ")[0]] if text.split(" ") else [],
            voice_dna=VoiceDNA(
                warmth=0.75, curiosity=0.7, confidence=0.85, energy=0.85, humor=0.25
            ),
        )

    if mood == "soft":
        return PerformancePlan(
            mood=mood,
            speaking_rate=base_speed * 0.92,
            pitch_multiplier=base_pitch * 0.95,
            energy_multiplier=base_energy * 0.88,
            pauses=[0.03, 0.04],
            emphasis_tokens=[],
            voice_dna=VoiceDNA(
                warmth=0.9, curiosity=0.45, confidence=0.55, energy=0.45, humor=0.1
            ),
        )

    if mood == "urgent":
        return PerformancePlan(
            mood=mood,
            speaking_rate=base_speed * 1.18,
            pitch_multiplier=base_pitch * 1.03,
            energy_multiplier=base_energy * 1.2,
            pauses=[0.01],
            emphasis_tokens=["now"],
            voice_dna=VoiceDNA(
                warmth=0.55, curiosity=0.4, confidence=0.95, energy=0.9, humor=0.05
            ),
        )

    return PerformancePlan(
        mood=mood,
        speaking_rate=base_speed,
        pitch_multiplier=base_pitch,
        energy_multiplier=base_energy,
        pauses=[0.02],
        emphasis_tokens=[],
        voice_dna=VoiceDNA(),
    )
