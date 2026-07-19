from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from .emotion_engine import EmotionEngine, EmotionState
from .playback_engine import PlaybackState
from .voice_identity import VoiceIdentityManager, VoiceProfile

SynthesizeCallable = Callable[[str], Dict[str, Any]]


@dataclass
class ConversationMemory:
    entities: List[str] = field(default_factory=list)
    names: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    current_topic: Optional[str] = None
    emotional_state: str = "neutral"
    unresolved_questions: List[str] = field(default_factory=list)
    hits: int = 0

    def remember(self, text: str) -> None:
        words = [word.strip(".,!?;:\"'()[]{}") for word in text.split()]
        for word in words:
            if len(word) > 1 and word[:1].isupper() and word not in self.names:
                self.names.append(word)
                self.entities.append(word)
        lowered = text.lower()
        if any(token in lowered for token in ["!", "great", "excited", "amazing"]):
            self.emotional_state = "excited"
        elif any(token in lowered for token in ["urgent", "now", "immediately"]):
            self.emotional_state = "urgent"
        elif any(token in lowered for token in ["quiet", "soft", "calm"]):
            self.emotional_state = "soft"
        content_words = [word.lower() for word in words if len(word) > 4]
        if content_words:
            self.current_topic = content_words[-1]
        if "?" in text:
            self.unresolved_questions.append(text)
        for marker in ["this", "that", "it", "they", "them"]:
            if marker in lowered.split() and marker not in self.references:
                self.references.append(marker)

    def context_prefix(self) -> str:
        fragments: List[str] = []
        if self.current_topic:
            fragments.append(f"Regarding {self.current_topic},")
        if self.names:
            self.hits += 1
            fragments.append(f"for {self.names[-1]},")
        return " ".join(fragments)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": self.entities,
            "names": self.names,
            "references": self.references,
            "current_topic": self.current_topic,
            "emotional_state": self.emotional_state,
            "unresolved_questions": self.unresolved_questions,
            "hits": self.hits,
        }


@dataclass
class SpeakingStyle:
    speed: float = 1.0
    energy: float = 1.0
    pause_scale: float = 1.0
    emphasis: float = 1.0
    emotional_tone: str = "neutral"

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class ConversationMetrics:
    conversation_start_ms: float = field(
        default_factory=lambda: perf_counter() * 1000.0
    )
    first_response_ms: Optional[float] = None
    interruption_count: int = 0
    interruption_recovery_times_ms: List[float] = field(default_factory=list)
    chunk_latencies_ms: List[float] = field(default_factory=list)
    response_update_count: int = 0
    memory_hits: int = 0
    conversation_duration_ms: Optional[float] = None

    @property
    def conversation_latency_ms(self) -> Optional[float]:
        if self.first_response_ms is None:
            return None
        return self.first_response_ms - self.conversation_start_ms

    @property
    def average_chunk_latency_ms(self) -> Optional[float]:
        if not self.chunk_latencies_ms:
            return None
        return sum(self.chunk_latencies_ms) / len(self.chunk_latencies_ms)

    def finish(self) -> None:
        self.conversation_duration_ms = (
            perf_counter() * 1000.0 - self.conversation_start_ms
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversation_latency_ms": self.conversation_latency_ms,
            "interruption_count": self.interruption_count,
            "interruption_recovery_time_ms": self.interruption_recovery_times_ms,
            "average_chunk_latency_ms": self.average_chunk_latency_ms,
            "response_update_count": self.response_update_count,
            "memory_hits": self.memory_hits,
            "conversation_duration_ms": self.conversation_duration_ms,
        }


@dataclass
class ConversationState:
    conversation_id: str = field(default_factory=lambda: str(uuid4()))
    active_speaker: str = "user"
    previous_utterance: str = ""
    current_utterance: str = ""
    pending_response: str = ""
    interruption_status: str = "none"
    created_at_ms: float = field(default_factory=lambda: perf_counter() * 1000.0)
    updated_at_ms: float = field(default_factory=lambda: perf_counter() * 1000.0)

    def touch(self) -> None:
        self.updated_at_ms = perf_counter() * 1000.0

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class ConversationTurnResult:
    text_delta: str
    response_text: str
    audio: List[float]
    playback_state: str
    updated: bool
    interrupted: bool
    metrics: Dict[str, Any]
    state: Dict[str, Any]
    memory: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


