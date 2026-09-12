"""
AI Nutrition Coach — Flask
Upload a meal photo → vision LLM nutritional assessment (Groq / Ollama).
"""

from __future__ import annotations

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

from shared.llm import get_groq_vision_chat, resolve_provider
from shared.strip_thinking import strip_model_thinking
from shared.vision_image import encode_image_for_vision

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "nutrition-coach-dev-key")

ASSISTANT_PROMPT = """
You are an expert nutritionist. Analyze the food in the image and write a concise nutritional assessment.

Rules:
- Output ONLY the final assessment — no chain-of-thought, no <think> tags, no scratch work.
- Use Markdown (headings and bullets). Do not use HTML tags.
- Keep the whole answer under ~350 words.

Use this structure:

## Identification
List each food item, one per line.

## Portion size & calories
- **Item**: portion, N calories

## Total calories
Total Calories: N

## Nutrient breakdown
- **Protein**: …
- **Carbohydrates**: …
- **Fats**: …
- **Vitamins / minerals**: brief notes

## Health evaluation
One short paragraph.

## Disclaimer
The nutritional information and calorie estimates provided are approximate and are based on general food data. Actual values may vary depending on factors such as portion size, specific ingredients, preparation methods, and individual variations. For precise dietary advice or medical guidance, consult a qualified nutritionist or healthcare provider.
"""


def get_vision_llm():
    provider = resolve_provider()
    if provider == "groq":
        return get_groq_vision_chat(temperature=0.2)

    from langchain_ollama import ChatOllama

    model = os.getenv("OLLAMA_VISION_MODEL", "").strip() or "llava"
    return ChatOllama(model=model, temperature=0.2), f"ollama:{model}"


def input_image_setup(uploaded_file) -> str:
    if uploaded_file is None or not uploaded_file.filename:
        raise FileNotFoundError("No file uploaded")
    bytes_data = uploaded_file.read()
    if not bytes_data:
        raise FileNotFoundError("Empty upload")
    return encode_image_for_vision(bytes_data)


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


def format_response_html(response_text: str) -> str:
    response_text = re.sub(
        r"\*\*(.*?)\*\*", r"<p><strong>\1</strong></p>", response_text
    )
    response_text = re.sub(r"(?m)^\s*\*\s(.*)", r"<li>\1</li>", response_text)
    response_text = re.sub(
        r"(?m)^-\s+\*\*(.*?)\*\*:?(.*)$",
        r"<li><strong>\1</strong>\2</li>",
        response_text,
    )
    response_text = re.sub(r"(?m)^-\s+(.*)$", r"<li>\1</li>", response_text)
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
    encoded_image: str,
    user_query: str,
    assistant_prompt: str,
    *,
    as_html: bool = True,
) -> str:
    try:
        llm, label = get_vision_llm()
        msg = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": assistant_prompt + "\n\nUser question: " + user_query,
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
        raw = strip_model_thinking(_message_text(getattr(out, "content", out)))
        if not raw:
            raw = (
                "I couldn't produce a clean nutrition write-up for this image. "
                "Please try again with a clearer meal photo."
            )
        if as_html:
            return f"<p><em>Model: {label}</em></p>" + format_response_html(raw)
        return f"_Model: {label}_\n\n{raw}"
    except Exception as e:
        print(f"Error in generating response: {e}")
        if as_html:
            return f"<p>An error occurred while generating the response: {e}</p>"
        return f"An error occurred while generating the response: {e}"


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
                encoded_image, user_query, ASSISTANT_PROMPT, as_html=True
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
