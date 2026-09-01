"""Create minimal binary fixtures for smoke tests."""

from __future__ import annotations

import base64
import struct
import wave
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent

SAMPLE_TXT = (
    "AI Lab fixture document.\n"
    "The capital of France is Paris.\n"
    "This file is used by DocChat smoke tests.\n"
)

# 1x1 PNG
PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def write_minimal_pdf(path: Path) -> None:
    """Minimal PDF with extractable text (Helvetica)."""
    content = b"BT /F1 12 Tf 72 720 Td (Lab fixture: Paris is the capital of France.) Tj ET"
    objects = [
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        (
            b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n"
        ),
        f"4 0 obj<< /Length {len(content)} >>stream\n".encode() + content + b"\nendstream\nendobj\n",
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n",
    ]
    body = b"".join(objects)
    xref_positions = []
    cursor = 0
    for obj in objects:
        xref_positions.append(cursor)
        cursor += len(obj)
    xref_start = len(b"%PDF-1.4\n") + len(body)
    xref = [b"xref\n", f"0 {len(objects) + 1}\n".encode(), b"0000000000 65535 f \n"]
    offset = len(b"%PDF-1.4\n")
    for pos in xref_positions:
        xref.append(f"{offset + pos:010d} 00000 n \n".encode())
    trailer = (
        b"trailer<< /Size 6 /Root 1 0 R >>\nstartxref\n"
        + str(xref_start).encode()
        + b"\n%%EOF\n"
    )
    path.write_bytes(b"%PDF-1.4\n" + body + b"".join(xref) + trailer)


def write_minimal_wav(path: Path, seconds: float = 0.25, rate: int = 16000) -> None:
    frames = int(rate * seconds)
    silent = struct.pack("<h", 0) * frames
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(silent)


def ensure_fixtures() -> list[str]:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    created: list[str] = []

    txt = FIXTURES / "sample.txt"
    if not txt.exists():
        txt.write_text(SAMPLE_TXT, encoding="utf-8")
        created.append("sample.txt")

    png = FIXTURES / "sample.png"
    if not png.exists():
        png.write_bytes(base64.b64decode(PNG_B64))
        created.append("sample.png")

    pdf = FIXTURES / "sample.pdf"
    if not pdf.exists():
        write_minimal_pdf(pdf)
        created.append("sample.pdf")

    wav = FIXTURES / "sample.wav"
    if not wav.exists():
        write_minimal_wav(wav)
        created.append("sample.wav")

    return created


if __name__ == "__main__":
    made = ensure_fixtures()
    if made:
        print("Created:", ", ".join(made))
    else:
        print("Fixtures already present.")
