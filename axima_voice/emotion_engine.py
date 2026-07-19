from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Dict, List, Optional


@dataclass
class EmotionProfile:
    name: str
    energy: float
    intensity: float
    pitch_bias: float
    speaking_rate: float
    pause_behavior: float
    breathing_frequency: float
    emphasis: float
    articulation: float
    sentence_ending_style: str
    transition_speed: float

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class EmotionState:
    active_emotion: str = "neutral"
    intensity: float = 0.0
    started_at_ms: float = field(default_factory=lambda: perf_counter() * 1000.0)
    updated_at_ms: float = field(default_factory=lambda: perf_counter() * 1000.0)

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class EmotionTransition:
    from_emotion: str
    to_emotion: str
    started_at_ms: float
    completed_at_ms: Optional[float] = None
    blend: float = 0.0
    override: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class EmotionTimeline:
    states: List[EmotionState] = field(default_factory=list)
    transitions: List[EmotionTransition] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "states": [state.to_dict() for state in self.states],
            "transitions": [transition.to_dict() for transition in self.transitions],
        }


@dataclass
class EmotionMetrics:
    emotion_changes: int = 0
    emotion_duration_ms: Dict[str, float] = field(default_factory=dict)
    emotion_transition_time_ms: List[float] = field(default_factory=list)
    breaths_inserted: int = 0
    hesitations_inserted: int = 0
    laughter_inserted: int = 0
    intensities: List[float] = field(default_factory=list)
    emotion_prediction_latency_ms: Optional[float] = None

    @property
    def average_emotion_intensity(self) -> Optional[float]:
        if not self.intensities:
            return None
        return sum(self.intensities) / len(self.intensities)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "emotion_changes": self.emotion_changes,
            "emotion_duration_ms": self.emotion_duration_ms,
            "emotion_transition_time_ms": self.emotion_transition_time_ms,
            "breaths_inserted": self.breaths_inserted,
            "hesitations_inserted": self.hesitations_inserted,
            "laughter_inserted": self.laughter_inserted,
            "average_emotion_intensity": self.average_emotion_intensity,
            "emotion_prediction_latency_ms": self.emotion_prediction_latency_ms,
        }


