from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import perf_counter
from typing import Any, Dict, Iterable, List, Optional


class RuntimeState(str, Enum):
    IDLE = "IDLE"
    GENERATING = "GENERATING"
    PAUSED = "PAUSED"
    INTERRUPTED = "INTERRUPTED"
    RESUMING = "RESUMING"
    FINISHED = "FINISHED"


@dataclass
class RuntimeMetrics:
    generation_start_ms: Optional[float] = None
    first_audio_time_ms: Optional[float] = None
    completion_time_ms: Optional[float] = None

    def latency_report(self) -> Dict[str, Optional[float]]:
        first_audio_latency_ms = None
        total_generation_ms = None
        if (
            self.generation_start_ms is not None
            and self.first_audio_time_ms is not None
        ):
            first_audio_latency_ms = self.first_audio_time_ms - self.generation_start_ms
        if self.generation_start_ms is not None and self.completion_time_ms is not None:
            total_generation_ms = self.completion_time_ms - self.generation_start_ms
        return {
            "generation_start_ms": self.generation_start_ms,
            "first_audio_time_ms": self.first_audio_time_ms,
            "completion_time_ms": self.completion_time_ms,
            "first_audio_latency_ms": first_audio_latency_ms,
            "total_generation_ms": total_generation_ms,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {**self.__dict__.copy(), **self.latency_report()}


@dataclass
class RuntimeExecutionResult:
    audio: List[float]
    state: RuntimeState
    metrics: RuntimeMetrics
    interrupted: bool = False
    paused: bool = False
    resumed: bool = False
    stop_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audio": self.audio,
            "state": self.state.value,
            "metrics": self.metrics.to_dict(),
            "interrupted": self.interrupted,
            "paused": self.paused,
            "resumed": self.resumed,
            "stop_reason": self.stop_reason,
        }


@dataclass
class RuntimeExecutionController:
    state: RuntimeState = RuntimeState.IDLE
    interrupted: bool = False
    paused: bool = False
    resumed: bool = False
    stop_reason: Optional[str] = None
    metrics: RuntimeMetrics = field(default_factory=RuntimeMetrics)

    def stop_generation(self, reason: str = "interrupted") -> None:
        self.interrupted = True
        self.stop_reason = reason
        self.state = RuntimeState.INTERRUPTED

    def pause_generation(self) -> None:
        if self.state in {RuntimeState.GENERATING, RuntimeState.RESUMING}:
            self.paused = True
            self.state = RuntimeState.PAUSED

    def resume_generation(self) -> None:
        if self.state in {RuntimeState.PAUSED, RuntimeState.INTERRUPTED}:
            self.paused = False
            self.resumed = True
            self.state = RuntimeState.RESUMING

    def begin_generation(self) -> None:
        self.state = RuntimeState.GENERATING
        self.metrics.generation_start_ms = perf_counter() * 1000.0

    def mark_first_audio(self) -> None:
        if self.metrics.first_audio_time_ms is None:
            self.metrics.first_audio_time_ms = perf_counter() * 1000.0

    def finish_generation(self) -> None:
        self.metrics.completion_time_ms = perf_counter() * 1000.0
        if self.state not in {RuntimeState.INTERRUPTED, RuntimeState.PAUSED}:
            self.state = RuntimeState.FINISHED

    def latency_report(self) -> Dict[str, Optional[float]]:
        first_audio_latency_ms = None
        total_generation_ms = None
        if (
            self.metrics.generation_start_ms is not None
            and self.metrics.first_audio_time_ms is not None
        ):
            first_audio_latency_ms = (
                self.metrics.first_audio_time_ms - self.metrics.generation_start_ms
            )
        if (
            self.metrics.generation_start_ms is not None
            and self.metrics.completion_time_ms is not None
        ):
            total_generation_ms = (
                self.metrics.completion_time_ms - self.metrics.generation_start_ms
            )
        return {
            "generation_start_ms": self.metrics.generation_start_ms,
            "first_audio_time_ms": self.metrics.first_audio_time_ms,
            "completion_time_ms": self.metrics.completion_time_ms,
            "first_audio_latency_ms": first_audio_latency_ms,
            "total_generation_ms": total_generation_ms,
        }


def interleave_runtime_breathing(
    audio: Iterable[float], sentence_length: int, emotion: str
) -> List[float]:
    samples = list(audio)
    if not samples:
        return [0.0]

    # Runtime breathing behavior: insert tiny shaped pauses based on sentence size/emotion.
    base_pause = 0.0
    if sentence_length >= 10:
        base_pause += 0.014
    elif sentence_length >= 6:
        base_pause += 0.01

    if emotion == "excited":
        base_pause *= 0.6
    elif emotion == "soft":
        base_pause *= 1.5
    elif emotion == "urgent":
        base_pause *= 0.4

    pause_samples = int(22050 * base_pause)
    if pause_samples <= 0:
        return samples

    # Insert a mid-point micro-breath and a tail breath so the behavior changes audibly.
    mid = max(1, len(samples) // 2)
    return (
        samples[:mid]
        + ([0.0] * pause_samples)
        + samples[mid:]
        + ([0.0] * max(1, pause_samples // 2))
    )
