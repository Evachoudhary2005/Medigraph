"""Local speech-to-text via faster-whisper.

Loads a single shared WhisperModel on first use. Falls back to a small model
for speed on CPU. Returns text plus a rough confidence derived from the
segment's avg_logprob.
"""
from __future__ import annotations

import math
import os
import threading
from typing import Optional

# Silence the Hugging Face symlink warning on Windows (cosmetic only)
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

_model = None
_model_lock = threading.Lock()
_MODEL_SIZE = "small"   # multilingual; "tiny" is faster but weak on Hindi


def get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                from faster_whisper import WhisperModel
                _model = WhisperModel(_MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


def _confidence_from_segments(segments) -> float:
    """Very rough confidence: exp(avg_logprob) clipped to [0,1]."""
    logprobs = [s.avg_logprob for s in segments if s.avg_logprob is not None]
    if not logprobs:
        return 0.0
    avg = sum(logprobs) / len(logprobs)
    return max(0.0, min(1.0, math.exp(avg)))


def transcribe_file(path: str, language: Optional[str] = None) -> dict:
    model = get_model()
    segments, info = model.transcribe(
        path,
        language=language,       # None = auto-detect
        beam_size=1,             # fastest
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 300},
    )
    segments = list(segments)    # materialise so we can iterate twice
    text = " ".join(s.text.strip() for s in segments).strip()
    return {
        "text": text,
        "language": info.language,
        "language_probability": float(info.language_probability or 0.0),
        "confidence": _confidence_from_segments(segments),
        "duration_s": float(info.duration or 0.0),
    }
