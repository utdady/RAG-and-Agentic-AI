from __future__ import annotations

import os

import pytest

from api.diagnostics.cases import DEMO_CASES
from api.diagnostics.runner_util import collect_events, evaluate_case

_UNIT_CASES = [c.case_id for c in DEMO_CASES if not c.live and c.case_id != "pdf-qa-no-file"]

_LIVE_KEY_SKIP = pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"), reason="needs GROQ_API_KEY"
)


@pytest.mark.parametrize(
    "case_id",
    [
        pytest.param(
            "pdf-qa-no-file",
            marks=[pytest.mark.live, _LIVE_KEY_SKIP],
        ),
        *_UNIT_CASES,
    ],
)
def test_unit_cases(case_id: str):
    case = next(c for c in DEMO_CASES if c.case_id == case_id)
    events = collect_events(case.slug, case.payload)
    ok, detail = evaluate_case(case, events)
    assert ok, detail


def test_unknown_slug_returns_error():
    events = collect_events("not-a-real-slug", {"message": "hi"})
    assert any(e.get("type") == "error" for e in events)
    assert events[-1].get("type") == "done"