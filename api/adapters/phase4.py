from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from api.adapters.common import finish_text, require_groq
from api.bootstrap import add_app, prepare_app_import
from api.events import task, thinking


def run_nourishbot(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    path = payload.get("file_path")
    dietary = (payload.get("dietary") or "").strip()
    workflow = (payload.get("workflow") or "recipe").strip().lower()
    if not path:
        yield from finish_text("Upload a food photo first.")
        return
    yield thinking("CrewAI nutrition crew")
    yield task("crew", "NourishBot crew", "running")
    prepare_app_import("NourishBot", chdir=True)
    from app import analyze_food  # noqa: WPS433

    text = analyze_food(path, dietary, workflow)
    yield task("crew", "NourishBot crew", "completed")
    yield from finish_text(str(text))


def run_meal_planner(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    meal = (payload.get("meal_name") or payload.get("message") or "weeknight pasta").strip()
    servings = int(payload.get("servings") or 4)
    budget = (payload.get("budget") or "moderate").strip()
    dietary = (payload.get("dietary") or "").strip()
    skill = (payload.get("cooking_skill") or "intermediate").strip()
    include_nutrition = bool(payload.get("include_nutrition", True))
    yield thinking("Running sequential meal-planning crew")
    yield task("plan", "Meal plan", "running")
    add_app("Meal Grocery Planner", chdir=True)
    from crew_app import run_planner  # noqa: WPS433

    text = run_planner(
        meal_name=meal,
        servings=servings,
        budget=budget,
        dietary_restrictions=dietary,
        cooking_skill=skill,
        include_nutrition=include_nutrition,
    )
    yield task("plan", "Meal plan", "completed")
    yield from finish_text(str(text))


def run_healthcare(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    mode = (payload.get("mode") or "symptoms").strip().lower()
    message = (payload.get("message") or "").strip()
    yield thinking("Educational multi-agent consult")
    add_app("Healthcare Chatbot", chdir=True)
    disclaimer = (
        "Educational demo only — not medical or mental-health care. "
        "If you need help, contact a licensed clinician or emergency services.\n\n"
    )
    if mode in {"mental", "mental-health", "feelings"}:
        yield task("mental", "Mental health crew", "running")
        from mental_health_crew import run_mental_health_chat  # noqa: WPS433

        text = run_mental_health_chat(message)
        yield task("mental", "Mental health crew", "completed")
    else:
        yield task("consult", "Symptom consultation", "running")
        from healthcare_crew import run_healthcare_consultation  # noqa: WPS433

        text = run_healthcare_consultation(message)
        yield task("consult", "Symptom consultation", "completed")
    yield from finish_text(disclaimer + str(text))
