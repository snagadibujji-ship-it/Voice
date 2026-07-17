from __future__ import annotations

from typing import Iterable


def is_non_silent(audio: Iterable[float], threshold: float = 1e-5) -> bool:
    return any(abs(sample) > threshold for sample in audio)


def audio_stats(audio: Iterable[float]) -> dict:
    samples = list(audio)
    if not samples:
        return {"sample_count": 0, "peak": 0.0, "rms": 0.0}

    peak = max(abs(sample) for sample in samples)
    rms = (sum(sample * sample for sample in samples) / len(samples)) ** 0.5
    return {"sample_count": len(samples), "peak": peak, "rms": rms}
