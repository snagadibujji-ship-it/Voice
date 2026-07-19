from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .continuity_engine import ContinuityEngine
from .conversation_manager import ConversationManager
from .emotion_engine import EmotionEngine
from .meaning_parser import parse_meaning
from .performance_graph import build_performance_graph
from .phase2 import build_phase2_plan
from .phase3 import build_streaming_plan
from .phase4 import build_live_playback_plan
from .phase5 import build_composition_plan
from .phase6 import (
    MusicRenderer,
    build_fusion_plan,
    build_singing_plan,
    PersonalityMemory,
)
from .phase7 import apply_coarticulation, build_realism_plan
from .phase8 import build_phase8_plan
from .phase9 import build_phase9_plan
from .phonemes import text_to_phonemes
from .playback_engine import PlaybackEngine
from .prosody import plan_prosody
from .runtime_chunks import RuntimeChunkEngine, RuntimeChunkResult
from .runtime_engine import RuntimeExecutionController, RuntimeExecutionResult
from .simple_synth import SimpleSynthesizer
from .state_recovery import RecoveryState, StateRecoveryEngine
from .streaming_metrics import StreamingMetricsEngine
from .streaming_scheduler import StreamingScheduler
from .text_normalizer import normalize_text
from .voice_director import VoiceDirector
from .voice_identity import VoiceIdentityManager


