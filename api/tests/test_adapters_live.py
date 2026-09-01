from __future__ import annotations

import os

import pytest

from api.bootstrap import groq_ready
from api.diagnostics.cases import DEMO_CASES
from api.diagnostics.runner_util import collect_events, evaluate_case, iter_live_cases


pytestmark = pytest.mark.live


@pytest.fixture(scope="module")
def require_groq_key():
    if not groq_ready():
        pytest.skip("GROQ_API_KEY not set")


@pytest.mark.parametrize(
    "case_id",
    [c.case_id for c in iter_live_cases(DEMO_CASES, include_slow=False)],
)
def test_live_fast_cases(case_id: str, require_groq_key):
    case = next(c for c in DEMO_CASES if c.case_id == case_id)
    events = collect_events(case.slug, case.payload)
    ok, detail = evaluate_case(case, events)
    assert ok, f"{case.slug}: {detail}"


@pytest.mark.slow
@pytest.mark.parametrize(
    "case_id",
    [c.case_id for c in iter_live_cases(DEMO_CASES, include_slow=True) if c.slow],
)
def test_live_slow_cases(case_id: str, require_groq_key):
    if os.getenv("RUN_SLOW_LAB_TESTS", "").lower() not in {"1", "true", "yes"}:
        pytest.skip("Set RUN_SLOW_LAB_TESTS=1 to run slow adapter smokes")
    case = next(c for c in DEMO_CASES if c.case_id == case_id)
    events = collect_events(case.slug, case.payload)
    ok, detail = evaluate_case(case, events)
    assert ok, f"{case.slug}: {detail}"
