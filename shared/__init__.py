"""Shared utilities for RAG and Agentic AI projects."""

from shared.llm import (
    describe_setup,
    detect_hardware_tier,
    get_chat_llm,
    get_llm_info,
    resolve_whisper_model,
)

__all__ = [
    "describe_setup",
    "detect_hardware_tier",
    "get_chat_llm",
    "get_llm_info",
    "resolve_whisper_model",
]
