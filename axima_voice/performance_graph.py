from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PerformanceNode:
    token: str
    stress: float = 0.0
    pause_after: float = 0.0
    pitch: float = 1.0
    energy: float = 1.0


@dataclass
class PerformanceGraph:
    nodes: List[PerformanceNode] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [node.__dict__ for node in self.nodes],
            "metadata": self.metadata,
        }


def build_performance_graph(text: str, meaning: Dict[str, Any], prosody: Dict[str, Any]) -> PerformanceGraph:
    tokens = [t for t in text.split(" ") if t]
    mood = meaning.get("mood", "neutral")
    energy = float(prosody.get("energy", 1.0))
    pitch = float(prosody.get("pitch", 1.0))
    pause_scale = float(prosody.get("pause_scale", 1.0))

    nodes: List[PerformanceNode] = []
    for i, token in enumerate(tokens):
        stress = 0.15 if i == 0 else 0.05
        if token.endswith(("!", "?")):
            stress = 0.25
        nodes.append(
            PerformanceNode(
                token=token,
                stress=stress,
                pause_after=0.02 * pause_scale,
                pitch=pitch,
                energy=energy,
            )
        )

    return PerformanceGraph(
        nodes=nodes,
        metadata={"mood": mood, "token_count": len(tokens)},
    )
