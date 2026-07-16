from __future__ import annotations

import wave
from array import array
from pathlib import Path
from typing import Iterable


def save_wav(path: str | Path, audio: Iterable[float], sample_rate: int = 22050) -> None:
    samples = array("h")
    for sample in audio:
        clipped = max(-1.0, min(1.0, float(sample)))
        samples.append(int(clipped * 32767))

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples.tobytes())
