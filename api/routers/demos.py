from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from api.adapters.dispatch import run_demo
from api.catalog import DEMOS
from api.sse import stream_events

router = APIRouter()
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "_uploads"

KINDS_NEEDING_FILE = {
    "pdf",
    "docs",
    "image",
    "audio",
}


@router.get("/demos")
def list_demos() -> list[dict[str, Any]]:
    return DEMOS


def _demo(slug: str) -> dict[str, Any]:
    for item in DEMOS:
        if item["slug"] == slug:
            return item
    raise HTTPException(status_code=404, detail="Unknown demo")


async def _save_files(files: list[UploadFile] | None) -> list[str]:
    if not files:
        return []
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    for i, upload in enumerate(files):
        if not upload.filename:
            continue
        suffix = Path(upload.filename).suffix or ".bin"
        dest = UPLOAD_DIR / f"{i}_{upload.filename}"
        dest.write_bytes(await upload.read())
        paths.append(str(dest))
    return paths


@router.post("/demos/{slug}/run")
async def run_slug(
    slug: str,
    message: str = Form(""),
    url: str = Form(""),
    question: str = Form(""),
    mode: str = Form(""),
    meal_name: str = Form(""),
    servings: str = Form("4"),
    budget: str = Form("moderate"),
    dietary: str = Form(""),
    cooking_skill: str = Form("intermediate"),
    include_nutrition: str = Form("true"),
    workflow: str = Form("recipe"),
    files: list[UploadFile] | None = File(None),
) -> StreamingResponse:
    _demo(slug)
    paths = await _save_files(files)
    payload: dict[str, Any] = {
        "message": message,
        "url": url,
        "question": question,
        "mode": mode,
        "meal_name": meal_name,
        "servings": servings,
        "budget": budget,
        "dietary": dietary,
        "cooking_skill": cooking_skill,
        "include_nutrition": include_nutrition.lower() in {"1", "true", "yes", "on"},
        "workflow": workflow,
        "file_paths": paths,
        "file_path": paths[0] if paths else None,
    }
    return stream_events(run_demo(slug, payload))
