from axima_voice import AximaVoice
from axima_voice.playback_engine import PlaybackEngine, PlaybackState
from axima_voice.runtime_engine import RuntimeExecutionController, RuntimeState
from axima_voice.state_recovery import RecoveryState, StateRecoveryEngine
from axima_voice.streaming_scheduler import StreamingScheduler
from axima_voice.voice_director import VoiceDirector
from axima_voice.runtime_chunks import RuntimeChunkResult


def test_phase10_stream_schedule_and_runtime_chunks():
    voice = AximaVoice()
    result = voice.synthesize("That's a great question because we are building a streaming voice engine now")

    assert len(result["stream_schedule"]["chunks"]) >= 1
    assert len(result["runtime_chunks"]) >= 1
    assert result["streaming_metrics"]["chunks_generated"] >= 1
    assert result["streaming_metrics"]["chunks_completed"] >= 1
    assert result["latency_report"]["first_audio_latency_ms"] is not None
    assert result["latency_report"]["total_generation_ms"] is not None
    assert result["playback_state"] in {"BUFFERING", "PLAYING", "PAUSED", "INTERRUPTED", "RESUMING", "FINISHED"}
    assert result["playback_metrics"]["total_generation_ms"] is not None


def test_phase10_scheduler_prioritizes_voice_director_tone():
    scheduler = StreamingScheduler(VoiceDirector())
    schedule = scheduler.schedule("This is urgent and we need to start now")
    assert len(schedule.chunks) >= 1
    assert schedule.target_first_audio_ms <= 220


def test_phase10_state_recovery_round_trip():
    engine = StateRecoveryEngine()
    saved = engine.save_state(RecoveryState(chunk_index=2, sample_position=77, phoneme_position=7, emotion_state="excited", playback_state="PAUSED", runtime_state="PAUSED"))
    restored = engine.restore_state(saved)
    exact = engine.recover_exact_position(saved)
    assert restored.chunk_index == 2
    assert restored.sample_position == 77
    assert restored.emotion_state == "excited"
    assert restored.runtime_state == "PAUSED"
    assert exact.sample_position == 77


def test_phase10_runtime_controller_state_transitions():
    controller = RuntimeExecutionController()
    controller.begin_generation()
    controller.pause_generation()
    assert controller.state == RuntimeState.PAUSED
    controller.resume_generation()
    assert controller.state == RuntimeState.RESUMING
    controller.stop_generation("manual stop")
    assert controller.state == RuntimeState.INTERRUPTED


def test_phase10_playback_engine_and_continuation():
    engine = PlaybackEngine()
    chunks = [
        RuntimeChunkResult(chunk_index=0, text="Hello", audio=[0.1, 0.2], state="FINISHED", metrics={}),
        RuntimeChunkResult(chunk_index=1, text="world", audio=[0.3, 0.4], state="FINISHED", metrics={}),
    ]
    result = engine.play(chunks, predictive_opening=[0.0])
    assert result.state == PlaybackState.FINISHED
    assert result.chunk_count == 2
    assert len(result.audio) >= 5
    assert result.metrics.first_audio_latency_ms is not None
    assert result.metrics.total_generation_ms is not None

    engine.pause_stream()
    engine.resume_stream()
    engine.interrupt_stream()
    assert engine.state == PlaybackState.INTERRUPTED
    engine.continue_stream()
    assert engine.state == PlaybackState.PLAYING
