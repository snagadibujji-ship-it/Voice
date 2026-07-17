from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .meaning_parser import parse_meaning
from .performance_graph import build_performance_graph
from .phase2 import build_phase2_plan
from .phase3 import build_streaming_plan
from .phase4 import build_live_playback_plan
from .phase5 import build_composition_plan
from .phase6 import MusicRenderer, build_fusion_plan, build_singing_plan, PersonalityMemory
from .phase7 import apply_coarticulation, build_realism_plan
from .phase8 import build_phase8_plan
from .phase9 import build_phase9_plan
from .phonemes import text_to_phonemes
from .prosody import plan_prosody
from .runtime_chunks import RuntimeChunkEngine, RuntimeChunkResult
from .runtime_engine import RuntimeExecutionController, RuntimeExecutionResult
from .simple_synth import SimpleSynthesizer
from .state_recovery import RecoveryState, StateRecoveryEngine
from .streaming_metrics import StreamingMetricsEngine
from .streaming_scheduler import StreamingScheduler
from .text_normalizer import normalize_text
from .voice_director import VoiceDirector


@dataclass
class AximaVoice:
    """High-level orchestration layer for Axima Voice."""

    synthesizer: SimpleSynthesizer = field(default_factory=SimpleSynthesizer)
    music_renderer: MusicRenderer = field(default_factory=MusicRenderer)
    personality_memory: PersonalityMemory = field(default_factory=PersonalityMemory)
    voice_director: VoiceDirector = field(default_factory=VoiceDirector)
    streaming_scheduler: StreamingScheduler = field(init=False)
    runtime_chunk_engine: RuntimeChunkEngine = field(init=False)
    recovery_engine: StateRecoveryEngine = field(default_factory=StateRecoveryEngine)
    metrics_engine: StreamingMetricsEngine = field(default_factory=StreamingMetricsEngine)

    def __post_init__(self) -> None:
        self.streaming_scheduler = StreamingScheduler(self.voice_director)
        self.runtime_chunk_engine = RuntimeChunkEngine(self.synthesizer, self.voice_director)

    def synthesize(self, text: str) -> Dict[str, Any]:
        normalized = normalize_text(text)
        meaning = parse_meaning(normalized)
        prosody = plan_prosody(meaning)
        realism_plan = build_realism_plan(normalized, meaning)
        phase8_plan = build_phase8_plan(realism_plan)
        phase9_plan = build_phase9_plan(normalized, phase8_plan, realism_plan)
        performance_plan = build_phase2_plan(normalized, meaning, prosody)
        composition_plan = build_composition_plan(normalized, meaning, performance_plan.to_dict())
        fusion_plan = build_fusion_plan(normalized, composition_plan)
        singing_plan = build_singing_plan(normalized, composition_plan)
        phonemes = text_to_phonemes(normalized, prosody=prosody)
        performance_graph = build_performance_graph(normalized, meaning, prosody)
        streaming_plan = build_streaming_plan(normalized, meaning, performance_plan.to_dict())
        schedule = self.streaming_scheduler.schedule(normalized)
        runtime_controller = RuntimeExecutionController()
        speech_result: RuntimeExecutionResult = self.synthesizer.synthesize(
            phonemes,
            performance_graph=performance_graph,
            phase8_plan=phase8_plan,
            phase9_plan=phase9_plan,
            runtime_controller=runtime_controller,
        )
        live_playback_plan = build_live_playback_plan(streaming_plan, len(speech_result.audio), sample_rate=self.synthesizer.sample_rate)
        music_audio = self.music_renderer.render(composition_plan)
        coarticulated_phonemes = apply_coarticulation(realism_plan.phoneme_words)
        latency_report = speech_result.metrics.latency_report()
        metrics = self.metrics_engine.create()
        metrics.first_audio_latency_ms = latency_report.get("first_audio_latency_ms")
        metrics.total_generation_ms = latency_report.get("total_generation_ms")
        metrics.chunks_generated = len(schedule.chunks)
        metrics.chunks_completed = len(schedule.chunks)
        metrics.chunk_latency_ms = [schedule.target_chunk_latency_ms for _ in schedule.chunks]

        chunk_results: List[Dict[str, Any]] = []
        running_audio: List[float] = []
        chunk_controller = RuntimeExecutionController()
        for chunk in schedule.chunks:
            chunk_result: RuntimeChunkResult = self.runtime_chunk_engine.render_chunk(
                chunk,
                phase8_plan=phase8_plan,
                phase9_plan=phase9_plan,
                controller=chunk_controller,
                prior_audio=running_audio,
                phonemes=phonemes,
                performance_graph=performance_graph,
            )
            running_audio = chunk_result.audio
            chunk_results.append(chunk_result.to_dict())
            recovery_state = RecoveryState(
                chunk_index=chunk.index,
                sentence_index=0,
                phoneme_index=len(phonemes),
                emotion_state=phase9_plan.runtime_control.emotion,
                playback_state=chunk_result.state,
                runtime_state=chunk_result.state,
            )
            saved_state = self.recovery_engine.save_state(recovery_state)
            _ = self.recovery_engine.restore_state(saved_state)

        return {
            "text": text,
            "normalized_text": normalized,
            "meaning": meaning,
            "prosody": prosody,
            "realism_plan": realism_plan.to_dict(),
            "phase8_plan": phase8_plan.to_dict(),
            "phase9_plan": phase9_plan.to_dict(),
            "performance_plan": performance_plan.to_dict(),
            "composition_plan": composition_plan.to_dict(),
            "fusion_plan": fusion_plan.to_dict(),
            "singing_plan": singing_plan.to_dict(),
            "streaming_plan": streaming_plan.to_dict(),
            "stream_schedule": schedule.to_dict(),
            "runtime_chunks": chunk_results,
            "live_playback_plan": live_playback_plan.to_dict(),
            "runtime_state": speech_result.state.value,
            "runtime_metrics": speech_result.metrics.to_dict(),
            "latency_report": latency_report,
            "streaming_metrics": metrics.to_dict(),
            "interrupted": speech_result.interrupted,
            "paused": speech_result.paused,
            "resumed": speech_result.resumed,
            "stop_reason": speech_result.stop_reason,
            "phonemes": phonemes,
            "coarticulated_phonemes": coarticulated_phonemes,
            "performance_graph": performance_graph.to_dict(),
            "speech_audio": speech_result.audio,
            "music_audio": music_audio,
            "personality_memory": self.personality_memory.to_dict(),
        }
