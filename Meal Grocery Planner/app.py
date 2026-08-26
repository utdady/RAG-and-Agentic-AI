"""
Structured Meal & Grocery Planner — Gradio + CrewAI.

Sequential crew: meal plan → shopping list → budget → leftovers → (nutrition) → summary.
Watsonx → Groq/Ollama; Serper via SERPER_API_KEY in .env.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import gradio as gr

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# CrewBase YAML paths resolve relative to CWD
os.chdir(HERE)

from shared.env_load import load_env

load_env(HERE)

from crew_app import run_planner
from llm_config import get_crew_llm


def plan(
    meal_name: str,
    servings: float,
    budget: str,
    dietary_restrictions: str,
    cooking_skill: str,
    include_nutrition: bool,
):
    meal_name = (meal_name or "").strip()
    if not meal_name:
        return "Enter a meal name."
    try:
        get_crew_llm()  # fail fast if misconfigured
        return run_planner(
            meal_name=meal_name,
            servings=int(servings),
            budget=(budget or "$25").strip(),
            dietary_restrictions=dietary_restrictions or "",
            cooking_skill=cooking_skill or "beginner",
            include_nutrition=bool(include_nutrition),
        )
    except Exception as e:
        return f"Error: {e}"


def build_ui():
    with gr.Blocks(title="Meal & Grocery Planner") as demo:
        gr.Markdown("# Structured Meal & Grocery Planner")
        gr.Markdown(
            "CrewAI multi-agent planner: **recipe research → shopping list → "
            "budget → leftovers → optional nutrition → summary**.  \n"
            "Needs `GROQ_API_KEY` (or Ollama) and `SERPER_API_KEY` in repo-root `.env`.  \n"
            "Educational only — not medical or dietary advice."
        )
        with gr.Row():
            meal_name = gr.Textbox(label="Meal name", value="Chicken Stir Fry")
            servings = gr.Number(label="Servings", value=4, precision=0)
        with gr.Row():
            budget = gr.Textbox(label="Budget", value="$25")
            cooking_skill = gr.Dropdown(
                ["beginner", "intermediate", "advanced"],
                value="beginner",
                label="Cooking skill",
            )
        dietary = gr.Textbox(
            label="Dietary restrictions (comma-separated)",
            value="no nuts",
            placeholder="vegetarian, low sodium, …",
        )
        include_nutrition = gr.Checkbox(label="Include nutrition analyst", value=True)
        go = gr.Button("Plan meal & groceries", variant="primary")
        out = gr.Markdown(label="Result")
        go.click(
            plan,
            inputs=[
                meal_name,
                servings,
                budget,
                dietary,
                cooking_skill,
                include_nutrition,
            ],
            outputs=out,
        )
        gr.Examples(
            examples=[
                ["Chicken Stir Fry", 4, "$25", "no nuts", "beginner", True],
                ["Quinoa Buddha Bowl", 2, "$20", "vegetarian, high protein", "intermediate", True],
            ],
            inputs=[
                meal_name,
                servings,
                budget,
                dietary,
                cooking_skill,
                include_nutrition,
            ],
        )
    return demo


if __name__ == "__main__":
    demo = build_ui()
    host = os.getenv("GRADIO_HOST", "127.0.0.1")
    port = int(os.getenv("GRADIO_PORT", "7868"))
    demo.launch(server_name=host, server_port=port, share=False)