class EmotionEngine:
    def __init__(self) -> None:
        self.library = self._library()
        self.state = EmotionState()
        self.timeline = EmotionTimeline(states=[self.state])
        self.metrics = EmotionMetrics()

    @property
    def active_profile(self) -> EmotionProfile:
        return self.library[self.state.active_emotion]

    def start(self, emotion: str, intensity: float | None = None) -> EmotionState:
        return self.override(emotion, intensity=intensity)

    def hold(self) -> EmotionState:
        self.state.updated_at_ms = perf_counter() * 1000.0
        self.metrics.intensities.append(self.state.intensity)
        return self.state

    def decay(self, amount: float = 0.08) -> EmotionState:
        self.state.intensity = max(0.0, self.state.intensity - amount)
        if self.state.intensity <= 0.05 and self.state.active_emotion != "neutral":
            return self.transition("neutral")
        self.state.updated_at_ms = perf_counter() * 1000.0
        return self.state

    def blend(self, emotion: str, ratio: float = 0.5) -> EmotionState:
        target = self.library[emotion]
        current = self.active_profile
        blended_intensity = current.intensity * (1.0 - ratio) + target.intensity * ratio
        return self.transition(emotion, intensity=blended_intensity)

    def transition(self, emotion: str, intensity: float | None = None) -> EmotionState:
        if emotion not in self.library:
            emotion = "neutral"
        now = perf_counter() * 1000.0
        previous = self.state
        self._record_duration(previous, now)
        transition = EmotionTransition(previous.active_emotion, emotion, now)
        target = self.library[emotion]
        blend = min(1.0, max(0.0, target.transition_speed))
        transition.blend = blend
        new_intensity = intensity if intensity is not None else target.intensity
        if previous.active_emotion != emotion:
            self.metrics.emotion_changes += 1
            new_intensity = previous.intensity * (1.0 - blend) + new_intensity * blend
        transition.completed_at_ms = perf_counter() * 1000.0
        self.metrics.emotion_transition_time_ms.append(
            transition.completed_at_ms - transition.started_at_ms
        )
        self.timeline.transitions.append(transition)
        self.state = EmotionState(
            emotion,
            new_intensity,
            started_at_ms=now,
            updated_at_ms=transition.completed_at_ms,
        )
        self.timeline.states.append(self.state)
        self.metrics.intensities.append(self.state.intensity)
        return self.state

    def override(self, emotion: str, intensity: float | None = None) -> EmotionState:
        now = perf_counter() * 1000.0
        self._record_duration(self.state, now)
        target = self.library.get(emotion, self.library["neutral"])
        transition = EmotionTransition(
            self.state.active_emotion, target.name, now, override=True, blend=1.0
        )
        transition.completed_at_ms = perf_counter() * 1000.0
        self.timeline.transitions.append(transition)
        self.metrics.emotion_transition_time_ms.append(transition.completed_at_ms - now)
        if self.state.active_emotion != target.name:
            self.metrics.emotion_changes += 1
        self.state = EmotionState(
            target.name,
            intensity if intensity is not None else target.intensity,
            now,
            transition.completed_at_ms,
        )
        self.timeline.states.append(self.state)
        self.metrics.intensities.append(self.state.intensity)
        return self.state

    def infer(
        self,
        text: str,
        *,
        conversation_memory: Dict[str, Any] | None = None,
        voice_emotion_bias: str | None = None,
        override: bool = False,
    ) -> EmotionState:
        start = perf_counter() * 1000.0
        lowered = text.lower()
        emotion = (
            voice_emotion_bias
            if voice_emotion_bias in self.library
            else self.state.active_emotion
        )
        if any(token in lowered for token in ["excited", "amazing", "fantastic", "!"]):
            emotion = "excited"
        elif any(token in lowered for token in ["happy", "great", "glad"]):
            emotion = "happy"
        elif any(token in lowered for token in ["sorry", "apologize", "loss"]):
            emotion = "empathetic"
        elif any(token in lowered for token in ["why", "how", "what", "?"]):
            emotion = "curious"
        elif any(token in lowered for token in ["angry", "mad", "furious"]):
            emotion = "angry"
        elif any(token in lowered for token in ["scared", "afraid", "fear"]):
            emotion = "fearful"
        elif any(token in lowered for token in ["sad", "unhappy", "cry"]):
            emotion = "sad"
        elif any(token in lowered for token in ["whisper", "quietly", "hush"]):
            emotion = "whisper"
        elif any(token in lowered for token in ["calm", "steady", "relax"]):
            emotion = "calm"
        elif any(token in lowered for token in ["confident", "certain", "sure"]):
            emotion = "confident"
        elif any(token in lowered for token in ["surprise", "wow", "unexpected"]):
            emotion = "surprised"
        if (
            conversation_memory
            and conversation_memory.get("emotional_state") in self.library
            and emotion == self.state.active_emotion
        ):
            emotion = str(conversation_memory["emotional_state"])
        self.metrics.emotion_prediction_latency_ms = perf_counter() * 1000.0 - start
        if override:
            return self.override(emotion)
        if emotion == self.state.active_emotion:
            return self.hold()
        return self.transition(emotion)

    def register_vocal_events(self, emotion: str, text: str) -> Dict[str, int]:
        lowered = text.lower()
        profile = self.library.get(emotion, self.library["neutral"])
        breaths = (
            1 if profile.breathing_frequency > 1.05 or len(text.split()) > 8 else 0
        )
        hesitations = (
            1
            if any(token in lowered for token in ["um", "uh", "think", "maybe"])
            else 0
        )
        laughter = (
            1
            if emotion in {"happy", "excited"}
            and any(token in lowered for token in ["ha", "funny", "glad", "!"])
            else 0
        )
        self.metrics.breaths_inserted += breaths
        self.metrics.hesitations_inserted += hesitations
        self.metrics.laughter_inserted += laughter
        return {"breaths": breaths, "hesitations": hesitations, "laughter": laughter}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.to_dict(),
            "profile": self.active_profile.to_dict(),
            "timeline": self.timeline.to_dict(),
            "metrics": self.metrics.to_dict(),
        }

    def _record_duration(self, state: EmotionState, now: float) -> None:
        duration = max(0.0, now - state.started_at_ms)
        self.metrics.emotion_duration_ms[state.active_emotion] = (
            self.metrics.emotion_duration_ms.get(state.active_emotion, 0.0) + duration
        )

    def _library(self) -> Dict[str, EmotionProfile]:
        data = {
            "neutral": (1.0, 0.2, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, "level", 0.45),
            "happy": (1.12, 0.72, 0.06, 1.05, 0.9, 1.05, 1.12, 1.05, "lift", 0.55),
            "excited": (1.25, 0.9, 0.12, 1.12, 0.75, 1.15, 1.25, 1.1, "rise", 0.72),
            "calm": (0.86, 0.45, -0.04, 0.88, 1.35, 0.9, 0.85, 0.95, "soft-fall", 0.35),
            "confident": (1.1, 0.68, -0.01, 0.98, 0.95, 0.95, 1.18, 1.15, "firm", 0.5),
            "sad": (0.72, 0.62, -0.1, 0.82, 1.55, 1.2, 0.78, 0.82, "fall", 0.3),
            "angry": (
                1.32,
                0.86,
                0.04,
                1.08,
                0.72,
                1.35,
                1.35,
                1.25,
                "hard-stop",
                0.82,
            ),
            "fearful": (
                0.92,
                0.76,
                0.14,
                1.16,
                0.68,
                1.45,
                1.05,
                0.92,
                "tremble",
                0.75,
            ),
            "curious": (
                1.02,
                0.55,
                0.08,
                0.96,
                1.1,
                1.0,
                1.08,
                1.0,
                "question-rise",
                0.5,
            ),
            "surprised": (1.18, 0.78, 0.16, 1.1, 0.82, 1.25, 1.18, 1.0, "lift", 0.8),
            "empathetic": (
                0.82,
                0.58,
                -0.06,
                0.86,
                1.45,
                1.15,
                0.9,
                0.94,
                "gentle",
                0.4,
            ),
            "whisper": (0.55, 0.5, -0.16, 0.78, 1.25, 1.5, 0.62, 0.72, "fade", 0.6),
        }
        return {name: EmotionProfile(name, *values) for name, values in data.items()}
