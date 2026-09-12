"""Config for Model Comparison Chat (Groq / Ollama — no Watsonx)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.env_load import load_env

load_env(HERE)

# Generation defaults
MAX_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "512"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))

# UI slots keep lab keys; map to current Groq production ids (Llama/Gemma ids retired).
# llama  = fast
# granite = mid / alternate
# mistral = higher-quality
MODEL_SLOTS = {
    "llama": {
        "label": "Fast",
        "provider": os.getenv("LLAMA_PROVIDER", "auto"),
        "model": os.getenv("LLAMA_MODEL", "openai/gpt-oss-20b"),
        "ollama_model": os.getenv("LLAMA_OLLAMA_MODEL", "llama3.2:3b"),
    },
    "granite": {
        "label": "Balanced",
        "provider": os.getenv("GRANITE_PROVIDER", "auto"),
        "model": os.getenv("GRANITE_MODEL", "qwen/qwen3.6-27b"),
        "ollama_model": os.getenv("GRANITE_OLLAMA_MODEL", "gemma2:2b"),
    },
    "mistral": {
        "label": "Quality",
        "provider": os.getenv("MISTRAL_PROVIDER", "auto"),
        "model": os.getenv("MISTRAL_MODEL", "openai/gpt-oss-120b"),
        "ollama_model": os.getenv("MISTRAL_OLLAMA_MODEL", "mistral:7b"),
    },
}

SYSTEM_PROMPT = (
    "You are an AI assistant helping with customer inquiries. "
    "Provide a helpful and concise response."
)
