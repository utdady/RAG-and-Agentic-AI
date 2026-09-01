from __future__ import annotations

import pytest

from api.diagnostics.cases import DEMO_CASES
from api.diagnostics.runner_util import collect_events, evaluate_case


@pytest.mark.parametrize(
    "case_id",
    [c.case_id for c in DEMO_CASES if not c.live],
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
