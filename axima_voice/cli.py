from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import AximaVoice
from .wav_io import save_wav


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="axima-voice")
    parser.add_argument("text", nargs="?", default="Hello from Axima Voice")
    parser.add_argument("--out", default="out.wav")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    voice = AximaVoice()
    result = voice.synthesize(args.text)
    audio = [0.0] * max(1, len(result["phonemes"]))
    save_wav(Path(args.out), audio)
    print(result)


if __name__ == "__main__":
    main()
