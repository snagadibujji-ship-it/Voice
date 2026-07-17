from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .phase9 import Phase9Plan
from .phase8 import Phase8Plan
from .runtime_engine import RuntimeExecutionController, RuntimeExecutionResult
from .simple_synth import SimpleSynthesizer
from .streaming_scheduler import StreamingSchedule, StreamingChunkPlan
from .voice_director import VoiceDirector


@dataclass
class RuntimeChunkResult:
    chunk_index: int
    text: str
    audio: List[float]
    state: str
    metrics: Dict[str, Any]
    interrupted: bool = False
    resumed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_index": self.chunk_index,
            "text": self.text,
            "audio": self.audio,
            "state": self.state,
            "metrics": self.metrics,
            "interrupted": self.interrupted,
            "resumed": self.resumed,
        }


@dataclass
class RuntimeChunkEngine:
    synthesizer: SimpleSynthesizer = field(default_factory=SimpleSynthesizer)
    director: VoiceDirector = field(default_factory=VoiceDirector)

    def render_chunk(
        self,
        chunk: StreamingChunkPlan,
        phase8_plan: Phase8Plan,
        phase9_plan: Phase9Plan,
        controller: RuntimeExecutionController | None = None,
        resume_from_state: RuntimeExecutionController | None = None,
        prior_audio: List[float] | None = None,
        phonemes: List[str] | None = None,
        performance_graph: Any | None = None,
    ) -> RuntimeChunkResult:
        runtime_controller = controller or RuntimeExecutionController()
        if resume_from_state is not None:
            runtime_controller.state = resume_from_state.state
            runtime_controller.metrics = resume_from_state.metrics
            if resume_from_state.interrupted:
                runtime_controller.resume_generation()
        tone = self.director.tone_for_text(chunk.text)
        if tone["excitement"] > 0.8 or tone["urgency"] > 0.75:
            runtime_controller.resume_generation()
        result: RuntimeExecutionResult = self.synthesizer.synthesize(
            phonemes or chunk.text.split(),
            performance_graph=performance_graph,
            phase8_plan=phase8_plan,
            phase9_plan=phase9_plan,
            runtime_controller=runtime_controller,
        )
        audio = (prior_audio or []) + result.audio
        return RuntimeChunkResult(
            chunk_index=chunk.index,
            text=chunk.text,
            audio=audio,
            state=result.state.value,
            metrics=result.metrics.latency_report(),
            interrupted=result.interrupted,
            resumed=result.resumed,
        )
