from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RecoveryState:
    chunk_index: int = 0
    sample_position: int = 0
    phoneme_position: int = 0
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
            sample_position=int(payload.get("sample_position", 0)),
            phoneme_position=int(payload.get("phoneme_position", 0)),
            emotion_state=str(payload.get("emotion_state", "neutral")),
            playback_state=str(payload.get("playback_state", "IDLE")),
            runtime_state=str(payload.get("runtime_state", "IDLE")),
        )

    def recover_exact_position(self, payload: Dict[str, Any]) -> RecoveryState:
        return self.restore_state(payload)
