"""Configuration for Style Finder."""

from __future__ import annotations

import os
from pathlib import Path

from shared.llm import resolve_groq_vision_model

HERE = Path(__file__).resolve().parent

IMAGE_SIZE = (224, 224)
NORMALIZATION_MEAN = [0.485, 0.456, 0.406]
NORMALIZATION_STD = [0.229, 0.224, 0.225]

SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.8"))
DEFAULT_ALTERNATIVES_COUNT = 5

DATA_DIR = HERE / "data"
EMBEDDINGS_PATH = DATA_DIR / "swift-style-embeddings.pkl"
EMBEDDINGS_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "95eJ0YJVtqTZhEd7RaUlew/processed-swift-style-with-embeddings.pkl"
)

# Vision model overrides (repo-root .env) — deprecated Groq ids are aliased in shared/llm.py
GROQ_VISION_MODEL = resolve_groq_vision_model()
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava").strip() or "llava"
