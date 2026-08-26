"""Multimodal vision helpers (image path / URL → model text)."""

from __future__ import annotations

import base64
from pathlib import Path

import requests
from langchain_core.messages import HumanMessage

from llm_config import get_vision_llm

NUTRIENT_PROMPT = """
You are an expert nutritionist. Your task is to analyze the food items displayed in the image and provide a detailed nutritional assessment using the following format:
1. **Identification**: List each identified food item clearly, one per line.
2. **Portion Size & Calorie Estimation**: For each identified food item, specify the portion size and provide an estimated number of calories. Use bullet points with the following structure:
- **[Food Item]**: [Portion Size], [Number of Calories] calories
Example:
*   **Salmon**: 6 ounces, 210 calories
*   **Asparagus**: 3 spears, 25 calories
3. **Total Calories**: Provide the total number of calories for all food items.
Example:
Total Calories: [Number of Calories]
4. **Nutrient Breakdown**: Include a breakdown of key nutrients such as **Protein**, **Carbohydrates**, **Fats**, **Vitamins**, and **Minerals**. Use bullet points, and for each nutrient provide details about the contribution of each food item.
Example:
*   **Protein**: Salmon (35g), Asparagus (3g), Tomatoes (1g) = [Total Protein]
5. **Health Evaluation**: Evaluate the healthiness of the meal in one paragraph.
6. **Disclaimer**: Include the following exact text as a disclaimer:
The nutritional information and calorie estimates provided are approximate and are based on general food data.
Actual values may vary depending on factors such as portion size, specific ingredients, preparation methods, and individual variations.
For precise dietary advice or medical guidance, consult a qualified nutritionist or healthcare provider.
Format your response exactly like the template above to ensure consistency.
"""


def load_image_b64(image_input: str) -> str:
    image_input = (image_input or "").strip().strip('"').strip("'")
    if image_input.startswith("http://") or image_input.startswith("https://"):
        response = requests.get(image_input, timeout=60)
        response.raise_for_status()
        data = response.content
    else:
        path = Path(image_input)
        if not path.is_file():
            raise FileNotFoundError(f"No file found at path: {image_input}")
        data = path.read_bytes()
    if not data:
        raise ValueError("Empty image data")
    return base64.b64encode(data).decode("utf-8")


def vision_chat(encoded_image: str, text: str) -> str:
    llm, _label = get_vision_llm()
    msg = HumanMessage(
        content=[
            {"type": "text", "text": text},
            {
                "type": "image_url",
                "image_url": {"url": "data:image/jpeg;base64," + encoded_image},
            },
        ]
    )
    out = llm.invoke([msg])
    return getattr(out, "content", str(out))


def extract_ingredients_from_image(image_input: str) -> str:
    encoded = load_image_b64(image_input)
    return vision_chat(
        encoded,
        "Extract ingredients from the food item image. "
        "Return a comma-separated list of ingredients only.",
    )


def analyze_nutrition_from_image(image_input: str) -> str:
    encoded = load_image_b64(image_input)
    return vision_chat(encoded, NUTRIENT_PROMPT)
