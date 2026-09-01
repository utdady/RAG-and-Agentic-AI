"""Vision LLM fashion analysis (Groq / Ollama — not Watsonx)."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from langchain_core.messages import HumanMessage

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config
from helpers import has_items_section, strip_model_thinking
from shared.llm import (
    DEFAULT_GROQ_VISION_MODEL,
    resolve_groq_vision_model,
    resolve_provider,
)

logger = logging.getLogger(__name__)


class VisionFashionService:
    def __init__(self, temperature: float = 0.2):
        self.temperature = temperature
        self.llm, self.label = self._make_llm()

    def _make_llm(self):
        provider = resolve_provider()
        if provider == "groq":
            from langchain_groq import ChatGroq

            api_key = os.getenv("GROQ_API_KEY", "").strip()
            if not api_key:
                raise RuntimeError("GROQ_API_KEY required for Groq vision.")
            model = resolve_groq_vision_model()
            lower = model.lower()
            if (
                "llama-4-scout" in lower
                or "vision-preview" in lower
                or "llava-v1.5" in lower
            ):
                model = DEFAULT_GROQ_VISION_MODEL
            return ChatGroq(
                model=model, temperature=self.temperature, api_key=api_key
            ), f"groq:{model}"
        from langchain_ollama import ChatOllama

        model = config.OLLAMA_VISION_MODEL
        return ChatOllama(model=model, temperature=self.temperature), f"ollama:{model}"

    def generate_response(self, encoded_image: str, prompt: str) -> str:
        try:
            logger.info("Vision LLM request (%s), prompt_len=%d", self.label, len(prompt))
            msg = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/jpeg;base64," + encoded_image
                        },
                    },
                ]
            )
            out = self.llm.invoke([msg])
            content = getattr(out, "content", str(out))
            content = strip_model_thinking(content)
            logger.info("Vision LLM response_len=%d", len(content))
            return content
        except Exception as e:
            logger.error("Error generating response: %s", e)
            return f"Error generating response: {e}"

    def generate_fashion_response(
        self,
        user_image_base64: str,
        matched_row,
        all_items,
        similarity_score: float,
        threshold: float = 0.8,
    ) -> str:
        match_note = (
            "The closest catalog match is a strong visual match."
            if similarity_score >= threshold
            else "The closest catalog match is only loosely similar — focus on what you see in the photo."
        )
        assistant_prompt = (
            "You are writing a professional retail catalog analysis of the clothing in this image.\n\n"
            f"{match_note}\n\n"
            "Describe objectively:\n"
            "1. Garment types, colors, patterns, and materials\n"
            "2. Overall style category (e.g. business, casual, athleisure)\n"
            "3. Fit and construction details you can see\n\n"
            "Use formal, clinical language. Do not include product links, prices, or catalog listings — "
            "those are shown separately. Output only the final analysis with no reasoning or thinking tags."
        )

        response = self.generate_response(user_image_base64, assistant_prompt)

        if len(response) < 100 and not has_items_section(response):
            response = (
                "## Fashion Analysis\n\n"
                "This outfit features coordinated pieces suitable for everyday wear. "
                "See the catalog match below for related items."
            )

        return response
