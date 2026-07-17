from axima_voice import AximaVoice


def test_phase6_generates_speech_and_music_audio():
    voice = AximaVoice()
    result = voice.synthesize("Create an epic music and speak with it")

    assert len(result["speech_audio"]) > 1000
    assert len(result["music_audio"]) > 1000
    assert result["personality_memory"]["favorite_voice"] == "axima"
    assert result["fusion_plan"]["overlay_mode"] in {"speech_with_soft_music", "speech_only"}
