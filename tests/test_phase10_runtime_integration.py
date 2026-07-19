from axima_voice import AximaVoice
from axima_voice.continuity_engine import ContinuityEngine, ContinuityState
from axima_voice.playback_engine import PlaybackEngine, PlaybackState
from axima_voice.runtime_chunks import RuntimeChunkResult
from axima_voice.state_recovery import RecoveryState, StateRecoveryEngine


def test_phase10_end_to_end_real_execution_trace_and_metrics():
    result = AximaVoice().synthesize(
        "Urgent now we continue streaming voice chunks with exact runtime metrics"
    )

    assert result["playback_state"] == "FINISHED"
    assert [chunk["chunk_index"] for chunk in result["runtime_chunks"]] == list(
        range(len(result["runtime_chunks"]))
    )
    assert len(result["predictive_audio"]) > 1
    assert result["predictive_audio"] != [0.0]
    assert (
        result["playback_audio"][: len(result["predictive_audio"])]
        == result["predictive_audio"]
    )
    metrics = result["streaming_metrics"]
    assert metrics["first_audio_latency_ms"] is not None
    assert metrics["chunk_generation_latency_ms"]
    assert metrics["chunk_playback_latency_ms"]
    assert metrics["stream_duration_ms"] is not None


def test_phase10_playback_controls_during_active_playback():
    engine = PlaybackEngine()
    chunks = [
        RuntimeChunkResult(i, str(i), [0.1] * 8, "FINISHED", {}) for i in range(4)
    ]
    seen_states = []

    def controls(active_engine: PlaybackEngine, index: int) -> None:
        seen_states.append(active_engine.state)
        if index == 1:
            active_engine.pause_stream()
            assert active_engine.state == PlaybackState.PAUSED
            active_engine.resume_stream()
            assert active_engine.state == PlaybackState.RESUMING
            active_engine.continue_stream()
            assert active_engine.state == PlaybackState.PLAYING
        if index == 2:
            active_engine.interrupt_stream()

    result = engine.play(chunks, on_chunk_start=controls)
    assert PlaybackState.PLAYING in seen_states
    assert result.state == PlaybackState.INTERRUPTED
    assert result.interrupted
    assert result.metrics.interrupt_latency_ms is not None
    assert result.metrics.resume_latency_ms is not None
    assert result.metrics.chunks_completed == 2


def test_phase10_recovery_resumes_exact_position_into_playback():
    recovery = StateRecoveryEngine()
    chunks = [RuntimeChunkResult(0, "a", [0.1, 0.2], "FINISHED", {})]
    saved = recovery.save_state(
        RecoveryState(chunk_index=0, sample_position=1, playback_state="PAUSED")
    )
    exact = recovery.recover_exact_position(saved)
    resumed_audio = chunks[exact.chunk_index].audio[exact.sample_position :]
    result = PlaybackEngine().play(
        [RuntimeChunkResult(0, "a", resumed_audio, "FINISHED", {})]
    )
    assert result.audio == [0.2]
    assert result.state == PlaybackState.FINISHED


def test_phase10_continuity_modifies_energy_pitch_pause_and_emotion():
    engine = ContinuityEngine()
    original = [0.25, -0.25] * 80
    state = ContinuityState(
        carry_energy=1.2, carry_pitch=1.1, carry_pause=0.001, carry_emotion="soft"
    )
    changed = engine.blend_chunk_audio(original, state, "excited")
    assert changed != original
    assert changed[:20] == [0.0] * 20
    assert max(abs(sample) for sample in changed) != max(
        abs(sample) for sample in original
    )
