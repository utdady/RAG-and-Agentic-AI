"""CrewAI text LLM + LangChain vision helpers (Groq / Ollama)."""

from __future__ import annotations

import os

from crewai import LLM

DEFAULT_GROQ_VISION = "meta-llama/llama-4-scout-17b-16e-instruct"


def get_crew_llm() -> LLM:
    provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if provider == "auto":
        provider = "groq" if os.getenv("GROQ_API_KEY", "").strip() else "ollama"

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Set GROQ_API_KEY in repo-root .env")
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()
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


def get_vision_llm():
    """Return (langchain chat model, label) for multimodal image calls."""
    provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if provider == "auto":
        provider = "groq" if os.getenv("GROQ_API_KEY", "").strip() else "ollama"

    if provider == "groq":
        from langchain_groq import ChatGroq

        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Set GROQ_API_KEY in repo-root .env")
        model = (
            os.getenv("GROQ_VISION_MODEL", "").strip() or DEFAULT_GROQ_VISION
        )
        return ChatGroq(model=model, temperature=0.2, api_key=api_key), f"groq:{model}"

    from langchain_ollama import ChatOllama

    model = os.getenv("OLLAMA_VISION_MODEL", "").strip() or "llava"
    return ChatOllama(model=model, temperature=0.2), f"ollama:{model}"
