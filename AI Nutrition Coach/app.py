"""
AI Nutrition Coach — Flask
Upload a meal photo → vision LLM nutritional assessment (Groq / Ollama).
"""

from __future__ import annotations

import base64
import os
import re
import sys
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from langchain_core.messages import HumanMessage

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.env_load import load_env

load_env(HERE)

from shared.llm import resolve_provider

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "nutrition-coach-dev-key")

DEFAULT_GROQ_VISION = "meta-llama/llama-4-scout-17b-16e-instruct"

ASSISTANT_PROMPT = """
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


def get_vision_llm():
    provider = resolve_provider()
    if provider == "groq":
        from langchain_groq import ChatGroq

        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in repo-root .env")
        model = (
            os.getenv("GROQ_VISION_MODEL", "").strip() or DEFAULT_GROQ_VISION
        )
        return ChatGroq(model=model, temperature=0.2, api_key=api_key), f"groq:{model}"

    from langchain_ollama import ChatOllama

    model = os.getenv("OLLAMA_VISION_MODEL", "").strip() or "llava"
    return ChatOllama(model=model, temperature=0.2), f"ollama:{model}"


def input_image_setup(uploaded_file) -> str:
    if uploaded_file is None or not uploaded_file.filename:
        raise FileNotFoundError("No file uploaded")
    bytes_data = uploaded_file.read()
    if not bytes_data:
        raise FileNotFoundError("Empty upload")
    return base64.b64encode(bytes_data).decode("utf-8")


def format_response(response_text: str) -> str:
    response_text = re.sub(
        r"\*\*(.*?)\*\*", r"<p><strong>\1</strong></p>", response_text
    )
    response_text = re.sub(r"(?m)^\s*\*\s(.*)", r"<li>\1</li>", response_text)
    response_text = re.sub(
        r"(<li>.*?</li>)+",
        lambda match: f"<ul>{match.group(0)}</ul>",
        response_text,
        flags=re.DOTALL,
    )
    response_text = re.sub(r"</p>(?=<p>)", r"</p><br>", response_text)
    response_text = re.sub(r"(\n|\\n)+", r"<br>", response_text)
    return response_text


def generate_model_response(
    encoded_image: str, user_query: str, assistant_prompt: str
) -> str:
    try:
        llm, label = get_vision_llm()
        msg = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": assistant_prompt + "\n\n" + user_query,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/jpeg;base64," + encoded_image
                    },
                },
            ]
        )
        out = llm.invoke([msg])
        raw = getattr(out, "content", str(out))
        return f"<p><em>Model: {label}</em></p>" + format_response(raw)
    except Exception as e:
        print(f"Error in generating response: {e}")
        return f"<p>An error occurred while generating the response: {e}</p>"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_query = (
            request.form.get("user_query")
            or "How many calories are in this food?"
        ).strip()
        uploaded_file = request.files.get("file")

        if uploaded_file and uploaded_file.filename:
            try:
                encoded_image = input_image_setup(uploaded_file)
            except Exception:
                flash("Error processing the image. Please try again.", "danger")
                return redirect(url_for("index"))

            response = generate_model_response(
                encoded_image, user_query, ASSISTANT_PROMPT
            )
            return render_template(
                "index.html", user_query=user_query, response=response
            )

        flash("Please upload an image file.", "danger")
        return redirect(url_for("index"))

    return render_template("index.html")


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5002"))
    app.run(host=host, port=port, debug=False)
