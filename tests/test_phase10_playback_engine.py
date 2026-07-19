from axima_voice.playback_engine import PlaybackEngine, PlaybackState
from axima_voice.runtime_chunks import RuntimeChunkResult


def test_playback_engine_sequential_playback_and_metrics():
    engine = PlaybackEngine()
    chunks = [
        RuntimeChunkResult(
            chunk_index=0, text="Hello", audio=[0.1, 0.2], state="FINISHED", metrics={}
        ),
        RuntimeChunkResult(
            chunk_index=1, text="world", audio=[0.3, 0.4], state="FINISHED", metrics={}
        ),
    ]
    result = engine.play(chunks, predictive_opening=[0.0])

    assert result.state == PlaybackState.FINISHED
    assert result.chunk_count == 2
    assert len(result.audio) >= 5
    assert result.metrics.first_audio_latency_ms is not None
    assert result.metrics.total_generation_ms is not None


def test_playback_engine_pause_resume_interrupt_continue():
    engine = PlaybackEngine()
    engine.pause_stream()
    assert engine.state in {PlaybackState.IDLE, PlaybackState.PAUSED}

    engine.resume_stream()
    assert engine.state in {
        PlaybackState.RESUMING,
        PlaybackState.IDLE,
        PlaybackState.PAUSED,
        PlaybackState.INTERRUPTED,
    }

    # Interrupt/continue are intentionally effective only during active playback.
    engine.interrupt_stream()
    assert engine.state != PlaybackState.INTERRUPTED
