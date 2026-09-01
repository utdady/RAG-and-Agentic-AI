"""Turn adapter events into SSE."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from typing import Any

from fastapi.responses import StreamingResponse

from api.errors import humanize_exception
from api.events import done, error, token

logger = logging.getLogger(__name__)

def chunk_text(text: str, size: int = 48) -> Iterator[dict[str, Any]]:
    if not text:
        return
    for i in range(0, len(text), size):
        yield token(text[i : i + size])


def encode_event(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def stream_events(events: Iterator[dict[str, Any]]) -> StreamingResponse:
    def gen():
        try:
            for ev in events:
                yield encode_event(ev)
        except Exception as exc:
            logger.exception("Demo run failed")
            friendly = humanize_exception(exc)
            yield encode_event(error(friendly.message, title=friendly.title))
            yield encode_event(done())
    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
