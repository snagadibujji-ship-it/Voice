"""Axima Voice package."""

__version__ = "0.1.0"

from .conversation_manager import ConversationManager as ConversationManager
from .emotion_engine import EmotionEngine as EmotionEngine
from .pipeline import AximaVoice as AximaVoice
from .voice_identity import VoiceIdentityManager as VoiceIdentityManager

__all__ = ["AximaVoice", "ConversationManager", "VoiceIdentityManager", "EmotionEngine"]
