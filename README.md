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

## Phase 1 Status: Closed ✅

Phase 1 turned the scaffold into a working audio path.

### Completed in Phase 1

- Minimal waveform synthesizer
- Pipeline wired to audio samples
- CLI writes real WAV output
- Audio verification helpers
- Automated non-silent audio test
- First audible smoke test scaffold

### What Phase 1 still leaves for later phases

- More natural phoneme timing
- Better pronunciation modeling
- Streaming runtime
- Emotional performance control
- Voice identity tuning

## Phase 2 Status: Closed ✅

Phase 2 added expressive performance planning and voice identity controls.

### Completed in Phase 2

- Voice DNA representation
- Performance plan structure
- Mood inference from text and meaning
- Expressive speed, pitch, and energy planning
- Pause and emphasis planning
- Pipeline integration for performance planning

### What Phase 2 still leaves for later phases

- Better natural-language style control
- Streaming-first audio chunks
- Real emotion-conditioned speech rendering
- More advanced pronunciation and coarticulation
- Music and singing branch

## Phase 3 Status: In Progress 🔥

Phase 3 is focusing on streaming, interruption handling, and conversational timing.

### Completed in Phase 3 so far

- Streaming plan structure
- Conversation state tracking
- Chunk splitting for low-latency output

### Still remaining in Phase 3

- Wire streaming plan into pipeline
- Generate audio per chunk
- Support interruption-aware turn handling
- Add a real streaming demo command
- Add tests for chunking and first-audio latency

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
  phase2.py
  phase3.py
  source.py
  filter.py
  synth.py
  simple_synth.py
  voice_checks.py
  wav_io.py
```

## Next Phase Target

Phase 3 will make Axima feel more alive in real conversation by focusing on streaming, interruption handling, and conversational timing.

## Vision

Axima Voice aims to become a voice system that sounds like it is speaking with thought, not just rendering words.
