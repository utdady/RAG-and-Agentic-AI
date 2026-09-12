"""CrewAI LLM helper (Groq / Ollama)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from crewai import LLM

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.llm import resolve_groq_model


def get_crew_llm() -> LLM:
    provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if provider == "auto":
        provider = "groq" if os.getenv("GROQ_API_KEY", "").strip() else "ollama"

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Set GROQ_API_KEY in repo-root .env")
        model = resolve_groq_model()
        return LLM(
            model=f"groq/{model}",
            api_key=api_key,
            temperature=0.3,
            max_tokens=2500,
        )

    model = os.getenv("OLLAMA_MODEL", "llama3.2").strip() or "llama3.2"
    return LLM(
        model=f"ollama/{model}",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.3,
        max_tokens=2500,
    )
