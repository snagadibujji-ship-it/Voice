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

## Phase 10 Status: Closed ✅

Phase 10 finishes the streaming runtime foundation with verified execution rather than placeholder planning. The runtime now emits predictive starter audio, generates ordered chunks, applies continuity transforms to audio samples, plays chunks through a stateful playback engine, records execution-derived metrics, and supports recovery/control tests against active playback.

### Completed in Phase 10

- Voice director tone routing
- Streaming scheduler with ordered chunk plans
- Runtime chunk engine with per-chunk synthesis metrics
- Continuity engine that modifies energy, pitch, pause, and emotion at audio-sample level
- State recovery round-trip and exact-position resume path
- Playback engine that consumes chunks, tracks playback state, and finishes playback
- Active playback pause/resume/continue/interrupt behavior
- Predictive speech starter utterance emitted before the remaining chunks are played
- Runtime metrics sourced from measured execution timestamps
- End-to-end Phase 10 integration tests

### Known Limitations

- Playback is an in-process sample-buffer runtime, not an operating-system audio device driver.
- Interruption is proven during the active playback loop via runtime callbacks; external microphone/barge-in integration is outside Phase 10.
- Synthesis is lightweight procedural waveform generation, not production neural TTS.
- Build uses the repository-local PEP 517 backend so the project can build without downloading setuptools in restricted environments.

## Phase 10 Architecture

```text
Input
↓
Pipeline normalization / meaning / prosody
↓
Voice Director
↓
Streaming Scheduler
↓
Predictive starter synthesis
↓
Runtime Chunk Engine
↓
Continuity Engine
↓
State Recovery Layer
↓
Playback Engine
↓
Runtime Metrics
↓
Output sample buffer
```

## Phase 10 Reality Audit

### REAL

- `pipeline.py` orchestrates the runtime path and returns the execution artifacts.
- `runtime_engine.py` owns runtime states, timestamps, and latency reports.
- `playback_engine.py` consumes chunk audio, maintains state, tracks playback metrics, and handles active controls.
- `runtime_chunks.py` renders sequential chunk audio with measured generation metrics.
- `continuity_engine.py` changes output samples for energy, pitch, pause, and emotion continuity.
- `state_recovery.py` saves, restores, and recovers exact stream positions.
- `streaming_scheduler.py` creates ordered chunk plans from input text and voice tone.
- `streaming_metrics.py` stores measured first-audio, chunk-generation, chunk-playback, interrupt, resume, and stream-duration metrics.
- `voice_director.py` routes text tone into urgency, excitement, curiosity, confidence, focus, and hesitation signals.
- `simple_synth.py` produces real non-silent waveform samples and records generation timing.

### PARTIAL

- Real-time playback is modeled with an in-process playback loop rather than a hardware audio callback.
- Predictive speech is a real starter utterance but uses the existing procedural synthesizer rather than a dedicated neural predictor.

### SIMULATED

- Device-level output latency and microphone-driven barge-in remain outside the repository runtime.

### UNSOLVED

- Production-grade streaming naturalness, voice cloning, high-quality singing, and live audio-device integration remain unsolved by design and are not part of Phase 10 closure.

## Package Layout

```text
axima_voice/
  __init__.py
  _build_backend.py
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
  playback_engine.py
  continuity_engine.py
  source.py
  filter.py
  synth.py
  simple_synth.py
  voice_checks.py
  wav_io.py
```

## Vision

Axima Voice aims to become a voice system that sounds like it is speaking with thought, not just rendering words.

## Phase 11 Status: Closed ✅

Phase 11 extends the Phase 10 streaming runtime into a real-time conversational voice engine. It does not replace the Phase 10 playback/chunk/continuity path; it wraps that runtime with a `ConversationManager` that manages session lifecycle, incremental input, response updates, interruption ownership, adaptive memory, dynamic speaking style, and conversation metrics.

### Phase 11 Architecture