@dataclass
class AximaVoice:
    """High-level orchestration layer for Axima Voice."""

    synthesizer: SimpleSynthesizer = field(default_factory=SimpleSynthesizer)
    music_renderer: MusicRenderer = field(default_factory=MusicRenderer)
    personality_memory: PersonalityMemory = field(default_factory=PersonalityMemory)
    voice_director: VoiceDirector = field(default_factory=VoiceDirector)
    voice_identity_manager: VoiceIdentityManager = field(
        default_factory=VoiceIdentityManager
    )
    emotion_engine: EmotionEngine = field(default_factory=EmotionEngine)
    streaming_scheduler: StreamingScheduler = field(init=False)
    runtime_chunk_engine: RuntimeChunkEngine = field(init=False)
    playback_engine: PlaybackEngine = field(default_factory=PlaybackEngine)
    continuity_engine: ContinuityEngine = field(default_factory=ContinuityEngine)
    recovery_engine: StateRecoveryEngine = field(default_factory=StateRecoveryEngine)
    metrics_engine: StreamingMetricsEngine = field(
        default_factory=StreamingMetricsEngine
    )
    conversation_manager: ConversationManager = field(init=False)

    def __post_init__(self) -> None:
        self.streaming_scheduler = StreamingScheduler(self.voice_director)
        self.runtime_chunk_engine = RuntimeChunkEngine(
            self.synthesizer, self.voice_director
        )
        self.conversation_manager = ConversationManager(
            self.synthesize, self.voice_identity_manager, self.emotion_engine
        )

    def synthesize(self, text: str) -> Dict[str, Any]:
        normalized = normalize_text(text)
        meaning = parse_meaning(normalized)
        prosody = plan_prosody(meaning)
        realism_plan = build_realism_plan(normalized, meaning)
        phase8_plan = build_phase8_plan(realism_plan)
        phase9_plan = build_phase9_plan(normalized, phase8_plan, realism_plan)
        performance_plan = build_phase2_plan(normalized, meaning, prosody)
        composition_plan = build_composition_plan(
            normalized, meaning, performance_plan.to_dict()
        )
        fusion_plan = build_fusion_plan(normalized, composition_plan)
        singing_plan = build_singing_plan(normalized, composition_plan)
        phonemes = text_to_phonemes(normalized, prosody=prosody)
        performance_graph = build_performance_graph(normalized, meaning, prosody)
        streaming_plan = build_streaming_plan(
            normalized, meaning, performance_plan.to_dict()
        )
        schedule = self.streaming_scheduler.schedule(normalized)
        active_voice_profile = self.voice_identity_manager.active_profile
        emotion_state = self.emotion_engine.infer(
            normalized, voice_emotion_bias=active_voice_profile.emotion_bias
        )
        active_emotion_profile = self.emotion_engine.active_profile
        vocal_events = self.emotion_engine.register_vocal_events(
            emotion_state.active_emotion, normalized
        )
        runtime_controller = RuntimeExecutionController()
        speech_result: RuntimeExecutionResult = self.synthesizer.synthesize(
            phonemes,
            performance_graph=performance_graph,
            phase8_plan=phase8_plan,
            phase9_plan=phase9_plan,
            runtime_controller=runtime_controller,
            voice_profile=active_voice_profile,
            emotion_profile=active_emotion_profile,
            vocal_events=vocal_events,
        )
        live_playback_plan = build_live_playback_plan(
            streaming_plan,
            len(speech_result.audio),
            sample_rate=self.synthesizer.sample_rate,
        )
        music_audio = self.music_renderer.render(composition_plan)
        coarticulated_phonemes = apply_coarticulation(realism_plan.phoneme_words)
        latency_report = speech_result.metrics.latency_report()
        metrics = self.metrics_engine.create()
        metrics.first_audio_latency_ms = latency_report.get("first_audio_latency_ms")
        metrics.total_generation_ms = latency_report.get("total_generation_ms")
        chunk_results: List[Dict[str, Any]] = []
        running_audio: List[float] = []
        chunk_controller = RuntimeExecutionController()
        continuity_state = self.continuity_engine.next_state(
            emotion_state.active_emotion
        )
        for chunk in schedule.chunks:
            chunk_result: RuntimeChunkResult = self.runtime_chunk_engine.render_chunk(
                chunk,
                phase8_plan=phase8_plan,
                phase9_plan=phase9_plan,
                controller=chunk_controller,
                prior_audio=running_audio,
                phonemes=phonemes,
                performance_graph=performance_graph,
                voice_profile=active_voice_profile,
                emotion_profile=active_emotion_profile,
                vocal_events=vocal_events,
            )
            blended_audio = self.continuity_engine.blend_chunk_audio(
                chunk_result.audio,
                continuity_state,
                emotion_state.active_emotion,
            )
            running_audio = blended_audio
            chunk_results.append({**chunk_result.to_dict(), "audio": blended_audio})
            continuity_state = self.continuity_engine.next_state(
                emotion_state.active_emotion,
                energy=1.0,
                pitch=1.0,
                pause=schedule.target_chunk_latency_ms / 1000.0,
            )
            recovery_state = RecoveryState(
                chunk_index=chunk.index,
                sample_position=len(blended_audio),
                phoneme_position=len(phonemes),
                emotion_state=emotion_state.active_emotion,
                playback_state=chunk_result.state,
                runtime_state=chunk_result.state,
            )
            saved_state = self.recovery_engine.save_state(recovery_state)
            _ = self.recovery_engine.recover_exact_position(saved_state)

        metrics.chunks_generated = len(chunk_results)
        metrics.chunks_completed = len(chunk_results)
        metrics.chunk_generation_latency_ms = [
            float(chunk["metrics"].get("total_generation_ms") or 0.0)
            for chunk in chunk_results
        ]
        metrics.chunk_latency_ms = list(metrics.chunk_generation_latency_ms)

        predictive_controller = RuntimeExecutionController()
        starter_tokens = (
            schedule.chunks[0].text.split()[:2] if schedule.chunks else [normalized]
        )
        predictive_result = self.synthesizer.synthesize(
            starter_tokens,
            performance_graph=performance_graph,
            phase8_plan=phase8_plan,
            phase9_plan=phase9_plan,
            runtime_controller=predictive_controller,
            voice_profile=active_voice_profile,
            emotion_profile=active_emotion_profile,
            vocal_events=vocal_events,
        )

        playback_result = self.playback_engine.play(
            chunk_results=[
                RuntimeChunkResult(
                    **{
                        k: v
                        for k, v in chunk.items()
                        if k
                        in {
                            "chunk_index",
                            "text",
                            "audio",
                            "state",
                            "metrics",
                            "interrupted",
                            "resumed",
                        }
                    }
                )
                for chunk in chunk_results
            ],
            predictive_opening=predictive_result.audio,
        )

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
            "playback_state": playback_result.state.value,
            "playback_metrics": playback_result.metrics.to_dict(),
            "playback_audio": playback_result.audio,
            "predictive_audio": predictive_result.audio,
            "live_playback_plan": live_playback_plan.to_dict(),
            "runtime_state": speech_result.state.value,
            "runtime_metrics": speech_result.metrics.to_dict(),
            "latency_report": latency_report,
            "emotion": self.emotion_engine.to_dict(),
            "emotion_metrics": self.emotion_engine.metrics.to_dict(),
            "voice_identity": active_voice_profile.to_dict(),
            "voice_identity_metrics": self.voice_identity_manager.metrics.to_dict(),
            "streaming_metrics": {
                **playback_result.metrics.to_dict(),
                **metrics.to_dict(),
                "chunk_playback_latency_ms": playback_result.metrics.chunk_playback_latency_ms,
                "stream_duration_ms": playback_result.metrics.stream_duration_ms,
            },
            "interrupted": speech_result.interrupted or playback_result.interrupted,
            "paused": speech_result.paused or playback_result.paused,
            "resumed": speech_result.resumed or playback_result.resumed,
            "stop_reason": speech_result.stop_reason,
            "phonemes": phonemes,
            "coarticulated_phonemes": coarticulated_phonemes,
            "performance_graph": performance_graph.to_dict(),
            "audio": speech_result.audio,
            "speech_audio": speech_result.audio,
            "music_audio": music_audio,
            "personality_memory": self.personality_memory.to_dict(),
        }
