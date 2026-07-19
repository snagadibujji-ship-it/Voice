from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List, Optional


@dataclass
class SpeakerEmbedding:
    vector: List[float]

    def cosine_similarity(self, other: "SpeakerEmbedding") -> float:
        dot = sum(a * b for a, b in zip(self.vector, other.vector))
        left = math.sqrt(sum(a * a for a in self.vector))
        right = math.sqrt(sum(b * b for b in other.vector))
        if left == 0.0 or right == 0.0:
            return 0.0
        return dot / (left * right)

    def to_dict(self) -> Dict[str, Any]:
        return {"vector": self.vector}

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "SpeakerEmbedding":
        return cls(vector=[float(value) for value in payload.get("vector", [])])


@dataclass
class VoiceProfile:
    voice_id: str
    display_name: str
    language: str = "en"
    accent: str = "neutral"
    speaking_rate: float = 1.0
    base_pitch: float = 145.0
    pitch_range: float = 1.0
    energy: float = 1.0
    pause_style: float = 1.0
    breathing_style: float = 1.0
    emotion_bias: str = "neutral"
    pronunciation_preferences: Dict[str, str] = field(default_factory=dict)
    sample_rate: int = 22050
    version: str = "1.0"
    gender: Optional[str] = None
    embedding: SpeakerEmbedding = field(
        default_factory=lambda: SpeakerEmbedding([1.0, 0.0, 0.0, 0.0])
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "voice_id": self.voice_id,
            "display_name": self.display_name,
            "gender": self.gender,
            "language": self.language,
            "accent": self.accent,
            "speaking_rate": self.speaking_rate,
            "base_pitch": self.base_pitch,
            "pitch_range": self.pitch_range,
            "energy": self.energy,
            "pause_style": self.pause_style,
            "breathing_style": self.breathing_style,
            "emotion_bias": self.emotion_bias,
            "pronunciation_preferences": self.pronunciation_preferences,
            "sample_rate": self.sample_rate,
            "version": self.version,
            "embedding": self.embedding.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "VoiceProfile":
        profile = cls(
            voice_id=str(payload["voice_id"]),
            display_name=str(payload.get("display_name", payload["voice_id"])),
            gender=payload.get("gender"),
            language=str(payload.get("language", "en")),
            accent=str(payload.get("accent", "neutral")),
            speaking_rate=float(payload.get("speaking_rate", 1.0)),
            base_pitch=float(payload.get("base_pitch", 145.0)),
            pitch_range=float(payload.get("pitch_range", 1.0)),
            energy=float(payload.get("energy", 1.0)),
            pause_style=float(payload.get("pause_style", 1.0)),
            breathing_style=float(payload.get("breathing_style", 1.0)),
            emotion_bias=str(payload.get("emotion_bias", "neutral")),
            pronunciation_preferences=dict(
                payload.get("pronunciation_preferences", {})
            ),
            sample_rate=int(payload.get("sample_rate", 22050)),
            version=str(payload.get("version", "1.0")),
            embedding=SpeakerEmbedding.from_dict(
                payload.get("embedding", {"vector": []})
            ),
        )
        if not profile.embedding.vector:
            profile.embedding = VoiceIdentityManager.embedding_for_profile(profile)
        return profile


@dataclass
class VoiceIdentityMetrics:
    voice_switch_count: int = 0
    voice_profile_load_time_ms: Optional[float] = None
    identity_similarity: Optional[float] = None
    identity_changes: List[str] = field(default_factory=list)
    profile_cache_hits: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "voice_switch_count": self.voice_switch_count,
            "voice_profile_load_time_ms": self.voice_profile_load_time_ms,
            "identity_similarity": self.identity_similarity,
            "identity_changes": self.identity_changes,
            "profile_cache_hits": self.profile_cache_hits,
        }


