from axima_voice import AximaVoice


def test_phase8_audio_control_map_exists():
    voice = AximaVoice()
    result = voice.synthesize("Hello Gowtham, make it sound more alive and expressive")

    phase8 = result["phase8_plan"]

    assert phase8["control_map"]["voice_name"] == "Axima"
    assert len(phase8["control_map"]["controls"]) >= 1
    assert phase8["rendering_profile"]["sample_rate"] == 22050
    assert "apply_pitch_to_rendering" in phase8["articulation_notes"]
