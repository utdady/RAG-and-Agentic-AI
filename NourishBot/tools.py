"""CrewAI tools for ingredient extraction, filtering, and nutrient analysis."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

from crewai.tools import tool

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from vision import analyze_nutrition_from_image, extract_ingredients_from_image


@tool("Extract ingredients")
def extract_ingredients(image_input: str) -> str:
    """
    Extract ingredients from a food item image.

    Args:
        image_input: Local image file path or http(s) URL.
    """
    return extract_ingredients_from_image(image_input)


@tool("Filter ingredients")
def filter_ingredients(raw_ingredients: str) -> List[str]:
    """
    Clean raw ingredient text into a list of food items.

    Args:
        raw_ingredients: Raw ingredients as a comma- or newline-separated string.
    """
    text = (raw_ingredients or "").replace("\n", ",")
    return [
        ingredient.strip().lower()
        for ingredient in text.split(",")
        if ingredient.strip()
    ]


@tool("Filter based on dietary restrictions")
def filter_based_on_restrictions(
    ingredients: str, dietary_restrictions: Optional[str] = None
) -> List[str]:
    """
    Filter ingredients for dietary restrictions using a text LLM.

    Args:
        ingredients: Comma-separated ingredient list.
        dietary_restrictions: e.g. vegan, gluten-free, keto. Empty = keep all.
    """
    items = [
        i.strip().lower()
        for i in (ingredients or "").replace("\n", ",").split(",")
        if i.strip()
    ]
    if not dietary_restrictions or not str(dietary_restrictions).strip():
        return items

    from shared.llm import get_chat_llm

    llm = get_chat_llm(temperature=0.1)
    prompt = (
        "You are an AI nutritionist specialized in dietary restrictions.\n"
        f"Ingredients: {', '.join(items)}\n"
        f"Dietary restriction: {dietary_restrictions}\n"
        "Remove any ingredient that does not comply. "
        "Return only the compliant ingredients as a comma-separated list "
        "with no additional commentary."
    )
    out = llm.invoke(prompt)
    filtered = getattr(out, "content", str(out)).strip().lower()
    return [item.strip() for item in filtered.split(",") if item.strip()]


@tool("Analyze nutritional values and calories of the dish from uploaded image")
def analyze_image(image_input: str) -> str:
    """
    Nutrient breakdown and calorie estimate from a food image.

    Args:
        image_input: Local image file path or http(s) URL.
    """
    return analyze_nutrition_from_image(image_input)
