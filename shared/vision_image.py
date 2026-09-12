"""Compress / normalize images for Groq (and similar) vision APIs."""

from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import BinaryIO, Union

from PIL import Image

Source = Union[str, Path, bytes, BinaryIO]

# Phone photos are often multi‑MB; Groq also rejects <2px images.
_DEFAULT_MAX_SIDE = 1280
_DEFAULT_QUALITY = 85
_MIN_SIDE = 2


def encode_image_for_vision(
    source: Source,
    *,
    max_side: int = _DEFAULT_MAX_SIDE,
    quality: int = _DEFAULT_QUALITY,
) -> str:
    """Return JPEG base64 (no data: prefix), resized for vision APIs."""
    if isinstance(source, (str, Path)):
        img = Image.open(source)
    elif isinstance(source, bytes):
        img = Image.open(io.BytesIO(source))
    else:
        img = Image.open(source)

    img = img.convert("RGB")
    w, h = img.size
    if w < _MIN_SIDE or h < _MIN_SIDE:
        raise ValueError(
            f"Image is too small ({w}×{h}). Use a normal meal photo (at least "
            f"{_MIN_SIDE}×{_MIN_SIDE} pixels)."
        )

    longest = max(w, h)
    if longest > max_side:
        scale = max_side / float(longest)
        img = img.resize(
            (max(_MIN_SIDE, int(w * scale)), max(_MIN_SIDE, int(h * scale))),
            Image.Resampling.LANCZOS,
        )

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
