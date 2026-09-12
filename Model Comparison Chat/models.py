"""
Multi-model chat helpers with structured JSON output.

UI slots: llama | granite | mistral (lab names) → Groq/Ollama backends via env.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from config import MAX_TOKENS, MODEL_SLOTS, SYSTEM_PROMPT, TEMPERATURE
from shared.llm import GROQ_MODEL_ALIASES, pick_ollama_model, resolve_provider


class AIResponse(BaseModel):
    summary: str = Field(description="Summary of the user's message")
    sentiment: int = Field(
        description="Sentiment score from 0 (negative) to 100 (positive)"
    )
    response: str = Field(description="Suggested response to the user")


json_parser = JsonOutputParser(pydantic_object=AIResponse)

# Simple chat-style prompt (works across Groq / Ollama backends)
PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "{system_prompt}\n\nRespond ONLY with valid JSON matching this schema:\n"
            "{format_prompt}",
        ),
        ("human", "{user_prompt}"),
    ]
)


def _resolve_slot_groq_model(raw: str) -> str:
    model = (raw or "").strip()
    return GROQ_MODEL_ALIASES.get(model, model)


def _make_llm(slot_key: str):
    slot = MODEL_SLOTS[slot_key]
    slot_provider = (slot.get("provider") or "auto").strip().lower()
    if slot_provider == "auto":
        provider = resolve_provider()
    else:
        provider = slot_provider

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            # Fall back to Ollama for this slot
            provider = "ollama"
        else:
            from langchain_groq import ChatGroq

            model = _resolve_slot_groq_model(slot["model"])
            kwargs: dict = {
                "model": model,
                "temperature": TEMPERATURE,
                "api_key": api_key,
                "max_tokens": MAX_TOKENS,
            }
            # Qwen thinking burns the completion budget before JSON lands.
            if "qwen" in model.lower():
                kwargs["reasoning_effort"] = "none"
                kwargs["reasoning_format"] = "hidden"
            return ChatGroq(**kwargs)

    from langchain_ollama import ChatOllama

    ollama_name = slot.get("ollama_model") or pick_ollama_model()
    return ChatOllama(model=ollama_name, temperature=TEMPERATURE)


_llms: dict = {}


def get_llm(slot_key: str):
    if slot_key not in _llms:
        if slot_key not in MODEL_SLOTS:
            raise ValueError(f"Unknown model slot: {slot_key}")
        _llms[slot_key] = _make_llm(slot_key)
    return _llms[slot_key]


def get_ai_response(slot_key: str, system_prompt: str, user_prompt: str) -> dict:
    llm = get_llm(slot_key)
    chain = PROMPT | llm | json_parser
    return chain.invoke(
        {
            "system_prompt": system_prompt or SYSTEM_PROMPT,
            "user_prompt": user_prompt,
            "format_prompt": json_parser.get_format_instructions(),
        }
    )


def llama_response(system_prompt: str, user_prompt: str) -> dict:
    return get_ai_response("llama", system_prompt, user_prompt)


def granite_response(system_prompt: str, user_prompt: str) -> dict:
    return get_ai_response("granite", system_prompt, user_prompt)


def mistral_response(system_prompt: str, user_prompt: str) -> dict:
    return get_ai_response("mistral", system_prompt, user_prompt)


def describe_slots() -> str:
    lines = []
    for key, slot in MODEL_SLOTS.items():
        lines.append(
            f"  {key}: groq={slot['model']} | ollama={slot['ollama_model']} "
            f"({slot['label']})"
        )
    return "\n".join(lines)
