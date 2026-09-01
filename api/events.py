"""SSE event payloads for the Beautiful UI hub."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class HubEvent(BaseModel):
    type: Literal[
        "thinking",
        "task",
        "context",
        "tool",
        "token",
        "followup",
        "image",
        "error",
        "done",
    ]
    label: str | None = None
    id: str | None = None
    name: str | None = None
    status: str | None = None
    title: str | None = None
    snippet: str | None = None
    source: str | None = None
    text: str | None = None
    suggestions: list[str] | None = None
    mime: str | None = None
    data: str | None = None
    message: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


def thinking(label: str) -> dict:
    return HubEvent(type="thinking", label=label).model_dump(exclude_none=True)


def task(id: str, name: str, status: str) -> dict:
    return HubEvent(type="task", id=id, name=name, status=status).model_dump(
        exclude_none=True
    )


def context(title: str, snippet: str, source: str = "") -> dict:
    return HubEvent(
        type="context", title=title, snippet=snippet, source=source
    ).model_dump(exclude_none=True)


def tool(name: str, status: str = "done") -> dict:
    return HubEvent(type="tool", name=name, status=status).model_dump(exclude_none=True)


def token(text: str) -> dict:
    return HubEvent(type="token", text=text).model_dump(exclude_none=True)


def followup(suggestions: list[str]) -> dict:
    return HubEvent(type="followup", suggestions=suggestions).model_dump(
        exclude_none=True
    )


def image(data_b64: str, mime: str = "image/png") -> dict:
    return HubEvent(type="image", data=data_b64, mime=mime).model_dump(exclude_none=True)


def error(message: str, *, title: str | None = None) -> dict:
    return HubEvent(type="error", message=message, title=title).model_dump(
        exclude_none=True
    )


def done() -> dict:
    return HubEvent(type="done").model_dump(exclude_none=True)