class VoiceIdentityManager:
    def __init__(self) -> None:
        self.profiles: Dict[str, VoiceProfile] = self._builtins()
        self.active_voice_id = "default"
        self.metrics = VoiceIdentityMetrics()

    @property
    def active_profile(self) -> VoiceProfile:
        return self.profiles[self.active_voice_id]

    def switch_voice(self, voice_id: str) -> VoiceProfile:
        start = perf_counter() * 1000.0
        if voice_id not in self.profiles:
            raise KeyError(f"Unknown voice profile: {voice_id}")
        previous = self.active_profile
        selected = self.profiles[voice_id]
        if voice_id == self.active_voice_id:
            self.metrics.profile_cache_hits += 1
        else:
            self.metrics.voice_switch_count += 1
            self.metrics.identity_changes.append(f"{self.active_voice_id}->{voice_id}")
        self.metrics.identity_similarity = previous.embedding.cosine_similarity(
            selected.embedding
        )
        self.active_voice_id = voice_id
        self.metrics.voice_profile_load_time_ms = perf_counter() * 1000.0 - start
        return selected

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.export(), indent=2, sort_keys=True))

    def load(self, path: str | Path) -> VoiceProfile:
        start = perf_counter() * 1000.0
        payload = json.loads(Path(path).read_text())
        profile = self.import_profile(
            payload["active_profile"] if "active_profile" in payload else payload
        )
        self.metrics.voice_profile_load_time_ms = perf_counter() * 1000.0 - start
        return profile

    def clone(
        self, source_voice_id: str, new_voice_id: str, display_name: str | None = None
    ) -> VoiceProfile:
        source = self.profiles[source_voice_id]
        payload = source.to_dict()
        payload["voice_id"] = new_voice_id
        payload["display_name"] = display_name or f"{source.display_name} Clone"
        clone = VoiceProfile.from_dict(payload)
        clone.embedding = self.embedding_for_profile(clone)
        self.profiles[new_voice_id] = clone
        return clone

    def export(self) -> Dict[str, Any]:
        return {
            "active_voice_id": self.active_voice_id,
            "active_profile": self.active_profile.to_dict(),
            "profiles": {
                voice_id: profile.to_dict()
                for voice_id, profile in self.profiles.items()
            },
            "metrics": self.metrics.to_dict(),
        }

    def import_profile(self, payload: Dict[str, Any]) -> VoiceProfile:
        profile = VoiceProfile.from_dict(payload)
        self.profiles[profile.voice_id] = profile
        self.active_voice_id = profile.voice_id
        return profile

    def compare(self, left_voice_id: str, right_voice_id: str) -> float:
        similarity = self.profiles[left_voice_id].embedding.cosine_similarity(
            self.profiles[right_voice_id].embedding
        )
        self.metrics.identity_similarity = similarity
        return similarity

    @staticmethod
    def embedding_for_profile(profile: VoiceProfile) -> SpeakerEmbedding:
        return SpeakerEmbedding(
            [
                profile.base_pitch / 300.0,
                profile.speaking_rate,
                profile.energy,
                profile.pitch_range,
                profile.pause_style,
                profile.breathing_style,
            ]
        )

    def _builtins(self) -> Dict[str, VoiceProfile]:
        profiles = {
            "default": VoiceProfile("default", "Default"),
            "soft": VoiceProfile(
                "soft",
                "Soft",
                speaking_rate=0.92,
                base_pitch=132.0,
                pitch_range=0.82,
                energy=0.76,
                pause_style=1.35,
                breathing_style=1.25,
                emotion_bias="soft",
            ),
            "energetic": VoiceProfile(
                "energetic",
                "Energetic",
                speaking_rate=1.18,
                base_pitch=168.0,
                pitch_range=1.28,
                energy=1.28,
                pause_style=0.72,
                breathing_style=0.82,
                emotion_bias="excited",
            ),
            "narrator": VoiceProfile(
                "narrator",
                "Narrator",
                speaking_rate=0.86,
                base_pitch=118.0,
                pitch_range=0.9,
                energy=1.05,
                pause_style=1.5,
                breathing_style=1.1,
                emotion_bias="neutral",
            ),
            "assistant": VoiceProfile(
                "assistant",
                "Assistant",
                speaking_rate=1.06,
                base_pitch=152.0,
                pitch_range=1.08,
                energy=1.04,
                pause_style=0.94,
                breathing_style=0.95,
                emotion_bias="helpful",
            ),
            "calm": VoiceProfile(
                "calm",
                "Calm",
                speaking_rate=0.88,
                base_pitch=126.0,
                pitch_range=0.74,
                energy=0.82,
                pause_style=1.65,
                breathing_style=1.4,
                emotion_bias="soft",
            ),
        }
        for profile in profiles.values():
            profile.embedding = self.embedding_for_profile(profile)
        return profiles
