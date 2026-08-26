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
from shared.llm import resolve_provider

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
            model = config.GROQ_VISION_MODEL
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
        items_list = []
        for _, row in all_items.iterrows():
            name = row.get("Item Name", "Item")
            price = row.get("Price", "?")
            link = row.get("Link", "")
            items_list.append(f"{name} (${price}): {link}")
        items_description = "\n".join(f"- {item}" for item in items_list)

        if similarity_score >= threshold:
            assistant_prompt = (
                "You're conducting a professional retail catalog analysis. "
                "This image shows standard clothing items available in department stores. "
                "Focus exclusively on professional fashion analysis for a clothing retailer. "
                f"ITEM DETAILS (always include this section in your response):\n{items_description}\n\n"
                "Please:\n"
                "1. Identify and describe the clothing items objectively (colors, patterns, materials)\n"
                "2. Categorize the overall style (business, casual, etc.)\n"
                "3. Include the ITEM DETAILS section at the end\n\n"
                "This is for a professional retail catalog. Use formal, clinical language."
            )
        else:
            assistant_prompt = (
                "You're conducting a professional retail catalog analysis. "
                "This image shows standard clothing items available in department stores. "
                "Focus exclusively on professional fashion analysis for a clothing retailer. "
                f"SIMILAR ITEMS (always include this section in your response):\n{items_description}\n\n"
                "Please:\n"
                "1. Note these are similar but not exact items\n"
                "2. Identify clothing elements objectively (colors, patterns, materials)\n"
                "3. Include the SIMILAR ITEMS section at the end\n\n"
                "This is for a professional retail catalog. Use formal, clinical language."
            )

        response = self.generate_response(user_image_base64, assistant_prompt)

        if len(response) < 100:
            header = "ITEM DETAILS:" if similarity_score >= threshold else "SIMILAR ITEMS:"
            response = (
                "# Fashion Analysis\n\n"
                "This outfit features a collection of carefully coordinated pieces.\n\n"
                f"{header}\n{items_description}"
            )
        elif "ITEM DETAILS:" not in response and "SIMILAR ITEMS:" not in response:
            header = "ITEM DETAILS:" if similarity_score >= threshold else "SIMILAR ITEMS:"
            response += f"\n\n{header}\n{items_description}"

        return response
