"""
LlamaIndex LLM factory — same env contract as shared.llm (Groq / Ollama / auto).
"""

from __future__ import annotations

import os

from shared.llm import (
    DEFAULT_GROQ_MODEL,
    detect_hardware_tier,
    pick_ollama_model,
    resolve_groq_model,
    resolve_provider,
)


def get_llama_index_llm(temperature: float = 0.3):
    """
    Return a LlamaIndex LLM (Groq or Ollama).

    Env: LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL, OLLAMA_MODEL, HARDWARE_TIER
    """
    provider = resolve_provider()
    tier = detect_hardware_tier()

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "LLM_PROVIDER=groq but GROQ_API_KEY is not set. "
                "Add it to .env or use LLM_PROVIDER=ollama."
            )
        from llama_index.llms.groq import Groq

        model = resolve_groq_model()
        return Groq(model=model, api_key=api_key, temperature=temperature)

    from llama_index.llms.ollama import Ollama

    model = pick_ollama_model(tier)
    return Ollama(model=model, temperature=temperature, request_timeout=120.0)


def describe_llama_index_llm() -> str:
    provider = resolve_provider()
    tier = detect_hardware_tier()
    if provider == "groq":
        model = resolve_groq_model()
    else:
        model = pick_ollama_model(tier)
    return f"LlamaIndex LLM={provider}:{model} (tier={tier})"
