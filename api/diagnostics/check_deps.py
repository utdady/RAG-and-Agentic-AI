"""Import-check each hub demo's Python dependencies (no LLM calls)."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# slug -> (folder, module, chdir)
DEMO_IMPORTS: dict[str, tuple[str, str, bool]] = {
    "pdf-qa": ("PDF QA Bot", "app", False),
    "sql-agent": ("Natural Language SQL Agent", "agent", False),
    "math-assistant": ("AI Math Assistant", "agent", False),
    "youtube-summarizer": ("YouTube Summarizer", "app", False),
    "connoisseur": ("Connoisseur Companion", "agents.workflow", True),
    "docchat": ("DocChat", "agents.workflow", True),
    "food-search": ("Food Search RAG", "rag_chat", False),
    "icebreaker": ("Icebreaker Bot", "app", True),
    "data-viz": ("Data Viz Agent", "agent", False),
    "data-analysis": ("AI Powered Data Analysis", "agent", False),
    "style-finder": ("Style Finder", "app", True),
    "nutrition-coach": ("AI Nutrition Coach", "app", False),
    "model-compare": ("Model Comparison Chat", "models", False),
    "nourishbot": ("NourishBot", "app", True),
    "meal-planner": ("Meal Grocery Planner", "crew_app", True),
    "healthcare": ("Healthcare Chatbot", "healthcare_crew", True),
    "meeting-assistant": ("Meeting Assistant", "app", True),
}


@dataclass
class DepResult:
    slug: str
    ok: bool
    detail: str = ""


def check_demo(slug: str) -> DepResult:
    folder, module, chdir = DEMO_IMPORTS[slug]
    app_path = REPO / folder
    code = f"""
import os, sys
repo = {str(REPO)!r}
app = {str(app_path)!r}
sys.path.insert(0, repo)
sys.path.insert(0, app)
if {chdir!r}:
    os.chdir(app)
import importlib
importlib.import_module({module!r})
print("ok")
"""
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=180,
    )
    if proc.returncode == 0:
        return DepResult(slug, True, module)
    err = (proc.stderr or proc.stdout or "unknown error").strip().splitlines()
    line = err[-1] if err else "import failed"
    return DepResult(slug, False, line[:200])


def main() -> int:
    results = [check_demo(slug) for slug in sorted(DEMO_IMPORTS)]
    width = max(len(r.slug) for r in results)
    for r in results:
        mark = "OK" if r.ok else "FAIL"
        detail = f" — {r.detail}" if r.detail else ""
        print(f"[{mark:<4}] {r.slug:<{width}}{detail}")
    failed = sum(1 for r in results if not r.ok)
    print(f"\n{len(results) - failed}/{len(results)} import-ready")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
