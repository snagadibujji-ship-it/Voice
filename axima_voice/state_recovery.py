from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class RecoveryState:
    chunk_index: int = 0
    sentence_index: int = 0
    phoneme_index: int = 0
    emotion_state: str = "neutral"
    playback_state: str = "IDLE"
    runtime_state: str = "IDLE"

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


class StateRecoveryEngine:
    def save_state(self, state: RecoveryState) -> Dict[str, Any]:
        return state.to_dict()

    def restore_state(self, payload: Dict[str, Any]) -> RecoveryState:
        return RecoveryState(
            chunk_index=int(payload.get("chunk_index", 0)),
            sentence_index=int(payload.get("sentence_index", 0)),
            phoneme_index=int(payload.get("phoneme_index", 0)),
            emotion_state=str(payload.get("emotion_state", "neutral")),
            playback_state=str(payload.get("playback_state", "IDLE")),
            runtime_state=str(payload.get("runtime_state", "IDLE")),
        )
