from pathlib import Path

from axima_voice import AximaVoice, VoiceIdentityManager
from axima_voice.voice_identity import SpeakerEmbedding


def test_phase12_builtin_profiles_load_and_switch_with_metrics():
    manager = VoiceIdentityManager()
    assert {"default", "soft", "energetic", "narrator", "assistant", "calm"}.issubset(
        manager.profiles
    )

    default = manager.active_profile
    soft = manager.switch_voice("soft")

    assert default.voice_id == "default"
    assert soft.voice_id == "soft"
    assert manager.metrics.voice_switch_count == 1
    assert manager.metrics.voice_profile_load_time_ms is not None
    assert manager.metrics.identity_similarity is not None
    assert manager.metrics.identity_changes == ["default->soft"]


def test_phase12_profile_save_load_clone_export_import(tmp_path: Path):
    manager = VoiceIdentityManager()
    clone = manager.clone("assistant", "assistant_clone", "Assistant Clone")
    manager.switch_voice(clone.voice_id)
    path = tmp_path / "voice.json"

    manager.save(path)
    loaded_manager = VoiceIdentityManager()
    loaded = loaded_manager.load(path)
    exported = manager.export()["active_profile"]
    imported = loaded_manager.import_profile(exported)

    assert loaded.voice_id == "assistant_clone"
    assert imported.voice_id == "assistant_clone"
    assert loaded_manager.active_profile.display_name == "Assistant Clone"
    assert loaded_manager.metrics.voice_profile_load_time_ms is not None


def test_phase12_embedding_similarity_and_identity_selection():
    manager = VoiceIdentityManager()
    same = SpeakerEmbedding([1.0, 0.5, 0.25]).cosine_similarity(
        SpeakerEmbedding([1.0, 0.5, 0.25])
    )
    different = manager.compare("soft", "energetic")

    assert same == 1.0
    assert 0.0 < different < 1.0
    assert manager.metrics.identity_similarity == different


def test_phase12_synthesis_changes_when_voice_profile_changes():
    voice = AximaVoice()
    default_result = voice.synthesize("Identity aware speech should sound different")
    voice.voice_identity_manager.switch_voice("energetic")
    energetic_result = voice.synthesize("Identity aware speech should sound different")

    assert default_result["voice_identity"]["voice_id"] == "default"
    assert energetic_result["voice_identity"]["voice_id"] == "energetic"
    assert default_result["playback_audio"] != energetic_result["playback_audio"]
    assert energetic_result["voice_identity_metrics"]["voice_switch_count"] == 1
    assert (
        energetic_result["voice_identity_metrics"]["voice_profile_load_time_ms"]
        is not None
    )


def test_phase12_conversation_continues_after_voice_switch():
    voice = AximaVoice()
    manager = voice.conversation_manager
    manager.start_conversation("voice-switch")
    first = manager.accept_partial_text("I think the assistant should")
    profile = manager.switch_voice("soft")
    second = manager.accept_partial_text("I think the assistant should continue softly")

    assert profile.voice_id == "soft"
    assert first.audio
    assert second.audio
    assert second.text_delta == " continue softly"
    assert second.state["conversation_id"] == "voice-switch"
    assert second.metrics["voice_switch_count"] == 1
    assert second.metrics["voice_profile_load_time_ms"] is not None
