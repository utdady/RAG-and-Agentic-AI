from __future__ import annotations

import base64
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from api.adapters.common import (
    finish_text,
    hub_heavy_retrieval,
    pin_groq_vision_model,
    pil_to_b64,
    require_groq,
)
from api.bootstrap import prepare_app_import, prepare_demo_import
from api.errors import humanize_exception
from api.events import done, error, image, thinking


def run_data_viz(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    question = (payload.get("message") or "").strip()
    yield thinking("Loading student-mat CSV")
    prepare_demo_import("Data Viz Agent", chdir=True)
    import importlib

    from download_data import main as download_csv  # noqa: WPS433

    download_csv()
    agent_mod = importlib.import_module("agent")
    importlib.reload(agent_mod)
    if hasattr(agent_mod, "reset_caches"):
        agent_mod.reset_caches()

    yield thinking("Running pandas / matplotlib agent")
    text, images = agent_mod.run_query(question)
    extras = []
    for img in images or []:
        if hasattr(img, "save"):
            extras.append(image(pil_to_b64(img)))
    yield from finish_text(text, extras)


def run_data_analysis(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    question = (payload.get("message") or "").strip()
    yield thinking("Ensuring analysis datasets")
    prepare_demo_import("AI Powered Data Analysis")
    from download_data import main as download_datasets  # noqa: WPS433

    download_datasets()
    from agent import run_query  # noqa: WPS433

    text, _ = run_query(question)
    yield from finish_text(text)


def _reload_style_finder_modules() -> object:
    """Import Style Finder with fresh demo modules (uvicorn does not watch demo folders)."""
    import importlib
    import sys

    pin_groq_vision_model()
    prepare_demo_import("Style Finder", chdir=True)
    for name in ("app", "llm_service", "config", "helpers", "image_processor"):
        sys.modules.pop(name, None)

    shared_llm = importlib.import_module("shared.llm")
    importlib.reload(shared_llm)
    pin_groq_vision_model()

    config = importlib.import_module("config")
    importlib.reload(config)

    llm_service = importlib.import_module("llm_service")
    importlib.reload(llm_service)

    style_app = importlib.import_module("app")
    importlib.reload(style_app)
    return style_app


def run_style_finder(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    path = payload.get("file_path")
    if not path:
        yield from finish_text("Upload an outfit photo first.")
        return

    from PIL import Image as PILImage  # noqa: WPS433

    # Free / small hosts: vision-only — ResNet50 + pickle OOMs ~512MB Render.
    if not hub_heavy_retrieval():
        yield thinking("Vision outfit analysis (catalog match skipped on free tier)")
        try:
            image_path = Path(path).resolve()
            pin_groq_vision_model()
            prepare_demo_import("Style Finder", chdir=True)
            import io

            from helpers import process_response  # noqa: WPS433
            from llm_service import VisionFashionService  # noqa: WPS433

            img = PILImage.open(image_path).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

            vision = VisionFashionService()
            analysis = process_response(vision.generate_outfit_only_response(b64))
            note = (
                "_Catalog matching is off on this host to stay within free-tier memory. "
                "Showing a vision-based outfit analysis instead._"
            )
            body = f"{analysis}\n\n---\n\n{note}"
            yield from finish_text(body, [image(pil_to_b64(img))])
        except Exception as exc:  # noqa: BLE001
            friendly = humanize_exception(exc)
            yield error(friendly.message, title=friendly.title)
            yield done()
        return

    yield thinking("Loading catalog embeddings")
    try:
        image_path = Path(path).resolve()
        style_app = _reload_style_finder_modules()
        analyze_style = style_app.analyze_style

        img = PILImage.open(image_path).convert("RGB")
        matched, analysis, meta, status = analyze_style(img)
        extras = []
        if matched is not None:
            extras.append(image(pil_to_b64(matched)))
        # Drop provider/model prefixes from status (e.g. groq:…).
        safe_status = status or ""
        for prefix in ("groq:", "ollama:"):
            if prefix in safe_status.lower():
                parts = [p.strip() for p in safe_status.split("|")]
                parts = [p for p in parts if not p.lower().startswith(prefix)]
                safe_status = " | ".join(parts)
        body = f"{analysis}\n\n---\n\n### Catalog match\n\n{meta}"
        if safe_status:
            body = f"{body}\n\n_{safe_status}_"
        yield from finish_text(body, extras)
    except Exception as exc:  # noqa: BLE001
        friendly = humanize_exception(exc)
        yield error(friendly.message, title=friendly.title)
        yield done()


def run_nutrition_coach(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    path = payload.get("file_path")
    question = (payload.get("message") or "How many calories are in this food?").strip()
    if not path:
        yield from finish_text("Upload a meal photo first.")
        return
    yield thinking("Vision nutrition assessment")
    try:
        image_path = Path(path).resolve()
        pin_groq_vision_model()
        prepare_app_import("AI Nutrition Coach")
        import queue
        import threading

        from app import ASSISTANT_PROMPT, generate_model_response  # noqa: WPS433
        from shared.vision_image import encode_image_for_vision  # noqa: WPS433

        encoded = encode_image_for_vision(image_path)
        result_q: queue.Queue[tuple[str, object]] = queue.Queue()

        def _worker() -> None:
            try:
                text = generate_model_response(
                    encoded, question, ASSISTANT_PROMPT, as_html=False
                )
                result_q.put(("ok", text))
            except Exception as exc:  # noqa: BLE001
                result_q.put(("err", exc))

        worker = threading.Thread(target=_worker, daemon=True)
        worker.start()
        waited = 0
        while worker.is_alive():
            worker.join(10)
            waited += 10
            if worker.is_alive():
                yield thinking(f"Still analyzing the meal photo… ({waited}s)")

        kind, payload_or_exc = result_q.get()
        if kind == "err":
            friendly = humanize_exception(payload_or_exc)  # type: ignore[arg-type]
            yield error(friendly.message, title=friendly.title)
            yield done()
            return
        yield from finish_text(str(payload_or_exc))
    except Exception as exc:  # noqa: BLE001
        friendly = humanize_exception(exc)
        yield error(friendly.message, title=friendly.title)
        yield done()


def run_model_compare(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    blocked = require_groq()
    if blocked:
        yield from blocked
        return
    question = (payload.get("message") or "").strip()
    yield thinking("Querying three model slots")
    prepare_demo_import("Model Comparison Chat")
    from config import SYSTEM_PROMPT  # noqa: WPS433
    from models import granite_response, llama_response, mistral_response  # noqa: WPS433

    parts = []
    for name, fn in (
        ("Fast slot", llama_response),
        ("Balanced slot", granite_response),
        ("Quality slot", mistral_response),
    ):
        try:
            out = fn(SYSTEM_PROMPT, question)
            if hasattr(out, "model_dump"):
                out = out.model_dump()
            resp = out.get("response") if isinstance(out, dict) else str(out)
            summary = out.get("summary", "") if isinstance(out, dict) else ""
            parts.append(f"### {name}\n{resp}\n\n_{summary}_")
        except Exception as exc:
            parts.append(f"### {name}\nError: {exc}")
    yield from finish_text("\n\n".join(parts))
