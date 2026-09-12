"""
Multi-model chat helpers with structured JSON output.

UI slots: llama | granite | mistral (lab names) → Groq/Ollama backends via env.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, ValidationError

from config import MAX_TOKENS, MODEL_SLOTS, SYSTEM_PROMPT, TEMPERATURE
from shared.llm import GROQ_MODEL_ALIASES, pick_ollama_model, resolve_provider
from shared.strip_thinking import strip_model_thinking

_JSON_OBJ_RE = re.compile(r"\{[\s\S]*\}")


class AIResponse(BaseModel):
    summary: str = Field(description="Summary of the user's message")
    sentiment: int = Field(
        description="Sentiment score from 0 (negative) to 100 (positive)"
    )
    response: str = Field(description="Suggested response to the user")


FORMAT_HINT = (
    'Return ONLY a JSON object with keys "summary" (string), '
    '"sentiment" (integer 0-100), and "response" (string). '
    "No markdown fences, no commentary."
)


def _resolve_slot_groq_model(raw: str) -> str:
    model = (raw or "").strip()
    return GROQ_MODEL_ALIASES.get(model, model)


def _message_text(content: object) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text") or ""))
            else:
                text = getattr(block, "text", None)
                if text:
                    parts.append(str(text))
        return "".join(parts)
    return str(content)


def _parse_ai_response(text: str) -> dict:
    cleaned = strip_model_thinking(text).strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    candidates = [cleaned]
    match = _JSON_OBJ_RE.search(cleaned)
    if match:
        candidates.append(match.group(0))
    last_err: Exception | None = None
    for cand in candidates:
        try:
            data = json.loads(cand)
            return AIResponse.model_validate(data).model_dump()
        except (json.JSONDecodeError, ValidationError) as exc:
            last_err = exc
            continue
    raise ValueError(
        f"Could not parse structured JSON from model output ({last_err})."
    )


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
            provider = "ollama"
        else:
            from langchain_groq import ChatGroq

            model = _resolve_slot_groq_model(slot["model"])
            lower = model.lower()
            kwargs: dict = {
                "model": model,
                "temperature": TEMPERATURE,
                "api_key": api_key,
                "max_tokens": max(MAX_TOKENS, 512),
            }
            model_kwargs: dict = {
                "response_format": {"type": "json_object"},
            }
            if "qwen" in lower:
                kwargs["reasoning_effort"] = "none"
                kwargs["reasoning_format"] = "hidden"
            if "gpt-oss" in lower:
                # gpt-oss ignores reasoning_format; hide reasoning so content is JSON-only.
                model_kwargs["include_reasoning"] = False
                kwargs["reasoning_effort"] = "low"
            kwargs["model_kwargs"] = model_kwargs
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
    system = (system_prompt or SYSTEM_PROMPT).strip() + "\n\n" + FORMAT_HINT
    out = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(content=user_prompt),
        ]
    )
    return _parse_ai_response(_message_text(getattr(out, "content", out)))


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
