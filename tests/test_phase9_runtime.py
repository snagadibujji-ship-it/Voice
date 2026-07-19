from axima_voice import AximaVoice


def test_phase9_runtime_controls_and_audio():
    voice = AximaVoice()
    result = voice.synthesize(
        "Hello Gowtham, and welcome back because we are going live now"
    )

    phase9 = result["phase9_plan"]
    speech_audio = result["speech_audio"]

    assert phase9["runtime_control"]["voice_name"] == "Axima"
    assert phase9["runtime_profile"]["target_first_audio_ms"] == 160
    assert len(phase9["runtime_control"]["emotion_frames"]) >= 1
    assert len(phase9["runtime_control"]["presence_cues"]) >= 1
    assert len(speech_audio) > 1000
    assert max(abs(sample) for sample in speech_audio) > 0.0