```text
User partial text
↓
ConversationManager
↓
ConversationState / ConversationMemory / SpeakingStyle
↓
Incremental delta detection
↓
AximaVoice Phase 10 synthesize runtime
↓
Predictive starter + runtime chunks + continuity + playback
↓
Conversation metrics
↓
Incremental spoken output
```

### Conversation Engine

- Conversation lifecycle is tracked by conversation ID, active speaker, previous/current utterance, pending response, interruption status, and timestamps.
- Incremental text streaming accepts partial text and synthesizes only the new delta instead of replaying completed audio.
- Response updates support appending, modifying unfinished text, cancellation, and regenerating remaining chunks.
- Smart interruption supports user interruption, assistant self-interruption, graceful cancellation, and continuation with recovery timing.
- Adaptive short-term memory tracks entities, names, references, current topic, emotional state, unresolved questions, and memory hits.
- Dynamic style updates adjust speed, energy, pauses, emphasis, and emotional tone for subsequent streaming output without restarting the conversation.

### Phase 11 Runtime Metrics

- conversation latency
- interruption count
- interruption recovery time
- average chunk latency
- response update count
- memory hits
- conversation duration

### Phase 11 Reality Audit

#### REAL

- `ConversationManager` executes against the Phase 10 `AximaVoice.synthesize()` runtime.
- Incremental streaming synthesizes deltas rather than restarting the full utterance.
- Response update, cancellation, interruption, continuation, memory, style adjustment, and metrics paths are covered by integration tests.
- Conversation metrics are derived from runtime timestamps and Phase 10 chunk latency outputs.

#### PARTIAL

- Conversation policy is deterministic and lightweight; it is not an LLM response planner.
- Dynamic speaking style is applied as runtime audio post-processing over Phase 10 output rather than a neural prosody model.

#### SIMULATED

- External microphone/VAD-driven interruption detection is represented by explicit runtime interruption calls.
- Multi-speaker diarization and live audio device callbacks are not implemented.

#### UNSOLVED

- Production-grade natural conversation intelligence, neural dialogue planning, real microphone barge-in, and hardware audio scheduling remain outside Phase 11.

## Phase 12 Status: Closed ✅

Phase 12 adds Neural Voice Identity as a lightweight, runtime-integrated identity layer. The implementation is intentionally not production voice cloning; it provides a stable public API for persistent voice profiles, speaker embeddings, runtime voice switching, identity-aware synthesis controls, and execution-derived identity metrics that future neural models can replace behind the same interface.

### Phase 12 Architecture

```text
Input / partial conversation text
↓
ConversationManager
↓
VoiceIdentityManager active profile
↓
Streaming Scheduler
↓
Runtime Chunk Engine
↓
Identity-aware SimpleSynthesizer
↓
Continuity Engine
↓
Playback Engine
↓
Output sample buffer + identity metrics
```

### Voice Identity Pipeline

- `VoiceIdentityManager` owns profile registration, active voice selection, profile save/load, clone, export, import, and identity comparison.
- `VoiceProfile` stores speaker identity and voice configuration: voice ID, display name, optional gender metadata, language, accent, speaking rate, base pitch, pitch range, energy, pause style, breathing style, emotion bias, pronunciation preferences, sample rate, version, and embedding.
- `SpeakerEmbedding` stores a lightweight vector and supports cosine similarity for identity comparison and selection.
- `AximaVoice` keeps one active identity manager and passes the active profile through full synthesis, chunk rendering, predictive starter generation, continuity, playback, and returned runtime artifacts.
- `ConversationManager` can switch voices during an active conversation without recreating the engine.

### Built-in Voice Profiles

- Default
- Soft
- Energetic
- Narrator
- Assistant
- Calm

Each profile uses different runtime configuration values for pitch, rate, range, energy, pauses, breathing, and emotion bias, producing measurably different waveform output.

### Phase 12 Runtime Metrics

- voice switch count
- voice profile load time
- identity similarity
- identity changes
- profile cache hits

### Phase 12 Reality Audit

#### REAL

