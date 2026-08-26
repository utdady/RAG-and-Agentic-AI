"""Shared bootstrap for BeeAI Labs scripts."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

for p in (ROOT, HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from shared.env_load import load_env

load_env(HERE)

from beeai_framework.backend import ChatModel, ChatModelParameters


def quiet_asyncio_logs() -> None:
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)


def resolve_beeai_model_name() -> str:
    """
    Return BeeAI ChatModel.from_name slug.

    Course used watsonx:… / openai:gpt-5-nano.
    Here: groq:… when GROQ_API_KEY is set, else ollama:…
    """
    override = os.getenv("BEEAI_MODEL", "").strip()
    if override:
        return override

    provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if provider == "auto":
        provider = "groq" if os.getenv("GROQ_API_KEY", "").strip() else "ollama"

    if provider == "groq":
        if not os.getenv("GROQ_API_KEY", "").strip():
            raise RuntimeError("Set GROQ_API_KEY in repo-root .env (or LLM_PROVIDER=ollama).")
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()
        return f"groq:{model}"

    if provider == "ollama":
        model = os.getenv("OLLAMA_MODEL", "llama3.2").strip() or "llama3.2"
        return f"ollama:{model}"

    raise ValueError(f"Unknown LLM_PROVIDER={provider!r}. Use auto, groq, or ollama.")


def get_chat_model(*, temperature: float = 0) -> ChatModel:
    name = resolve_beeai_model_name()
    return ChatModel.from_name(name, ChatModelParameters(temperature=temperature))


def banner(title: str) -> None:
    print("=" * 60)
    print(title)
    print(f"BeeAI model: {resolve_beeai_model_name()}")
    print("=" * 60)


async def llm_text(llm: ChatModel, messages: list) -> str:
    """Text completion — supports older create() and newer run()."""
    if hasattr(llm, "create"):
        response = await llm.create(messages=messages)
        return response.get_text_content()
    response = await llm.run(messages)
    return response.get_text_content()


async def llm_structure(llm: ChatModel, schema, messages: list):
    """Structured output — create_structure() or run(response_format=…)."""
    if hasattr(llm, "create_structure"):
        response = await llm.create_structure(schema=schema, messages=messages)
        obj = response.object
        return obj if isinstance(obj, dict) else obj

    response = await llm.run(messages, response_format=schema)
    structured = getattr(response, "output_structured", None)
    if structured is None and hasattr(response, "object"):
        structured = response.object
    if hasattr(structured, "model_dump"):
        return structured.model_dump()
    if isinstance(structured, dict):
        return structured
    return structured
