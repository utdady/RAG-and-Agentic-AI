"""Shared utilities for RAG and Agentic AI projects."""

from shared.embeddings import get_embedding_model, resolve_embedding_model
from shared.llama_index_llm import describe_llama_index_llm, get_llama_index_llm
from shared.llm import (
    describe_setup,
    detect_hardware_tier,
    get_chat_llm,
    get_llm_info,
    resolve_whisper_model,
)

__all__ = [
    "describe_llama_index_llm",
    "describe_setup",
    "detect_hardware_tier",
    "get_chat_llm",
    "get_embedding_model",
    "get_llama_index_llm",
    "get_llm_info",
    "resolve_embedding_model",
    "resolve_whisper_model",
]
