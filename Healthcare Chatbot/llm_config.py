"""AG2 llm_config helper (Groq / Ollama)."""

from __future__ import annotations

import logging
import os
from typing import Any

logging.getLogger("autogen.oai.client").setLevel(logging.ERROR)


def resolve_provider() -> str:
    provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if provider == "auto":
        return "groq" if os.getenv("GROQ_API_KEY", "").strip() else "ollama"
    if provider not in {"groq", "ollama"}:
        raise ValueError(
            f"Unknown LLM_PROVIDER={provider!r}. Use auto, groq, or ollama."
        )
    return provider


def get_config_list() -> list[dict[str, Any]]:
    provider = resolve_provider()
    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Set GROQ_API_KEY in repo-root .env (or LLM_PROVIDER=ollama).")
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()
        return [{"model": model, "api_key": api_key, "api_type": "groq"}]

    model = os.getenv("OLLAMA_MODEL", "llama3.2").strip() or "llama3.2"
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    if not base.endswith("/v1"):
        base = f"{base}/v1"
    return [
        {
            "model": model,
            "api_key": os.getenv("OLLAMA_API_KEY", "ollama"),
            "base_url": base,
            "api_type": "openai",
        }
    ]


def get_llm_config(**extra: Any) -> dict[str, Any]:
    cfg: dict[str, Any] = {"config_list": get_config_list()}
    cfg.update(extra)
    return cfg
