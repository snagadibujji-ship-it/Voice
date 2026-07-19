from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


DEFAULT_PHONEME_DICTIONARY: Dict[str, List[str]] = {
    "hello": ["HH", "AH", "L", "OW"],
    "gowtham": ["G", "OW", "TH", "AH", "M"],
    "axioma": ["AE", "K", "S", "IY", "OW", "M", "AH"],
    "axima": ["AE", "K", "S", "IY", "M", "AH"],
    "voice": ["V", "OY", "S"],
    "music": ["M", "Y", "UW", "Z", "IH", "K"],
    "welcome": ["W", "EH", "L", "K", "AH", "M"],
    "back": ["B", "AE", "K"],
    "create": ["K", "R", "IY", "EY", "T"],
    "epic": ["EH", "P", "IH", "K"],
    "future": ["F", "Y", "UW", "CH", "ER"],
    "futuristic": ["F", "Y", "UW", "CH", "ER", "IH", "S", "T", "IH", "K"],
    "speak": ["S", "P", "IY", "K"],
    "talk": ["T", "AO", "K"],
    "with": ["W", "IH", "TH"],
    "it": ["IH", "T"],
}


@dataclass
class VoiceIdentity:
    name: str = "Axima"
    warmth: float = 0.72
    clarity: float = 0.88
    futuristic_edge: float = 0.52
    softness: float = 0.4
    confidence: float = 0.86

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class PhonemeWord:
    word: str
    phonemes: List[str]
    stress_index: int = 0
    linked_from_previous: bool = False
    linked_to_next: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class ProsodyCurve:
    pitch_points: List[float] = field(default_factory=list)
    energy_points: List[float] = field(default_factory=list)
    duration_points: List[float] = field(default_factory=list)
    pause_points: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pitch_points": self.pitch_points,
            "energy_points": self.energy_points,
            "duration_points": self.duration_points,
            "pause_points": self.pause_points,
        }


@dataclass
class EmotionRenderPlan:
    emotion: str
    pitch_scale: float
    energy_scale: float
    duration_scale: float
    pause_scale: float
    emphasis_words: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class RealismPlan:
    identity: VoiceIdentity
    phoneme_words: List[PhonemeWord]
    prosody_curve: ProsodyCurve
    emotion_plan: EmotionRenderPlan
    coarticulation_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity.to_dict(),
            "phoneme_words": [word.to_dict() for word in self.phoneme_words],
            "prosody_curve": self.prosody_curve.to_dict(),
            "emotion_plan": self.emotion_plan.to_dict(),
            "coarticulation_notes": self.coarticulation_notes,
        }


def build_phoneme_dictionary() -> Dict[str, List[str]]:
    return dict(DEFAULT_PHONEME_DICTIONARY)


def _simple_g2p(word: str) -> List[str]:
    letters = word.lower()
    result: List[str] = []
    last = ""
    mapping = {
        "a": "AH",
        "b": "B",
        "c": "K",
        "d": "D",
        "e": "EH",
        "f": "F",
        "g": "G",
        "h": "HH",
        "i": "IH",
        "j": "JH",
        "k": "K",
        "l": "L",
        "m": "M",
        "n": "N",
        "o": "OW",
        "p": "P",
        "q": "K",
        "r": "R",
        "s": "S",
        "t": "T",
        "u": "UW",
        "v": "V",
        "w": "W",
        "x": "KS",
        "y": "Y",
        "z": "Z",
    }
    for ch in letters:
        ph = mapping.get(ch)
        if not ph:
            continue
        if ph != last:
            if len(ph) == 2 and ph == "KS":
                result.extend(["K", "S"])
            else:
                result.append(ph)
            last = ph
    return result or ["AH"]


def g2p(text: str, dictionary: Dict[str, List[str]] | None = None) -> List[PhonemeWord]:
    dictionary = dictionary or build_phoneme_dictionary()
    words: List[PhonemeWord] = []
    raw_words = [w.strip(".,!?;:\"'()[]{}") for w in text.split() if w.strip()]
    for index, word in enumerate(raw_words):
        key = word.lower()
        phonemes = dictionary.get(key) or _simple_g2p(key)
        words.append(
            PhonemeWord(
                word=word,
                phonemes=phonemes,
                stress_index=0 if len(phonemes) <= 2 else min(1, len(phonemes) - 1),
                linked_from_previous=index > 0
                and key in {"to", "of", "and", "with", "the"},
                linked_to_next=index < len(raw_words) - 1
                and key in {"to", "of", "and", "with", "the"},
            )
        )
    return words


