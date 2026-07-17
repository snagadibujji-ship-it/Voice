from axima_voice import AximaVoice


def test_phase4_live_playback_plan():
    voice = AximaVoice()
    result = voice.synthesize("Hello Gowtham, this is Axima in live voice mode")

    live_plan = result["live_playback_plan"]
    streaming_plan = result["streaming_plan"]

    assert live_plan["first_audio_target_ms"] == 180
    assert live_plan["interruption_window_ms"] == 120
    assert len(live_plan["playback_chunks"]) >= 1
    assert live_plan["state"]["can_interrupt"] is True
    assert streaming_plan["first_audio_target_ms"] == 200
