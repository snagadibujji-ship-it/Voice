from axima_voice import AximaVoice
from axima_voice.runtime_engine import RuntimeExecutionController, RuntimeState


def test_phase9_runtime_metrics_and_state():
    voice = AximaVoice()
    result = voice.synthesize(
        "Hello Gowtham, because we are going live now and this should feel alive"
    )

    assert result["runtime_state"] in {"FINISHED", "INTERRUPTED", "PAUSED", "RESUMING"}
    assert result["latency_report"]["first_audio_latency_ms"] is not None
    assert result["latency_report"]["total_generation_ms"] is not None
    assert len(result["speech_audio"]) > 1000
    assert max(abs(sample) for sample in result["speech_audio"]) > 0.0


def test_phase9_runtime_controller_pause_resume_stop():
    controller = RuntimeExecutionController()
    controller.begin_generation()
    assert controller.state == RuntimeState.GENERATING

    controller.pause_generation()
    assert controller.state == RuntimeState.PAUSED

    controller.resume_generation()
    assert controller.state == RuntimeState.RESUMING
    assert controller.resumed is True

    controller.stop_generation("test interruption")
    assert controller.state == RuntimeState.INTERRUPTED
    assert controller.interrupted is True
    assert controller.stop_reason == "test interruption"