def detect_emotion(text: str, meaning: Dict[str, Any]) -> str:
    lowered = text.lower()
    if any(
        token in lowered
        for token in ["!", "amazing", "epic", "wow", "great", "awesome"]
    ):
        return "excited"
    if any(token in lowered for token in ["sorry", "sad", "unfortunately", "missed"]):
        return "soft"
    if any(token in lowered for token in ["urgent", "now", "quick", "fast"]):
        return "urgent"
    if meaning.get("emotion"):
        return str(meaning["emotion"])
    return "neutral"


def render_emotion(emotion: str) -> EmotionRenderPlan:
    if emotion == "excited":
        return EmotionRenderPlan(
            emotion,
            pitch_scale=1.12,
            energy_scale=1.16,
            duration_scale=0.94,
            pause_scale=0.85,
            emphasis_words=["amazing", "epic", "wow"],
        )
    if emotion == "soft":
        return EmotionRenderPlan(
            emotion,
            pitch_scale=0.96,
            energy_scale=0.86,
            duration_scale=1.12,
            pause_scale=1.18,
            emphasis_words=[],
        )
    if emotion == "urgent":
        return EmotionRenderPlan(
            emotion,
            pitch_scale=1.03,
            energy_scale=1.2,
            duration_scale=0.9,
            pause_scale=0.8,
            emphasis_words=["now", "quick"],
        )
    return EmotionRenderPlan(
        emotion,
        pitch_scale=1.0,
        energy_scale=1.0,
        duration_scale=1.0,
        pause_scale=1.0,
        emphasis_words=[],
    )


def build_prosody_curve(
    text: str,
    phoneme_words: List[PhonemeWord],
    emotion_plan: EmotionRenderPlan,
    voice_identity: VoiceIdentity,
) -> ProsodyCurve:
    pitch_points: List[float] = []
    energy_points: List[float] = []
    duration_points: List[float] = []
    pause_points: List[float] = []
    words = [w.strip(".,!?;:\"'()[]{}") for w in text.split() if w.strip()]
    for index, word in enumerate(words):
        emphasis = 1.08 if word.lower() in emotion_plan.emphasis_words else 1.0
        token_count = max(
            1, len(phoneme_words[index].phonemes) if index < len(phoneme_words) else 1
        )
        pitch_points.append(
            (1.0 + (index % 3) * 0.02)
            * emotion_plan.pitch_scale
            * (1.0 + voice_identity.futuristic_edge * 0.02)
            * emphasis
        )
        energy_points.append(
            (0.9 + (index % 2) * 0.05)
            * emotion_plan.energy_scale
            * (1.0 + voice_identity.confidence * 0.01)
            * emphasis
        )
        duration_points.append(
            max(0.08, 0.11 * emotion_plan.duration_scale + token_count * 0.002)
        )
        pause_points.append(
            0.02 * emotion_plan.pause_scale if index < len(words) - 1 else 0.0
        )
    return ProsodyCurve(
        pitch_points=pitch_points,
        energy_points=energy_points,
        duration_points=duration_points,
        pause_points=pause_points,
    )


def apply_coarticulation(phoneme_words: List[PhonemeWord]) -> List[str]:
    output: List[str] = []
    for index, word in enumerate(phoneme_words):
        if index > 0:
            prev = phoneme_words[index - 1]
            if prev.word.lower() in {"to", "and", "with", "the"} and word.phonemes:
                output.append("_")
        for phoneme in word.phonemes:
            output.append(phoneme)
        if index < len(phoneme_words) - 1 and word.word.lower() in {
            "to",
            "and",
            "with",
            "the",
        }:
            output.append("~")
    return output


def build_realism_plan(text: str, meaning: Dict[str, Any]) -> RealismPlan:
    identity = VoiceIdentity()
    dictionary = build_phoneme_dictionary()
    phoneme_words = g2p(text, dictionary)
    emotion = detect_emotion(text, meaning)
    emotion_plan = render_emotion(emotion)
    prosody_curve = build_prosody_curve(text, phoneme_words, emotion_plan, identity)
    coarticulation_notes = [
        "blend_function_words",
        "light_release_consonants",
        "avoid_flat_pitch",
    ]
    return RealismPlan(
        identity=identity,
        phoneme_words=phoneme_words,
        prosody_curve=prosody_curve,
        emotion_plan=emotion_plan,
        coarticulation_notes=coarticulation_notes,
    )
