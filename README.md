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

## Phase 0 Status: Closed ✅

Phase 0 delivered the project bootstrap and the first orchestration layer.

### Completed in Phase 0

- Repository initialization
- Python package skeleton
- CLI entrypoint
- Smoke test scaffold
- Text normalization
- Meaning parser stub
- Prosody planner stub
- Phoneme token planner
- Performance graph scaffold
- WAV output utility

### What Phase 0 was still missing before closure

- Real waveform synthesis
- Real speech playback path
- Pronunciation-quality phoneme mapping
- Streaming audio engine
- End-to-end audible demo

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
  performance_graph.py
  source.py
  filter.py
  synth.py
  wav_io.py
```

## Next Phase: Phase 1

Phase 1 will turn the scaffold into real audio output.

### Phase 1 target

- Build a minimal synthesis path
- Generate non-silent speech-like audio
- Add timing and waveform structure
- Produce the first understandable spoken demo

## Vision

Axima Voice aims to become a voice system that sounds like it is speaking with thought, not just rendering words.
