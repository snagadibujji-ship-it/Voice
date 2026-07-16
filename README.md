# Axima Voice

Axima Voice is an experimental speech generation engine designed around **meaning-first synthesis** rather than traditional text-to-speech.

Instead of converting text directly into generic audio, Axima Voice explores a pipeline where speech is shaped by intent, emotion, rhythm, pause structure, and pronunciation planning.

## Core Idea

```text
Text → Normalize → Meaning → Prosody → Phonemes → Source → Filter → WAV
```

## Goals

- Build a lightweight voice engine from scratch
- Produce real spoken audio, not beeps or noise
- Expose a modular pipeline that can evolve over time
- Support future meaning-aware speech generation

## Current Phase

Phase 0: repo bootstrap

- README
- Python skeleton
- Pipeline interface
- First synthesis stub

## Proposed Package Layout

```text
axima_voice/
  __init__.py
  cli.py
  pipeline.py
  text_normalizer.py
  meaning_parser.py
  prosody.py
  phonemes.py
  source.py
  filter.py
  synth.py
  wav_io.py
```

## Next Milestones

1. Text normalization
2. Minimal grapheme-to-phoneme mapping
3. WAV generation
4. First understandable voice output
5. Prosody and emotion planning

## Vision

Axima Voice aims to become a voice system that sounds like it is speaking with thought, not just rendering words.
