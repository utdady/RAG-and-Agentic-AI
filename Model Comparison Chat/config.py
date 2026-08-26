"""Config for Model Comparison Chat (Groq / Ollama — no Watsonx)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent

load_dotenv(HERE / ".env")
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / "Meeting Assistant" / ".env")

# Generation defaults
MAX_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "256"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))

# UI slots keep lab names; map to real Groq/Ollama model ids via env
# llama  = fast small model
# granite = mid / alternate family (Gemma on Groq, or Ollama granite)
# mistral = larger / higher-quality slot
MODEL_SLOTS = {
    "llama": {
        "label": "Llama (fast)",
        "provider": os.getenv("LLAMA_PROVIDER", "auto"),
        "model": os.getenv("LLAMA_MODEL", "llama-3.1-8b-instant"),
        "ollama_model": os.getenv("LLAMA_OLLAMA_MODEL", "llama3.2:3b"),
    },
    "granite": {
        "label": "Gemma (balanced)",
        "provider": os.getenv("GRANITE_PROVIDER", "auto"),
        "model": os.getenv("GRANITE_MODEL", "gemma2-9b-it"),
        "ollama_model": os.getenv("GRANITE_OLLAMA_MODEL", "gemma2:2b"),
    },
    "mistral": {
        "label": "Llama 70B (quality)",
        "provider": os.getenv("MISTRAL_PROVIDER", "auto"),
        "model": os.getenv("MISTRAL_MODEL", "llama-3.3-70b-versatile"),
        "ollama_model": os.getenv("MISTRAL_OLLAMA_MODEL", "mistral:7b"),
    },
}

SYSTEM_PROMPT = (
    "You are an AI assistant helping with customer inquiries. "
    "Provide a helpful and concise response."
)
