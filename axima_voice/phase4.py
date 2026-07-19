from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .phase3 import StreamingPlan, StreamChunk


@dataclass
class PlaybackChunk:
    index: int
    text: str
    sample_start: int
    sample_end: int
    duration_ms: int


@dataclass
class LivePlaybackState:
    is_streaming: bool = True
    can_interrupt: bool = True
    emitted_chunks: int = 0
    current_turn_index: int = 0
    last_latency_ms: int = 0
    notes: List[str] = field(default_factory=list)


@dataclass
class LivePlaybackPlan:
    state: LivePlaybackState
    playback_chunks: List[PlaybackChunk]
    first_audio_target_ms: int = 180
    interruption_window_ms: int = 120

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": {
                "is_streaming": self.state.is_streaming,
                "can_interrupt": self.state.can_interrupt,
                "emitted_chunks": self.state.emitted_chunks,
                "current_turn_index": self.state.current_turn_index,
                "last_latency_ms": self.state.last_latency_ms,
                "notes": self.state.notes,
            },
            "playback_chunks": [chunk.__dict__ for chunk in self.playback_chunks],
            "first_audio_target_ms": self.first_audio_target_ms,
            "interruption_window_ms": self.interruption_window_ms,
        }


def build_live_playback_plan(
    streaming_plan: StreamingPlan, audio_length: int, sample_rate: int = 22050
) -> LivePlaybackPlan:
    chunks = streaming_plan.chunks
    if not chunks:
        chunks = [StreamChunk(index=0, text="", audio_hint="empty", pause_after=0.0)]

    samples_per_chunk = max(1, audio_length // len(chunks))
    playback_chunks: List[PlaybackChunk] = []
    cursor = 0
    for i, chunk in enumerate(chunks):
        start = cursor
        end = (
            audio_length
            if i == len(chunks) - 1
            else min(audio_length, cursor + samples_per_chunk)
        )
        cursor = end
        duration_ms = int(((end - start) / max(1, sample_rate)) * 1000)
        playback_chunks.append(
            PlaybackChunk(
                index=chunk.index,
                text=chunk.text,
                sample_start=start,
                sample_end=end,
                duration_ms=duration_ms,
            )
        )

    state = LivePlaybackState(
        is_streaming=True,
        can_interrupt=True,
        emitted_chunks=len(playback_chunks),
        current_turn_index=streaming_plan.state.turn_index,
        last_latency_ms=streaming_plan.first_audio_target_ms,
        notes=["phase4-live-runtime"],
    )

    return LivePlaybackPlan(
        state=state,
        playback_chunks=playback_chunks,
        first_audio_target_ms=180,
        interruption_window_ms=120,
    )
