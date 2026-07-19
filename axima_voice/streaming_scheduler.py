from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .voice_director import VoiceDirector


@dataclass
class StreamingChunkPlan:
    index: int
    text: str
    priority: int
    estimated_tokens: int
    latency_budget_ms: int
    interrupt_priority: int

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class StreamingSchedule:
    chunks: List[StreamingChunkPlan] = field(default_factory=list)
    target_first_audio_ms: int = 220
    target_chunk_latency_ms: int = 120
    playback_priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "target_first_audio_ms": self.target_first_audio_ms,
            "target_chunk_latency_ms": self.target_chunk_latency_ms,
            "playback_priority": self.playback_priority,
        }


def _estimate_tokens(text: str) -> int:
    return max(1, len([t for t in text.split() if t]))


class StreamingScheduler:
    def __init__(self, director: VoiceDirector | None = None) -> None:
        self.director = director or VoiceDirector()

    def schedule(self, text: str) -> StreamingSchedule:
        tone = self.director.tone_for_text(text)
        words = [w.strip(".,!?;:\"'()[]{}") for w in text.split() if w.strip()]
        if not words:
            return StreamingSchedule(
                chunks=[
                    StreamingChunkPlan(
                        index=0,
                        text="",
                        priority=0,
                        estimated_tokens=1,
                        latency_budget_ms=100,
                        interrupt_priority=0,
                    )
                ]
            )

        chunks: List[StreamingChunkPlan] = []
        cursor = 0
        while cursor < len(words):
            remaining = len(words) - cursor
            chunk_size = 2 if remaining >= 6 else 1 if remaining <= 2 else 2
            chunk_words = words[cursor : cursor + chunk_size]
            chunk_text = " ".join(chunk_words)
            priority = 2 if cursor == 0 else 1
            if tone["urgency"] > 0.75:
                priority += 1
            if tone["hesitation"] > 0.2:
                priority -= 1
            chunks.append(
                StreamingChunkPlan(
                    index=len(chunks),
                    text=chunk_text,
                    priority=max(0, priority),
                    estimated_tokens=_estimate_tokens(chunk_text),
                    latency_budget_ms=90 if cursor == 0 else 120,
                    interrupt_priority=3 if cursor == 0 else 2,
                )
            )
            cursor += chunk_size

        target_first_audio_ms = 180 if tone["urgency"] > 0.75 else 220
        target_chunk_latency_ms = 100 if tone["urgency"] > 0.75 else 120
        playback_priority = 2 if tone["excitement"] > 0.8 else 1
        chunks.sort(key=lambda c: (-c.priority, c.index))
        return StreamingSchedule(
            chunks=chunks,
            target_first_audio_ms=target_first_audio_ms,
            target_chunk_latency_ms=target_chunk_latency_ms,
            playback_priority=playback_priority,
        )
