"""Format AutoGen / GroupChat message lists for Gradio Markdown."""

from __future__ import annotations

from typing import Any


DISCLAIMER_HEALTH = (
    "> **Educational demo only — not medical advice.**  \n"
    "> This multi-agent chatbot does **not** diagnose, prescribe, or replace a "
    "licensed clinician. If you have an emergency, call local emergency services.\n\n"
)

DISCLAIMER_MENTAL = (
    "> **Educational demo only — not therapy or crisis care.**  \n"
    "> This chatbot is **not** a substitute for professional mental health support. "
    "If you are in crisis, contact local emergency services or a crisis hotline.\n\n"
)


def format_messages(messages: list[Any] | None) -> str:
    if not messages:
        return "_No messages captured._"

    lines: list[str] = []
    for msg in messages:
        if isinstance(msg, dict):
            name = msg.get("name") or msg.get("role") or "agent"
            content = msg.get("content") or ""
        else:
            name = getattr(msg, "name", None) or getattr(msg, "role", "agent")
            content = getattr(msg, "content", str(msg))
        if not content:
            continue
        lines.append(f"### {name}\n\n{content}\n")
    return "\n".join(lines) if lines else "_No messages captured._"
