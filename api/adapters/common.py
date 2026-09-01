from __future__ import annotations

import io
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from api.bootstrap import groq_ready
from api.errors import demo_unavailable
from api.events import done, error
from api.sse import chunk_text

HUB_GROQ_VISION_MODEL = "qwen/qwen3.6-27b"
_RETIRED_GROQ_VISION_MARKERS = (
    "llama-4-scout",
    "llama-3.2-11b-vision-preview",
    "llama-3.2-90b-vision-preview",
    "llava-v1.5-7b-4096-preview",
)


def pin_groq_vision_model() -> str:
    """Force a current Groq vision id for hub image demos (retired ids → qwen)."""
    try:
        from shared.llm import DEFAULT_GROQ_VISION_MODEL, resolve_groq_vision_model

        model = resolve_groq_vision_model()
        fallback = DEFAULT_GROQ_VISION_MODEL
    except Exception:
        model = HUB_GROQ_VISION_MODEL
        fallback = HUB_GROQ_VISION_MODEL

    lower = model.lower()
    if any(marker in lower for marker in _RETIRED_GROQ_VISION_MARKERS):
        model = fallback
    os.environ["GROQ_VISION_MODEL"] = model
    return model


def require_groq() -> list[dict[str, Any]] | None:
    """Return error events when Groq is unavailable, else None."""
    if groq_ready():
        return None
    err = demo_unavailable()
    return [
        error(err.message, title=err.title),
        done(),
    ]

def save_upload(data: bytes, suffix: str, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / f"upload{suffix}"
    path.write_bytes(data)
    return path


def finish_text(text: str, extras: list[dict[str, Any]] | None = None) -> Iterator[dict[str, Any]]:
    yield from chunk_text(text or "")
    for ev in extras or []:
        yield ev
    yield done()


def pil_to_b64(img) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    import base64

    return base64.b64encode(buf.getvalue()).decode("ascii")
