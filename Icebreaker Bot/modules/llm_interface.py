"""LLM / embedding factories — Groq or Ollama + local MiniLM (not Watsonx/Slate)."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config
from shared.llama_index_llm import describe_llama_index_llm, get_llama_index_llm
from shared.llm import DEFAULT_GROQ_MODEL, resolve_provider

logger = logging.getLogger(__name__)


def create_embedding_model():
    """Local HuggingFace embeddings for LlamaIndex."""
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    model = HuggingFaceEmbedding(model_name=config.EMBEDDING_MODEL)
    logger.info("Embedding model: %s", config.EMBEDDING_MODEL)
    return model


def create_llm(temperature: float | None = None):
    """LlamaIndex chat LLM (respects config.LLM_MODEL_OVERRIDE when set)."""
    temp = config.TEMPERATURE if temperature is None else temperature
    if config.LLM_MODEL_OVERRIDE:
        provider = resolve_provider()
        if provider == "groq":
            os.environ["GROQ_MODEL"] = config.LLM_MODEL_OVERRIDE
        else:
            os.environ["OLLAMA_MODEL"] = config.LLM_MODEL_OVERRIDE
    llm = get_llama_index_llm(temperature=temp)
    logger.info(describe_llama_index_llm())
    return llm


def change_llm_model(new_model_id: str) -> None:
    """Set a runtime model override for subsequent create_llm() calls."""
    config.LLM_MODEL_OVERRIDE = (new_model_id or "").strip() or None
    logger.info("LLM model override: %s", config.LLM_MODEL_OVERRIDE or "(env default)")


def available_models() -> list[str]:
    """Dropdown choices for Gradio (provider-aware)."""
    provider = resolve_provider()
    if provider == "groq":
        current = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip() or DEFAULT_GROQ_MODEL
        opts = [
            current,
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768",
        ]
        # dedupe preserving order
        seen: set[str] = set()
        return [m for m in opts if not (m in seen or seen.add(m))]
    # Ollama — suggest common local tags; env/override still wins
    return [
        os.getenv("OLLAMA_MODEL", "").strip() or "llama3.2:3b",
        "llama3.2:3b",
        "llama3.1:8b",
        "mistral:7b",
    ]
