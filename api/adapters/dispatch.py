from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from api.adapters.phase1 import (
    run_math_assistant,
    run_pdf_qa,
    run_sql_agent,
    run_youtube,
)
from api.adapters.phase2 import (
    run_connoisseur,
    run_docchat,
    run_food_search,
    run_icebreaker,
)
from api.adapters.phase3 import (
    run_data_analysis,
    run_data_viz,
    run_model_compare,
    run_nutrition_coach,
    run_style_finder,
)
from api.adapters.phase4 import run_healthcare, run_meal_planner, run_nourishbot
from api.adapters.phase5 import run_meeting_assistant
from api.errors import unknown_demo
from api.events import done, error

RUNNERS: dict[str, Callable[[dict[str, Any]], Iterator[dict[str, Any]]]] = {
    "pdf-qa": run_pdf_qa,
    "sql-agent": run_sql_agent,
    "math-assistant": run_math_assistant,
    "youtube-summarizer": run_youtube,
    "connoisseur": run_connoisseur,
    "docchat": run_docchat,
    "food-search": run_food_search,
    "icebreaker": run_icebreaker,
    "data-viz": run_data_viz,
    "data-analysis": run_data_analysis,
    "style-finder": run_style_finder,
    "nutrition-coach": run_nutrition_coach,
    "model-compare": run_model_compare,
    "nourishbot": run_nourishbot,
    "meal-planner": run_meal_planner,
    "healthcare": run_healthcare,
    "meeting-assistant": run_meeting_assistant,
}


def run_demo(slug: str, payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    runner = RUNNERS.get(slug)
    if runner is None:
        err = unknown_demo()
        yield error(err.message, title=err.title)
        yield done()
        return
    yield from runner(payload)
