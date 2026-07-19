from axima_voice import AximaVoice, EmotionEngine


def test_phase13_emotion_inference_persistence_and_metrics():
    engine = EmotionEngine()
    excited = engine.infer("I am so excited!")
    held = engine.infer("This continues")

    assert excited.active_emotion == "excited"
    assert held.active_emotion == "excited"
    assert engine.metrics.emotion_changes >= 1
    assert engine.metrics.emotion_prediction_latency_ms is not None
    assert engine.metrics.average_emotion_intensity is not None


def test_phase13_emotion_transition_blend_decay_and_override():
    engine = EmotionEngine()
    engine.start("happy")
    blended = engine.blend("calm", ratio=0.5)
    decayed = engine.decay(amount=0.2)
    override = engine.override("whisper")

    assert blended.active_emotion == "calm"
    assert decayed.intensity <= blended.intensity
    assert override.active_emotion == "whisper"
    assert engine.timeline.transitions
    assert engine.metrics.emotion_transition_time_ms


def test_phase13_pipeline_emotion_changes_speech_and_inserts_events():
    voice = AximaVoice()
    neutral = voice.synthesize("This is a simple statement")
    excited = voice.synthesize("I am so excited and glad!")

    assert neutral["emotion"]["state"]["active_emotion"] in {"neutral", "helpful"}
    assert excited["emotion"]["state"]["active_emotion"] == "excited"
    assert neutral["playback_audio"] != excited["playback_audio"]
    assert excited["emotion_metrics"]["laughter_inserted"] >= 1
    assert excited["emotion_metrics"]["breaths_inserted"] >= 1
    assert excited["emotion_metrics"]["average_emotion_intensity"] is not None


def test_phase13_hesitation_whisper_and_chunk_continuity():
    voice = AximaVoice()
    hesitant = voice.synthesize("I think maybe we should pause and consider this")
    whisper = voice.synthesize("Please whisper this quietly")

    assert hesitant["emotion_metrics"]["hesitations_inserted"] >= 1
    assert whisper["emotion"]["state"]["active_emotion"] == "whisper"
    assert whisper["playback_audio"]
    assert max(abs(sample) for sample in whisper["playback_audio"]) < max(
        abs(sample) for sample in hesitant["playback_audio"]
    )
    assert len(whisper["runtime_chunks"]) >= 1


def test_phase13_conversation_emotion_memory_and_voice_identity_compatibility():
    voice = AximaVoice()
    manager = voice.conversation_manager
    manager.start_conversation("emotion-conversation")
    first = manager.accept_partial_text("I am sorry about that")
    manager.switch_voice("energetic")
    second = manager.accept_partial_text("I am sorry about that but now I am excited!")

    assert first.memory["emotional_state"] == "empathetic"
    assert second.memory["emotional_state"] == "excited"
    assert second.metrics["emotion_changes"] >= 1
    assert second.metrics["voice_switch_count"] == 1
    assert second.audio


def test_phase13_streaming_compatibility_with_emotion_timeline():
    voice = AximaVoice()
    manager = voice.conversation_manager
    manager.start_conversation("stream-emotion")
    first = manager.accept_partial_text("I")
    second = manager.accept_partial_text("I am curious?")
    third = manager.accept_partial_text("I am curious? Tell me more")

    assert first.audio
    assert second.audio
    assert third.audio
    assert voice.emotion_engine.timeline.states
    assert third.metrics["emotion_prediction_latency_ms"] is not None
