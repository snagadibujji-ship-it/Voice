from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class StreamChunk:
    index: int
    text: str
    audio_hint: str
    pause_after: float = 0.0


@dataclass
class ConversationState:
    turn_index: int = 0
    speaking_style: str = "neutral"
    interruption_supported: bool = True
    last_emotion: str = "neutral"
    memory_tags: List[str] = field(default_factory=list)


@dataclass
class StreamingPlan:
    state: ConversationState
    chunks: List[StreamChunk]
    first_audio_target_ms: int = 200

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": {
                "turn_index": self.state.turn_index,
                "speaking_style": self.state.speaking_style,
                "interruption_supported": self.state.interruption_supported,
                "last_emotion": self.state.last_emotion,
                "memory_tags": self.state.memory_tags,
            },
            "chunks": [chunk.__dict__ for chunk in self.chunks],
            "first_audio_target_ms": self.first_audio_target_ms,
        }


def split_for_streaming(text: str) -> List[str]:
    text = text.strip()
    if not text:
        return [""]

    separators = [",", ";", ":", "!", "?", "."]
    for sep in separators:
        text = text.replace(sep, f"{sep}|")
    parts = [part.strip() for part in text.split("|") if part.strip()]
    if len(parts) == 1 and len(parts[0].split()) > 8:
        words = parts[0].split()
        mid = max(1, len(words) // 2)
        return [" ".join(words[:mid]), " ".join(words[mid:])]
    return parts


def build_streaming_plan(
    text: str, meaning: Dict[str, Any], performance_plan: Dict[str, Any]
) -> StreamingPlan:
    parts = split_for_streaming(text)
    mood = performance_plan.get("mood", meaning.get("mood", "neutral"))
    state = ConversationState(
        turn_index=meaning.get("turn_index", 0),
        speaking_style=mood,
        interruption_supported=True,
        last_emotion=meaning.get("emotion", mood),
        memory_tags=[meaning.get("intent", "unknown")],
    )

    chunks: List[StreamChunk] = []
    for index, part in enumerate(parts):
        audio_hint = f"chunk-{index + 1}:{mood}"
        pause_after = 0.02 if index < len(parts) - 1 else 0.0
        chunks.append(
            StreamChunk(
                index=index, text=part, audio_hint=audio_hint, pause_after=pause_after
            )
        )

    return StreamingPlan(state=state, chunks=chunks)
