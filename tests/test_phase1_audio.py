from axima_voice import AximaVoice
from axima_voice.voice_checks import audio_stats, is_non_silent


def test_phase1_audio_is_non_silent():
    voice = AximaVoice()
    result = voice.synthesize("Hello Gowtham")
    audio = result["audio"]

    assert len(audio) > 1000
    assert is_non_silent(audio)

    stats = audio_stats(audio)
    assert stats["sample_count"] == len(audio)
    assert stats["peak"] > 0.0
    assert stats["rms"] > 0.0
