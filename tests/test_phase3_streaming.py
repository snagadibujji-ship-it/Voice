from axima_voice.phase2 import build_phase2_plan
from axima_voice.phase3 import build_streaming_plan, split_for_streaming


def test_split_for_streaming_long_text():
    parts = split_for_streaming(
        "This is a long sentence that should split into at least two chunks for streaming"
    )
    assert len(parts) >= 2


def test_streaming_plan_has_chunks():
    text = "Hello Gowtham, this is Axima speaking in chunks"
    meaning = {
        "intent": "greeting",
        "emotion": "friendly",
        "mood": "neutral",
        "turn_index": 1,
    }
    performance_plan = build_phase2_plan(
        text, meaning, {"speed": 1.0, "pitch": 1.0, "energy": 1.0, "pause_scale": 1.0}
    )
    plan = build_streaming_plan(text, meaning, performance_plan.to_dict())

    assert plan.first_audio_target_ms == 200
    assert len(plan.chunks) >= 1
    assert plan.state.interruption_supported is True
