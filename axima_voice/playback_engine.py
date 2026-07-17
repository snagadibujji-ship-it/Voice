from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import perf_counter
from typing import Any, Dict, List, Optional

from .runtime_chunks import RuntimeChunkResult
from .runtime_engine import RuntimeState
from .streaming_metrics import StreamingMetrics


class PlaybackState(str, Enum):
    IDLE = "IDLE"
    BUFFERING = "BUFFERING"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    INTERRUPTED = "INTERRUPTED"
    RESUMING = "RESUMING"
    FINISHED = "FINISHED"


@dataclass
class PlaybackExecutionResult:
    audio: List[float]
    state: PlaybackState
    metrics: StreamingMetrics
    interrupted: bool = False
    paused: bool = False
    resumed: bool = False
    chunk_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audio": self.audio,
            "state": self.state.value,
            "metrics": self.metrics.to_dict(),
            "interrupted": self.interrupted,
            "paused": self.paused,
            "resumed": self.resumed,
            "chunk_count": self.chunk_count,
        }


@dataclass
class PlaybackEngine:
    state: PlaybackState = PlaybackState.IDLE
    interrupted: bool = False
    paused: bool = False
    resumed: bool = False
    current_chunk_index: int = 0
    metrics: StreamingMetrics = field(default_factory=StreamingMetrics)
    _start_ms: Optional[float] = None
    _last_chunk_ms: Optional[float] = None

    def interrupt_stream(self) -> None:
        self.interrupted = True
        self.state = PlaybackState.INTERRUPTED

    def pause_stream(self) -> None:
        if self.state in {PlaybackState.PLAYING, PlaybackState.RESUMING, PlaybackState.BUFFERING}:
            self.paused = True
            self.state = PlaybackState.PAUSED

    def resume_stream(self) -> None:
        if self.state in {PlaybackState.PAUSED, PlaybackState.INTERRUPTED}:
            self.paused = False
            self.resumed = True
            self.state = PlaybackState.RESUMING

    def continue_stream(self) -> None:
        if self.state in {PlaybackState.RESUMING, PlaybackState.PAUSED, PlaybackState.INTERRUPTED}:
            self.paused = False
            self.interrupted = False
            self.state = PlaybackState.PLAYING

    def play(self, chunk_results: List[RuntimeChunkResult], predictive_opening: List[float] | None = None) -> PlaybackExecutionResult:
        self.state = PlaybackState.BUFFERING
        self._start_ms = perf_counter() * 1000.0
        output: List[float] = list(predictive_opening or [])
        if output and self.metrics.first_audio_latency_ms is None:
            self.metrics.first_audio_latency_ms = 0.0
        self.state = PlaybackState.PLAYING

        for index, chunk in enumerate(chunk_results):
            self.current_chunk_index = index
            if self.interrupted:
                self.metrics.interrupt_latency_ms = self._elapsed_since_start()
                self.state = PlaybackState.INTERRUPTED
                break
            if self.paused:
                self.state = PlaybackState.PAUSED
                break
            chunk_start = perf_counter() * 1000.0
            if self.metrics.first_audio_latency_ms is None and chunk.audio:
                self.metrics.first_audio_latency_ms = chunk_start - (self._start_ms or chunk_start)
            output.extend(chunk.audio)
            self.metrics.chunk_latency_ms.append(perf_counter() * 1000.0 - chunk_start)
            self.metrics.chunks_completed += 1
            self.metrics.chunks_generated += 1
            self._last_chunk_ms = perf_counter() * 1000.0

        if not self.interrupted and not self.paused:
            self.state = PlaybackState.FINISHED
        self.metrics.total_generation_ms = self._elapsed_since_start()
        return PlaybackExecutionResult(
            audio=output,
            state=self.state,
            metrics=self.metrics,
            interrupted=self.interrupted,
            paused=self.paused,
            resumed=self.resumed,
            chunk_count=len(chunk_results),
        )

    def _elapsed_since_start(self) -> Optional[float]:
        if self._start_ms is None:
            return None
        return perf_counter() * 1000.0 - self._start_ms
