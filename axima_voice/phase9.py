from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .phase7 import RealismPlan
from .phase8 import Phase8Plan


@dataclass
class BreathEvent:
    index: int
    after_token: str
    pause_seconds: float
    strength: float

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class EmotionFrame:
    index: int
    pitch_scale: float
    energy_scale: float
    duration_scale: float
    pause_scale: float

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class PresenceCue:
    index: int
    cue_type: str
    duration_seconds: float
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class InterruptState:
    can_interrupt: bool = True
    can_resume: bool = True
    stop_latency_ms: int = 80
    resume_latency_ms: int = 120
    restart_from_last_phrase: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class RuntimeControlPlan:
    voice_name: str
    emotion: str
    breath_events: List[BreathEvent] = field(default_factory=list)
    emotion_frames: List[EmotionFrame] = field(default_factory=list)
    presence_cues: List[PresenceCue] = field(default_factory=list)
    interrupt_state: InterruptState = field(default_factory=InterruptState)
    adaptive_turn_taking: bool = True
    live_response_bias: float = 0.88

    def to_dict(self) -> Dict[str, Any]:
        return {
            "voice_name": self.voice_name,
            "emotion": self.emotion,
            "breath_events": [event.to_dict() for event in self.breath_events],
            "emotion_frames": [frame.to_dict() for frame in self.emotion_frames],
            "presence_cues": [cue.to_dict() for cue in self.presence_cues],
            "interrupt_state": self.interrupt_state.to_dict(),
            "adaptive_turn_taking": self.adaptive_turn_taking,
            "live_response_bias": self.live_response_bias,
        }


@dataclass
class RuntimeProfile:
    target_first_audio_ms: int = 160
    expressive_latency_budget_ms: int = 240
    phrase_boundary_breath_ms: int = 140
    micro_pause_ms: int = 70
    smoothness_window: int = 4

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class Phase9Plan:
    phase8_plan: Phase8Plan
    runtime_control: RuntimeControlPlan
    runtime_profile: RuntimeProfile
    runtime_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase8_plan": self.phase8_plan.to_dict(),
            "runtime_control": self.runtime_control.to_dict(),
            "runtime_profile": self.runtime_profile.to_dict(),
            "runtime_notes": self.runtime_notes,
        }


def _emotion_from_text(text: str, realism_plan: RealismPlan) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ["!", "great", "awesome", "epic", "amazing", "now"]):
        return "excited"
    if any(token in lowered for token in ["sorry", "sad", "unfortunately", "missed"]):
        return "soft"
    if any(token in lowered for token in ["urgent", "quick", "fast"]):
        return "urgent"
    return realism_plan.emotion_plan.emotion


def build_breath_events(text: str, runtime_profile: RuntimeProfile) -> List[BreathEvent]:
    words = [w.strip(".,!?;:\"'()[]{}") for w in text.split() if w.strip()]
    events: List[BreathEvent] = []
    for index, word in enumerate(words):
        if index == 0:
            continue
        if word.lower() in {"and", "but", "so", "because", "then"} or len(word) > 9:
            events.append(
                BreathEvent(
                    index=index,
                    after_token=word,
                    pause_seconds=runtime_profile.phrase_boundary_breath_ms / 1000.0,
                    strength=0.75 if len(word) > 9 else 0.45,
                )
            )
    return events


def build_emotion_frames(text: str, emotion: str, control_map_controls: List[Dict[str, Any]]) -> List[EmotionFrame]:
    words = [w.strip(".,!?;:\"'()[]{}") for w in text.split() if w.strip()]
    frames: List[EmotionFrame] = []
    total = max(1, len(words))
    for index, _ in enumerate(words):
        ratio = index / max(1, total - 1) if total > 1 else 0.0
        if emotion == "excited":
            pitch = 1.08 + 0.05 * ratio
            energy = 1.12 + 0.04 * ratio
            duration = 0.95 - 0.03 * ratio
            pause = 0.85 - 0.08 * ratio
        elif emotion == "soft":
            pitch = 0.96 - 0.01 * ratio
            energy = 0.88 - 0.02 * ratio
            duration = 1.08 + 0.03 * ratio
            pause = 1.14 + 0.04 * ratio
        elif emotion == "urgent":
            pitch = 1.03 + 0.02 * ratio
            energy = 1.18 + 0.05 * ratio
            duration = 0.92 - 0.04 * ratio
            pause = 0.82 - 0.05 * ratio
        else:
            pitch = 1.0 + 0.01 * (0.5 - ratio)
            energy = 1.0 + 0.01 * (0.5 - ratio)
            duration = 1.0
            pause = 1.0

        if index < len(control_map_controls):
            control = control_map_controls[index]
            pitch *= float(control.get("pitch_scale", 1.0))
            energy *= float(control.get("energy_scale", 1.0))
            duration *= float(control.get("duration_scale", 1.0))
            pause *= max(0.8, float(control.get("pause_after", 0.0)) * 20.0 + 0.8)

        frames.append(
            EmotionFrame(
                index=index,
                pitch_scale=pitch,
                energy_scale=energy,
                duration_scale=duration,
                pause_scale=pause,
            )
        )
    return frames


def build_presence_cues(text: str, emotion: str, runtime_profile: RuntimeProfile) -> List[PresenceCue]:
    words = [w.strip(".,!?;:\"'()[]{}") for w in text.split() if w.strip()]
    cues: List[PresenceCue] = []
    for index, word in enumerate(words):
        if index == 0 and len(words) > 2:
            cues.append(PresenceCue(index=index, cue_type="thinking_start", duration_seconds=runtime_profile.micro_pause_ms / 1000.0))
        if word.lower() in {"hmm", "well", "let", "think"}:
            cues.append(PresenceCue(index=index, cue_type="hesitation", duration_seconds=0.08))
        if emotion in {"excited", "urgent"} and index == len(words) - 2:
            cues.append(PresenceCue(index=index, cue_type="anticipation", duration_seconds=0.05))
    return cues


def build_runtime_control_plan(text: str, phase8_plan: Phase8Plan, realism_plan: RealismPlan) -> RuntimeControlPlan:
    emotion = _emotion_from_text(text, realism_plan)
    runtime_profile = RuntimeProfile()
    breath_events = build_breath_events(text, runtime_profile)
    control_dicts = phase8_plan.control_map.to_dict().get("controls", [])
    emotion_frames = build_emotion_frames(text, emotion, control_dicts)
    presence_cues = build_presence_cues(text, emotion, runtime_profile)
    return RuntimeControlPlan(
        voice_name=phase8_plan.control_map.voice_name,
        emotion=emotion,
        breath_events=breath_events,
        emotion_frames=emotion_frames,
        presence_cues=presence_cues,
        interrupt_state=InterruptState(),
        adaptive_turn_taking=True,
        live_response_bias=0.9 if emotion in {"excited", "urgent"} else 0.86,
    )


def build_phase9_plan(text: str, phase8_plan: Phase8Plan, realism_plan: RealismPlan) -> Phase9Plan:
    runtime_profile = RuntimeProfile()
    runtime_control = build_runtime_control_plan(text, phase8_plan, realism_plan)
    runtime_notes = [
        "apply_breath_events_to_token_timing",
        "apply_emotion_frames_per_sentence",
        "inject_presence_cues_as_micro-pauses",
        "support_interrupt_stop_resume_state",
        "shape_runtime_controls_into_synth_inputs",
    ]
    return Phase9Plan(
        phase8_plan=phase8_plan,
        runtime_control=runtime_control,
        runtime_profile=runtime_profile,
        runtime_notes=runtime_notes,
    )
