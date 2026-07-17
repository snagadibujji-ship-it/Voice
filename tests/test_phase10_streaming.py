from axima_voice import AximaVoice
from axima_voice.runtime_engine import RuntimeExecutionController, RuntimeState
from axima_voice.state_recovery import RecoveryState, StateRecoveryEngine
from axima_voice.streaming_scheduler import StreamingScheduler
from axima_voice.voice_director import VoiceDirector


def test_phase10_stream_schedule_and_runtime_chunks():
    voice = AximaVoice()
    result = voice.synthesize("That's a great question because we are building a streaming voice engine now")

    assert len(result["stream_schedule"]["chunks"]) >= 1
    assert len(result["runtime_chunks"]) >= 1
    assert result["streaming_metrics"]["chunks_generated"] >= 1
    assert result["streaming_metrics"]["chunks_completed"] >= 1
    assert result["latency_report"]["first_audio_latency_ms"] is not None
    assert result["latency_report"]["total_generation_ms"] is not None


def test_phase10_scheduler_prioritizes_voice_director_tone():
    scheduler = StreamingScheduler(VoiceDirector())
    schedule = scheduler.schedule("This is urgent and we need to start now")
    assert len(schedule.chunks) >= 1
    assert schedule.target_first_audio_ms <= 220


def test_phase10_state_recovery_round_trip():
    engine = StateRecoveryEngine()
    saved = engine.save_state(RecoveryState(chunk_index=2, sentence_index=1, phoneme_index=7, emotion_state="excited", playback_state="PAUSED", runtime_state="PAUSED"))
    restored = engine.restore_state(saved)
    assert restored.chunk_index == 2
    assert restored.emotion_state == "excited"
    assert restored.runtime_state == "PAUSED"


def test_phase10_runtime_controller_state_transitions():
    controller = RuntimeExecutionController()
    controller.begin_generation()
    controller.pause_generation()
    assert controller.state == RuntimeState.PAUSED
    controller.resume_generation()
    assert controller.state == RuntimeState.RESUMING
    controller.stop_generation("manual stop")
    assert controller.state == RuntimeState.INTERRUPTED
