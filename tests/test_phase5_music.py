from axima_voice import AximaVoice


def test_phase5_composition_plan_exists():
    voice = AximaVoice()
    result = voice.synthesize("Create an epic futuristic music mood for Axima")

    composition_plan = result["composition_plan"]

    assert composition_plan["can_sing"] is True
    assert composition_plan["can_instrumentalize"] is True
    assert len(composition_plan["bars"]) >= 2
    assert composition_plan["music_dna"]["tempo"] > 0
