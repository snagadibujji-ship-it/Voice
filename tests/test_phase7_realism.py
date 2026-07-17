from axima_voice import AximaVoice


def test_phase7_realism_plan_and_coarticulation():
    voice = AximaVoice()
    result = voice.synthesize("Hello Gowtham and welcome back to Axima")

    realism_plan = result["realism_plan"]

    assert realism_plan["identity"]["name"] == "Axima"
    assert len(realism_plan["phoneme_words"]) >= 1
    assert len(realism_plan["prosody_curve"]["pitch_points"]) >= 1
    assert realism_plan["emotion_plan"]["emotion"] in {"neutral", "excited", "soft", "urgent"}
    assert len(result["coarticulated_phonemes"]) >= len(result["phonemes"])
