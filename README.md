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

## Phase 3 Status: Closed ✅

Phase 3 added streaming conversation planning and chunked turn structure.

### Completed in Phase 3

- Streaming plan structure
- Conversation state tracking
- Chunk splitting for low-latency output
- Pipeline integration for streaming planning
- Streaming chunk tests

### What Phase 3 still leaves for later phases

- Wire real per-chunk audio generation
- Interruption-aware playback runtime
- Real first-audio latency measurements
- More advanced conversational turn control
- Streaming player / live audio engine

## Phase 4 Status: Closed ✅

Phase 4 added the live runtime planning layer for voice-mode behavior.

### Completed in Phase 4

- Live playback plan structure
- Playback chunk mapping
- Interruption-aware runtime state
- First-audio latency target planning
- Pipeline integration for live playback planning
- Runtime tests for playback chunk mapping

### What Phase 4 still leaves for later phases

- Real chunk-by-chunk audio playback engine
- Actual interruption handling at playback time
- Real latency measurement in execution
- More advanced live conversation control
- Music and singing branch

## Phase 5 Status: Closed ✅

Phase 5 added the music and composition branch.

### Completed in Phase 5

- Music DNA representation
- Composition plan structure
- Mood-to-music inference
- Chord, melody, and rhythm planning
- Pipeline integration for composition planning
- Music composition tests

### What Phase 5 still leaves for later phases

- Real music audio rendering
- Singing voice generation
- Instrumental track generation
- Rich harmonic progression control
- Unified speech-plus-music performance mode

## Phase 6 Status: Closed ✅

Phase 6 added the first real audio generation branch for music, singing prep, and speech-plus-music fusion.

### Completed in Phase 6

- Music renderer
- Singing plan structure
- Fusion plan structure
- Personality memory
- Pipeline integration for speech and music audio outputs
- Audio generation tests

### What Phase 6 still leaves for later phases

- Better music realism and arrangement
- Singing voice synthesis
- Instrumental track layering
- Rich harmony control
- Real speech-music blending at runtime

## Phase 7 Status: Closed ✅

Phase 7 added the realism engine for stronger speech naturalness.

### Completed in Phase 7

- Phoneme dictionary
- Grapheme-to-phoneme fallback engine
- Coarticulation planning
- Emotion rendering
- Prosody curves
- Voice identity model
- Pipeline integration for realism planning
- Realism tests

### What Phase 7 still leaves for later phases

- Higher-quality pronunciation modeling
- More detailed coarticulation rules
- Better emotion-to-audio rendering
- More refined prosody timing
- Real-time expressive playback using the realism layer

## Phase 8 Status: Closed ✅

Phase 8 made the realism layer actually affect waveform synthesis.

### Completed in Phase 8

- Audio control map
- Audio rendering profile
- Phase 8 plan structure
- Control-aware waveform synthesis
- Pipeline integration for audio control planning
- Audio control tests
- Real audio verification for expressive controls

### What Phase 8 still leaves for later phases

- Even smoother pitch and energy transitions
- More advanced coarticulation-driven rendering
- Better voice identity fine-tuning
- More natural emotional contouring
- Live expressive playback that reacts in real time

## Phase 9 Status: Closed ✅

Phase 9 added runtime execution behavior for interruption, pause, resume, and runtime metrics.

### Completed in Phase 9

- Runtime control plan
- Breath event planning
- Emotion frames across the sentence
- Presence cues and hesitation planning
- Interrupt state and live response bias
- Runtime execution controller
- Runtime state machine
- Latency tracking
- Pipeline exposure of runtime metrics and state
- Runtime execution tests

### What Phase 9 still leaves for later phases

- True live audio-device interruption
- Real streaming playback loop
- External latency measurement from a device/player
- More natural speech response under interruption
- Production-grade voice assistant turn-taking

## Phase 10 Status: In Progress 🔥

Phase 10 is building the streaming voice engine foundation.

### Completed in Phase 10 so far

- Voice director
- Streaming scheduler
- Runtime chunk engine
- State recovery engine
- Streaming metrics engine
- Pipeline integration for streaming execution structures
- Phase 10 execution tests

### Still remaining in Phase 10

- Real predictive speech emission before full response completion
- Live playback controller with true chunk-by-chunk streaming behavior
- Interruption during a live playback stream
- Resume from recovered stream chunk state
- Measure real chunk latency in execution paths

## Phase 10 Architecture

```text
Input
↓
Thought Stream
↓
Voice Director
↓
Streaming Scheduler
↓
Runtime Chunk Engine
↓
State Recovery Layer
↓
Playback Controller
↓
Metrics Engine
↓
Output
```

## Phase 10 Reality Split

### REAL

- scheduler execution structures
- runtime chunk execution structures
- state recovery round-trip
- runtime controller behavior
- streaming metrics output fields

### PARTIAL

- chunked generation
- interruption awareness
- resume behavior
- predictive speech readiness

### SIMULATED

- live playback device control
- full streaming voice mode
- true real-time interruption mid-playback

### UNSOLVED

- low-latency audio-device playback engine
- natural predictive speech in a live stream
- high-quality chunk boundary continuity under interruption
- production-grade turn-taking

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
  phase4.py
  phase5.py
  phase6.py
  phase7.py
  phase8.py
  phase9.py
  voice_director.py
  streaming_scheduler.py
  runtime_chunks.py
  state_recovery.py
  streaming_metrics.py
  runtime_engine.py
  source.py
  filter.py
  synth.py
  simple_synth.py
  voice_checks.py
  wav_io.py
```

## Next Phase Target

Phase 10 will keep pushing toward a real streaming runtime by improving predictive speech, live interruption handling, and stateful chunk playback.

## What is real

- speech waveform generation
- music waveform generation
- control-aware synthesis
- runtime execution controller
- latency tracking
- streaming execution scaffolding
- state recovery scaffolding
- testable audio output paths

## What is simulated

- true human breathing
- real interruption behavior in playback
- full emotional speech naturalness
- live turn-taking like a product-grade voice assistant
- device-level streaming playback

## What remains unsolved

- very high quality prosody
- voice cloning
- top-tier streaming naturalness
- singing-grade realism
- true live playback interruption engine

## Vision

Axima Voice aims to become a voice system that sounds like it is speaking with thought, not just rendering words.
