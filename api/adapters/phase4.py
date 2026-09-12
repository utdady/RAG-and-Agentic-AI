from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from api.adapters.common import finish_text, hub_heavy_retrieval, require_groq
from api.bootstrap import prepare_app_import
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
    try:
        image_path = Path(path).resolve()
        prepare_app_import("NourishBot", chdir=True)
        from app import analyze_food  # noqa: WPS433

        text = analyze_food(str(image_path), dietary, workflow)
        yield task("crew", "NourishBot crew", "completed")
        yield from finish_text(str(text))
    except Exception as exc:  # noqa: BLE001
        from api.errors import humanize_exception
        from api.events import done, error

        friendly = humanize_exception(exc)
        yield task("crew", "NourishBot crew", "failed")
        yield error(friendly.message, title=friendly.title)
        yield done()


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
    include_nutrition = bool(payload.get("include_nutrition", False))
    heavy = hub_heavy_retrieval()
    yield thinking(
        "Running full meal-planning crew"
        if heavy
        else "Drafting a compact meal plan (hub lite)"
    )
    yield task("plan", "Meal plan", "running")
    try:
        import queue
        import threading

        result_q: queue.Queue[tuple[str, object]] = queue.Queue()

        def _worker() -> None:
            try:
                # Import inside the worker so SSE can heartbeat during cold loads.
                prepare_app_import("Meal Grocery Planner", chdir=True)
                from crew_app import run_planner, run_planner_lite  # noqa: WPS433

                planner = run_planner if heavy else run_planner_lite
                text = planner(
                    meal_name=meal,
                    servings=servings,
                    budget=budget,
                    dietary_restrictions=dietary,
                    cooking_skill=skill,
                    include_nutrition=include_nutrition,
                )
                result_q.put(("ok", text))
            except Exception as exc:  # noqa: BLE001
                result_q.put(("err", exc))

        worker = threading.Thread(target=_worker, daemon=True)
        worker.start()
        waited = 0
        while worker.is_alive():
            worker.join(5)
            waited += 5
            if worker.is_alive():
                yield thinking(f"Still planning your meal… ({waited}s)")

        kind, payload_or_exc = result_q.get()
        if kind == "err":
            from api.errors import humanize_exception
            from api.events import done, error

            friendly = humanize_exception(payload_or_exc)  # type: ignore[arg-type]
            yield task("plan", "Meal plan", "failed")
            yield error(friendly.message, title=friendly.title)
            yield done()
            return

        yield task("plan", "Meal plan", "completed")
        yield from finish_text(str(payload_or_exc))
    except Exception as exc:  # noqa: BLE001
        from api.errors import humanize_exception
        from api.events import done, error

        friendly = humanize_exception(exc)
        yield task("plan", "Meal plan", "failed")
        yield error(friendly.message, title=friendly.title)
        yield done()


def run_healthcare(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    mode = (payload.get("mode") or "symptoms").strip().lower()
    message = (payload.get("message") or "").strip()
    yield thinking("Educational multi-agent consult")
    prepare_app_import("Healthcare Chatbot", chdir=True)
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
