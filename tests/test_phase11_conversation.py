from axima_voice import AximaVoice
from axima_voice.conversation_manager import ConversationManager


def test_phase11_streaming_conversation_incremental_input_generates_deltas():
    voice = AximaVoice()
    manager = voice.conversation_manager
    state = manager.start_conversation("phase11")

    first = manager.accept_partial_text("I")
    second = manager.accept_partial_text("I think")
    third = manager.accept_partial_text("I think we should")

    assert state.conversation_id == "phase11"
    assert first.text_delta == "I"
    assert second.text_delta == " think"
    assert third.text_delta == " we should"
    assert len(first.audio) > 0
    assert len(second.audio) > 0
    assert len(third.audio) > 0
    assert third.state["current_utterance"] == "I think we should"
    assert third.metrics["conversation_latency_ms"] is not None
    assert third.metrics["average_chunk_latency_ms"] is not None
    assert third.metrics["conversation_duration_ms"] is not None


def test_phase11_response_update_cancel_and_regenerate_remaining_chunks():
    manager = ConversationManager(AximaVoice().synthesize)
    manager.start_conversation("updates")
    first = manager.accept_partial_text("I think we should turn left")
    modified = manager.accept_partial_text("I think we should turn right")
    cancelled = manager.cancel_unfinished_response()
    regenerated = manager.accept_partial_text("I think we should turn right now")

    assert first.audio
    assert modified.updated
    assert "right" in modified.response_text
    assert cancelled.interrupted
    assert regenerated.text_delta == " now"
    assert regenerated.metrics["response_update_count"] >= 2


def test_phase11_smart_interruption_and_recovery_continuation():
    manager = ConversationManager(AximaVoice().synthesize)
    manager.start_conversation("interrupt")
    manager.accept_partial_text("Axima will answer this request")
    interrupted = manager.interrupt_user(priority=5)
    continued = manager.continue_response(" with a graceful continuation")

    assert interrupted.interrupted
    assert interrupted.state["interruption_status"] == "user:5"
    assert continued.state["interruption_status"] != "user:5"
    assert continued.metrics["interruption_count"] == 1
    assert continued.metrics["interruption_recovery_time_ms"]
    assert continued.audio


def test_phase11_memory_retention_influences_future_response():
    manager = ConversationManager(AximaVoice().synthesize)
    manager.start_conversation("memory")
    manager.accept_partial_text("Gowtham is asking about latency")
    result = manager.accept_partial_text(
        "Gowtham is asking about latency and it matters"
    )

    assert "Gowtham" in result.memory["names"]
    assert result.memory["current_topic"] == "matters"
    assert result.metrics["memory_hits"] >= 1
    assert "Gowtham" in result.response_text


def test_phase11_dynamic_style_changes_audio_without_restart():
    manager = ConversationManager(AximaVoice().synthesize)
    manager.start_conversation("style")
    normal = manager.accept_partial_text("Speak calmly")
    manager.adjust_speaking_style(
        speed=1.8, energy=1.5, pause_scale=1.2, emphasis=1.2, emotional_tone="excited"
    )
    styled = manager.accept_partial_text("Speak calmly and faster now")

    assert styled.memory["emotional_state"] == "excited"
    assert styled.audio
    assert normal.audio != styled.audio
    assert max(abs(sample) for sample in styled.audio) > max(
        abs(sample) for sample in normal.audio
    )