class ConversationManager:
    def __init__(
        self,
        synthesize: SynthesizeCallable,
        voice_identity_manager: VoiceIdentityManager | None = None,
        emotion_engine: EmotionEngine | None = None,
    ) -> None:
        self._synthesize = synthesize
        self.voice_identity_manager = voice_identity_manager
        self.emotion_engine = emotion_engine
        self.state = ConversationState()
        self.memory = ConversationMemory()
        self.style = SpeakingStyle()
        self.metrics = ConversationMetrics()
        self._completed_response = ""
        self._interruption_started_ms: Optional[float] = None

    def start_conversation(
        self, conversation_id: str | None = None
    ) -> ConversationState:
        self.state = ConversationState(conversation_id=conversation_id or str(uuid4()))
        self.memory = ConversationMemory()
        self.metrics = ConversationMetrics()
        self._completed_response = ""
        self._interruption_started_ms = None
        if self.emotion_engine is not None:
            self.emotion_engine.override("neutral", intensity=0.2)
        return self.state

    def set_emotion(self, emotion: str, *, override: bool = False) -> EmotionState:
        if self.emotion_engine is None:
            raise RuntimeError("ConversationManager has no EmotionEngine")
        state = (
            self.emotion_engine.override(emotion)
            if override
            else self.emotion_engine.transition(emotion)
        )
        self.memory.emotional_state = state.active_emotion
        self.state.touch()
        return state

    def switch_voice(self, voice_id: str) -> VoiceProfile:
        if self.voice_identity_manager is None:
            raise RuntimeError("ConversationManager has no VoiceIdentityManager")
        profile = self.voice_identity_manager.switch_voice(voice_id)
        self.state.touch()
        return profile

    def accept_partial_text(self, partial_text: str) -> ConversationTurnResult:
        previous = self.state.current_utterance
        common = self._common_prefix(previous, partial_text)
        updated = common != previous and bool(previous)
        delta = partial_text[len(common) :]
        self.state.previous_utterance = previous
        self.state.current_utterance = partial_text
        self.state.active_speaker = "assistant"
        self.state.touch()
        self.memory.remember(delta or partial_text)
        if self.emotion_engine is not None:
            emotion_state = self.emotion_engine.infer(
                delta or partial_text,
                conversation_memory=self.memory.to_dict(),
                voice_emotion_bias=(
                    self.voice_identity_manager.active_profile.emotion_bias
                    if self.voice_identity_manager is not None
                    else None
                ),
            )
            self.memory.emotional_state = emotion_state.active_emotion
        if self.style.emotional_tone != "neutral":
            self.memory.emotional_state = self.style.emotional_tone
        if updated:
            self.metrics.response_update_count += 1
            self._completed_response = self._completed_response[: len(common)]
        if not delta.strip():
            return self._empty_result(updated=updated)
        response_text = self._response_for_delta(delta)
        return self._emit_response(response_text, delta=delta, updated=updated)

    def append_response(self, text: str) -> ConversationTurnResult:
        self.metrics.response_update_count += 1
        response_text = f"{self.state.pending_response}{text}"
        return self._emit_response(response_text, delta=text, updated=True)

    def modify_unfinished_response(self, replacement: str) -> ConversationTurnResult:
        self.metrics.response_update_count += 1
        return self._emit_response(replacement, delta=replacement, updated=True)

    def cancel_unfinished_response(self) -> ConversationTurnResult:
        self.state.pending_response = ""
        self.state.interruption_status = "cancelled"
        self.metrics.response_update_count += 1
        self.state.touch()
        self.metrics.finish()
        return self._empty_result(updated=True, interrupted=True)

    def interrupt_user(self, priority: int = 1) -> ConversationTurnResult:
        self.metrics.interruption_count += 1
        self._interruption_started_ms = perf_counter() * 1000.0
        self.state.interruption_status = f"user:{priority}"
        self.state.active_speaker = "user"
        self.state.pending_response = ""
        self.state.touch()
        self.metrics.finish()
        return self._empty_result(updated=True, interrupted=True)

    def assistant_self_interrupt(
        self, reason: str = "self-correction"
    ) -> ConversationTurnResult:
        self.metrics.interruption_count += 1
        self._interruption_started_ms = perf_counter() * 1000.0
        self.state.interruption_status = f"assistant:{reason}"
        self.state.pending_response = ""
        self.state.touch()
        self.metrics.finish()
        return self._empty_result(updated=True, interrupted=True)

    def continue_response(self, text: str = "") -> ConversationTurnResult:
        if self._interruption_started_ms is not None:
            self.metrics.interruption_recovery_times_ms.append(
                perf_counter() * 1000.0 - self._interruption_started_ms
            )
            self._interruption_started_ms = None
        self.state.interruption_status = "continued"
        continuation = text or self.state.pending_response
        return self._emit_response(continuation, delta=continuation, updated=True)

    def adjust_speaking_style(
        self,
        *,
        speed: float | None = None,
        energy: float | None = None,
        pause_scale: float | None = None,
        emphasis: float | None = None,
        emotional_tone: str | None = None,
    ) -> SpeakingStyle:
        if speed is not None:
            self.style.speed = max(0.5, min(2.0, speed))
        if energy is not None:
            self.style.energy = max(0.2, min(2.0, energy))
        if pause_scale is not None:
            self.style.pause_scale = max(0.2, min(3.0, pause_scale))
        if emphasis is not None:
            self.style.emphasis = max(0.2, min(2.0, emphasis))
        if emotional_tone is not None:
            self.style.emotional_tone = emotional_tone
            self.memory.emotional_state = emotional_tone
        self.state.touch()
        return self.style

    def _emit_response(
        self, response_text: str, *, delta: str, updated: bool
    ) -> ConversationTurnResult:
        self.state.pending_response = response_text
        result = self._synthesize(response_text)
        raw_audio = result.get("playback_audio", result.get("audio", []))
        audio = self._apply_style(raw_audio if isinstance(raw_audio, list) else [])
        if self.metrics.first_response_ms is None and audio:
            self.metrics.first_response_ms = perf_counter() * 1000.0
        self.metrics.chunk_latencies_ms.extend(
            float(value)
            for value in result.get("streaming_metrics", {}).get(
                "chunk_generation_latency_ms", []
            )
        )
        self.metrics.memory_hits = self.memory.hits
        self._completed_response += response_text
        self.metrics.finish()
        return ConversationTurnResult(
            text_delta=delta,
            response_text=response_text,
            audio=audio,
            playback_state=str(
                result.get("playback_state", PlaybackState.FINISHED.value)
            ),
            updated=updated,
            interrupted=False,
            metrics=self._conversation_metrics(),
            state=self.state.to_dict(),
            memory=self.memory.to_dict(),
        )

    def _conversation_metrics(self) -> Dict[str, Any]:
        metrics = self.metrics.to_dict()
        if self.voice_identity_manager is not None:
            metrics.update(self.voice_identity_manager.metrics.to_dict())
        if self.emotion_engine is not None:
            metrics.update(self.emotion_engine.metrics.to_dict())
        return metrics

    def _response_for_delta(self, delta: str) -> str:
        prefix = self.memory.context_prefix()
        return f"{prefix} {delta}".strip()

    def _apply_style(self, audio: List[float]) -> List[float]:
        scaled = [sample * self.style.energy * self.style.emphasis for sample in audio]
        if self.style.speed > 1.05:
            step = int(round(self.style.speed))
            scaled = scaled[:: max(1, step)] or scaled[:1]
        elif self.style.speed < 0.95:
            repeated: List[float] = []
            repeat = max(1, int(round(1.0 / self.style.speed)))
            for sample in scaled:
                repeated.extend([sample] * repeat)
            scaled = repeated
        if self.style.pause_scale > 1.05:
            scaled.extend([0.0] * int(22050 * 0.01 * self.style.pause_scale))
        return scaled

    def _empty_result(
        self, updated: bool, interrupted: bool = False
    ) -> ConversationTurnResult:
        return ConversationTurnResult(
            text_delta="",
            response_text="",
            audio=[],
            playback_state=PlaybackState.INTERRUPTED.value
            if interrupted
            else PlaybackState.IDLE.value,
            updated=updated,
            interrupted=interrupted,
            metrics=self._conversation_metrics(),
            state=self.state.to_dict(),
            memory=self.memory.to_dict(),
        )

    def _common_prefix(self, left: str, right: str) -> str:
        index = 0
        limit = min(len(left), len(right))
        while index < limit and left[index] == right[index]:
            index += 1
        return left[:index]
