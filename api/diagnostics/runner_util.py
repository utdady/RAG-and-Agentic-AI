"""Shared helpers for adapter and HTTP smoke runs."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from api.adapters.dispatch import run_demo
from api.diagnostics.cases import DemoCase


def collect_events(slug: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    return list(run_demo(slug, payload))


def summarize_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    types = [e.get("type") for e in events]
    errors = [e.get("message", "") for e in events if e.get("type") == "error"]
    tokens = "".join(e.get("text", "") for e in events if e.get("type") == "token")
    return {
        "count": len(events),
        "types": types,
        "errors": errors,
        "tokens": tokens,
        "has_done": types[-1] == "done" if types else False,
        "has_token": any(t == "token" for t in types),
        "has_error": any(t == "error" for t in types),
    }


def evaluate_case(case: DemoCase, events: list[dict[str, Any]]) -> tuple[bool, str]:
    summary = summarize_events(events)
    if not events:
        return False, "adapter returned zero events"
    if not summary["has_done"]:
        return False, "missing done event"
    if summary["has_error"]:
        return False, summary["errors"][0] or "error event"
    if case.expect_token and not summary["has_token"]:
        if case.allow_friendly_no_file:
            return True, "friendly no-file guidance"
        return False, "no token output"
    return True, "ok"


def iter_live_cases(
    cases: list[DemoCase],
    *,
    include_slow: bool = False,
) -> Iterator[DemoCase]:
    for case in cases:
        if not case.live:
            continue
        if case.slow and not include_slow:
            continue
        if case.skip_live_reason and not include_slow:
            continue
        yield case
