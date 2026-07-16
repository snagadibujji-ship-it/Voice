from axima_voice import AximaVoice


def test_pipeline_smoke():
    voice = AximaVoice()
    result = voice.synthesize("hello")
    assert result["normalized_text"] == "hello"
    assert result["phonemes"]
