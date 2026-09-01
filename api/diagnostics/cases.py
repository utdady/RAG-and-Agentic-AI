"""Per-demo smoke cases and repo mappings."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

SLUG_APP_FOLDERS: dict[str, str] = {
    "pdf-qa": "PDF QA Bot",
    "sql-agent": "Natural Language SQL Agent",
    "math-assistant": "AI Math Assistant",
    "youtube-summarizer": "YouTube Summarizer",
    "connoisseur": "Connoisseur Companion",
    "docchat": "DocChat",
    "food-search": "Food Search RAG",
    "icebreaker": "Icebreaker Bot",
    "data-viz": "Data Viz Agent",
    "data-analysis": "AI Powered Data Analysis",
    "style-finder": "Style Finder",
    "nutrition-coach": "AI Nutrition Coach",
    "model-compare": "Model Comparison Chat",
    "nourishbot": "NourishBot",
    "meal-planner": "Meal Grocery Planner",
    "healthcare": "Healthcare Chatbot",
    "meeting-assistant": "Meeting Assistant",
}


@dataclass(frozen=True)
class DemoCase:
    slug: str
    payload: dict[str, Any] = field(default_factory=dict)
    fixture: str | None = None
    case_id: str = ""
    expect_token: bool = True
    allow_friendly_no_file: bool = False
    live: bool = True
    slow: bool = False
    skip_live_reason: str = ""

    def __post_init__(self) -> None:
        if not self.case_id:
            object.__setattr__(self, "case_id", self.slug)


def fixture_path(name: str) -> Path:
    return FIXTURES / name


def build_cases() -> list[DemoCase]:
    txt = str(fixture_path("sample.txt"))
    pdf = str(fixture_path("sample.pdf"))
    png = str(fixture_path("sample.png"))
    wav = str(fixture_path("sample.wav"))

    return [
        DemoCase("math-assistant", {"message": "What is 2+2?"}),
        DemoCase("sql-agent", {"message": "How many albums are in the database?"}),
        DemoCase(
            "pdf-qa",
            {"message": "What city is mentioned?", "file_path": pdf},
            fixture="sample.pdf",
            slow=True,
        ),
        DemoCase(
            "youtube-summarizer",
            {"url": "https://www.youtube.com/watch?v=jNQXAC9IVRw", "message": ""},
            slow=True,
        ),
        DemoCase(
            "connoisseur",
            {"message": "Vegetarian date night in San Francisco, lively vibe"},
            slow=True,
        ),
        DemoCase(
            "docchat",
            {"message": "What is the capital of France?", "file_path": txt},
            fixture="sample.txt",
            slow=True,
        ),
        DemoCase("food-search", {"message": "healthy spicy dinner under 400 calories"}),
        DemoCase("icebreaker", {"message": "What should I mention as an icebreaker?"}),
        DemoCase(
            "data-viz",
            {"message": "How many rows are in the student dataset?"},
            slow=True,
        ),
        DemoCase(
            "data-analysis",
            {"message": "What CSV files are available?"},
            slow=True,
        ),
        DemoCase(
            "style-finder",
            {"message": "", "file_path": png},
            fixture="sample.png",
            slow=True,
        ),
        DemoCase(
            "nutrition-coach",
            {"message": "Describe this meal briefly.", "file_path": png},
            fixture="sample.png",
            slow=True,
        ),
        DemoCase(
            "model-compare",
            {"message": "Reply in one sentence: decline a meeting politely."},
            slow=True,
        ),
        DemoCase(
            "nourishbot",
            {"message": "", "file_path": png, "workflow": "recipe"},
            fixture="sample.png",
            slow=True,
        ),
        DemoCase(
            "meal-planner",
            {
                "meal_name": "weeknight pasta",
                "servings": "2",
                "budget": "moderate",
                "dietary": "",
                "cooking_skill": "beginner",
            },
            slow=True,
        ),
        DemoCase(
            "healthcare",
            {"message": "I have a mild headache and feel tired.", "mode": "symptoms"},
            slow=True,
        ),
        DemoCase(
            "meeting-assistant",
            {"message": "", "file_path": wav},
            fixture="sample.wav",
            slow=True,
            skip_live_reason="Whisper transcription is CPU-heavy; use --include-slow",
        ),
        DemoCase(
            "pdf-qa",
            {"message": "test"},
            case_id="pdf-qa-no-file",
            expect_token=True,
            allow_friendly_no_file=True,
            live=False,
        ),
    ]


DEMO_CASES = build_cases()
