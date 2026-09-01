from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from api.adapters.common import finish_text, require_groq
from api.bootstrap import add_app, prepare_app_import
from api.events import thinking


def run_meeting_assistant(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    path = payload.get("file_path")
    if not path:
        yield from finish_text("Upload meeting audio first.")
        return
    yield thinking("Transcribing with Whisper-tiny (CPU — this can take a while)")
    prepare_app_import("Meeting Assistant", chdir=True)
    from app import transcript_audio  # noqa: WPS433

    result, _outfile = transcript_audio(path)
    yield from finish_text(str(result))
