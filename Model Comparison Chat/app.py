"""Flask UI: compare LLM slots (fast / balanced / quality) with structured JSON."""

from __future__ import annotations

import time

from flask import Flask, jsonify, render_template, request

from config import MODEL_SLOTS, SYSTEM_PROMPT
from models import (
    describe_slots,
    granite_response,
    llama_response,
    mistral_response,
)

app = Flask(__name__)

HANDLERS = {
    "llama": llama_response,
    "granite": granite_response,
    "mistral": mistral_response,
}


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        model_slots={
            k: {"label": v["label"]} for k, v in MODEL_SLOTS.items()
        },
    )


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json or {}
    user_message = (data.get("message") or "").strip()
    model = (data.get("model") or "").strip()

    if not user_message or not model:
        return jsonify({"error": "Missing message or model selection"}), 400
    if model not in HANDLERS:
        return jsonify({"error": "Invalid model selection"}), 400

    start = time.time()
    try:
        result = HANDLERS[model](SYSTEM_PROMPT, user_message)
        if hasattr(result, "model_dump"):
            payload = result.model_dump()
        elif isinstance(result, dict):
            payload = result
        else:
            payload = {"summary": "", "sentiment": 50, "response": str(result)}
        payload["duration"] = time.time() - start
        payload["model"] = model
        payload["model_label"] = MODEL_SLOTS[model]["label"]
        return jsonify(payload)
    except Exception as e:
        return jsonify({"error": str(e), "duration": time.time() - start}), 500


if __name__ == "__main__":
    print("Model Comparison Chat")
    print(describe_slots())
    app.run(debug=True, host="0.0.0.0", port=5001)
