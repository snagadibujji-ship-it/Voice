from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StreamingMetrics:
    first_audio_latency_ms: Optional[float] = None
    chunk_latency_ms: List[float] = field(default_factory=list)
    interrupt_latency_ms: Optional[float] = None
    resume_latency_ms: Optional[float] = None
    total_generation_ms: Optional[float] = None
    chunks_generated: int = 0
    chunks_completed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "first_audio_latency_ms": self.first_audio_latency_ms,
            "chunk_latency_ms": self.chunk_latency_ms,
            "interrupt_latency_ms": self.interrupt_latency_ms,
            "resume_latency_ms": self.resume_latency_ms,
            "total_generation_ms": self.total_generation_ms,
            "chunks_generated": self.chunks_generated,
            "chunks_completed": self.chunks_completed,
        }


class StreamingMetricsEngine:
    def create(self) -> StreamingMetrics:
        return StreamingMetrics()
