from __future__ import annotations

import sys

from api.bootstrap import prepare_demo_import
from api.diagnostics.runner_util import collect_events, summarize_events


def test_data_viz_after_math_assistant():
    collect_events("math-assistant", {"message": "What is 2+2?"})
    events = collect_events(
        "data-viz",
        {"message": "Plot average G3 by study time"},
    )
    summary = summarize_events(events)
    assert not summary["has_error"], summary["errors"]
    assert summary["has_token"]
    agent_file = sys.modules.get("agent", None)
    assert agent_file is not None
    assert getattr(agent_file, "__file__", "").find("Data Viz Agent") >= 0


def test_data_analysis_after_math_assistant():
    collect_events("math-assistant", {"message": "What is 2+2?"})
    events = collect_events(
        "data-analysis",
        {"message": "What CSV files are available?"},
    )
    summary = summarize_events(events)
    assert not summary["has_error"], summary["errors"]
    assert summary["has_token"]
    agent_file = sys.modules.get("agent", None)
    assert agent_file is not None
    assert getattr(agent_file, "__file__", "").find("AI Powered Data Analysis") >= 0