- Voice profiles persist through save/load/export/import and can be cloned.
- Speaker embeddings support cosine similarity and profile comparison.
- Runtime synthesis changes when the active profile changes.
- Conversation sessions continue after voice switching.
- Identity metrics are populated from runtime switch/load/compare execution.

#### PARTIAL

- Identity-aware synthesis uses deterministic DSP/runtime controls, not a trained neural speaker encoder or vocoder.
- Pronunciation preferences are token-level substitutions intended as a stable future API hook.

#### SIMULATED

- Neural voice cloning is not implemented; embeddings are lightweight profile vectors.
- Gender is metadata only and does not imply acoustic modeling.

#### UNSOLVED

- Production speaker verification, neural timbre transfer, multilingual phoneme adaptation, and dataset-trained voice cloning remain outside Phase 12.

## Phase 13 Status: Closed ✅

Phase 13 adds an Emotion & Expressive Speech Engine on top of the Phase 10–12 runtime. It does not replace the streaming, conversation, or voice identity systems; it adds persistent conversation emotion, deterministic runtime emotion inference, emotion timelines, natural vocal event insertion, identity-compatible expressive synthesis, and execution-derived emotion metrics.

### Phase 13 Runtime Flow

```text
Input / partial conversation text
↓
ConversationManager
↓
Conversation memory
↓
EmotionEngine
↓
VoiceIdentityManager active profile
↓
Streaming Scheduler
↓
Runtime Chunk Engine
↓
Emotion-aware SimpleSynthesizer
↓
Continuity Engine
↓
Playback Engine
↓
Output sample buffer + emotion metrics
```

### Emotion Engine

- `EmotionEngine` owns the active emotional state for the conversation.
- `EmotionProfile` defines energy, intensity, pitch bias, speaking rate, pause behavior, breathing frequency, emphasis, articulation, sentence ending style, and transition speed.
- `EmotionTimeline` stores states and transitions so emotion survives chunk and conversation boundaries.
- `EmotionTransition` records start, completion, blend, and override behavior.
- `EmotionMetrics` records emotion changes, emotion duration, transition timing, breaths, hesitations, laughter, average intensity, and prediction latency.

### Emotion Library

Built-in emotions:

- neutral
- happy
- excited
- calm
- confident
- sad
- angry
- fearful
- curious
- surprised
- empathetic
- whisper

### Expressive Runtime Behavior

- Emotion inference uses punctuation, keywords, voice profile bias, and conversation memory.
- Emotion state persists across streaming calls and decays/transitions gradually unless explicitly overridden.
- Emotion modifies actual synthesized audio through pitch bias, energy, speaking rate, pause behavior, breathing frequency, emphasis, attack, and whisper attenuation.
- Natural vocal events are inserted by runtime logic: breathing, hesitation/thinking pause, and soft laughter.
- Conversation emotion memory and voice identity remain compatible during streaming and runtime voice switching.

### Phase 13 Runtime Metrics

- emotion changes
- emotion duration
- emotion transition time
- breaths inserted
- hesitations inserted
- laughter inserted
- average emotion intensity
- emotion prediction latency

### Phase 13 Reality Audit

#### REAL

- Emotion state, profiles, timeline, transitions, and metrics execute in runtime code.
- Emotion inference is deterministic and uses text cues, conversation memory, and voice identity bias.
- Emotion persists across streaming/conversation calls.
- Emotion changes measurable waveform output.
- Breathing, hesitation, laughter, and whisper behavior are inserted by synthesis runtime logic.
- Emotion metrics are populated from runtime execution.

#### PARTIAL

- Emotion modeling is deterministic DSP/prosody control, not a trained affective speech model.
- Vocal events are procedural insertions, not recorded human nonverbal audio.

#### SIMULATED

- No neural emotion classifier is used.
- No external sentiment model or LLM is used for emotion prediction.

#### UNSOLVED

- Production affective speech modeling, learned emotional timbre transfer, actor-quality nonverbal events, and multilingual emotion-specific pronunciation remain outside Phase 13.
