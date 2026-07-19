from axima_voice import AximaVoice


def test_phase8_real_audio_control_and_output():
    voice = AximaVoice()
    result = voice.synthesize(
        "Hello Gowtham, make the voice more alive and expressive now"
    )

    phase8 = result["phase8_plan"]
    speech_audio = result["speech_audio"]

    assert phase8["control_map"]["voice_name"] == "Axima"
    assert len(phase8["control_map"]["controls"]) >= 1
    assert len(speech_audio) > 1000
    assert max(abs(sample) for sample in speech_audio) > 0.0
    assert phase8["rendering_profile"]["sample_rate"] == 22050
