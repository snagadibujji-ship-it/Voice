from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class VoiceDirector:
    confidence: float = 0.75
    curiosity: float = 0.55
    excitement: float = 0.5
    urgency: float = 0.45
    focus: float = 0.7
    hesitation: float = 0.15

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()

    def tone_for_text(self, text: str) -> Dict[str, float]:
        lowered = text.lower()
        if any(
            token in lowered for token in ["!", "amazing", "epic", "great", "awesome"]
        ):
            return {
                "confidence": 0.82,
                "curiosity": 0.5,
                "excitement": 0.88,
                "urgency": 0.42,
                "focus": 0.68,
                "hesitation": 0.08,
            }
        if any(
            token in lowered for token in ["why", "how", "what", "question", "explain"]
        ):
            return {
                "confidence": 0.7,
                "curiosity": 0.88,
                "excitement": 0.42,
                "urgency": 0.28,
                "focus": 0.82,
                "hesitation": 0.18,
            }
        if any(token in lowered for token in ["urgent", "now", "fast", "immediately"]):
            return {
                "confidence": 0.8,
                "curiosity": 0.32,
                "excitement": 0.56,
                "urgency": 0.9,
                "focus": 0.88,
                "hesitation": 0.06,
            }
        return self.to_dict()
