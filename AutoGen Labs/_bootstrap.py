"""Shared bootstrap for AutoGen / AG2 Labs scripts."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

for p in (ROOT, HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from shared.env_load import load_env

load_env(HERE)

# Suppress noisy API-key format warnings from OpenAI client helpers
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
    """
    AG2 config_list entry.

    Course used OpenAI gpt-4o-mini (key from env).
    Here: Groq (api_type=groq) or Ollama OpenAI-compatible endpoint.
    """
    provider = resolve_provider()

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Set GROQ_API_KEY in repo-root .env (or LLM_PROVIDER=ollama).")
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()
        return [
            {
                "model": model,
                "api_key": api_key,
                "api_type": "groq",
            }
        ]

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


def banner(title: str) -> None:
    provider = resolve_provider()
    entry = get_config_list()[0]
    print("=" * 60)
    print(title)
    print(f"AG2 provider={provider} model={entry.get('model')}")
    print("=" * 60)
