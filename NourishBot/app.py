"""
NourishBot — Gradio + CrewAI multimodal nutrition coach.

Workflows:
  recipe   — detect ingredients → dietary filter → recipe ideas
  analysis — nutrient / calorie breakdown from a dish photo

Watsonx multimodal → Groq vision / Ollama LLaVA; text agents via Groq/Ollama.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import gradio as gr
import requests

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

os.chdir(HERE)

from shared.env_load import load_env

load_env(HERE)

from crew_app import run_analysis, run_recipe
from llm_config import get_crew_llm, get_vision_llm

UPLOADS = HERE / "uploads"
EXAMPLES = HERE / "examples"

EXAMPLE_URLS = [
    (
        "food-1.png",
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
        "5uo16pKhdB1f2Vz7H8Utkg/image-1.png",
    ),
    (
        "food-2.png",
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
        "fsuegY1q_OxKIxNhf6zeYg/image-2.png",
    ),
    (
        "food-3.png",
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
        "KCh_pM9BVWq_ZdzIBIA9Fw/image-3.png",
    ),
    (
        "food-4.png",
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
        "VaaYLw52RaykwrE3jpFv7g/image-4.png",
    ),
]


def ensure_examples() -> list[str]:
    EXAMPLES.mkdir(parents=True, exist_ok=True)
    paths: list[str] = []
    for name, url in EXAMPLE_URLS:
        dest = EXAMPLES / name
        if not dest.exists() or dest.stat().st_size == 0:
            try:
                r = requests.get(url, timeout=60)
                r.raise_for_status()
                dest.write_bytes(r.content)
            except Exception as e:
                print(f"Could not download {name}: {e}")
                continue
        paths.append(str(dest))
    return paths


def format_recipe_output(final_output: dict) -> str:
    output = "## Recipe Ideas\n\n"
    recipes = final_output.get("recipes") or []
    if not recipes and "raw" in final_output:
        return output + str(final_output["raw"])

    if not recipes:
        return output + "No recipes could be generated."

    for idx, recipe in enumerate(recipes, 1):
        if hasattr(recipe, "model_dump"):
            recipe = recipe.model_dump()
        title = recipe.get("title", f"Recipe {idx}")
        output += f"### {idx}. {title}\n\n"
        output += "**Ingredients:**\n\n"
        for ingredient in recipe.get("ingredients") or []:
            output += f"- {ingredient}\n"
        output += f"\n**Instructions:**\n\n{recipe.get('instructions', '')}\n\n"
        output += f"**Calorie Estimate:** {recipe.get('calorie_estimate', 'n/a')} kcal\n\n"
        output += "---\n\n"
    return output


def format_analysis_output(final_output: dict) -> str:
    if "raw" in final_output and len(final_output) == 1:
        return "## Nutritional Analysis\n\n" + str(final_output["raw"])

    output = "## Nutritional Analysis\n\n"
    if dish := final_output.get("dish"):
        output += f"**Dish:** {dish}\n\n"
    if portion := final_output.get("portion_size"):
        output += f"**Portion Size:** {portion}\n\n"
    if est_cal := final_output.get("estimated_calories"):
        output += f"**Estimated Calories:** {est_cal} calories\n\n"

    nutrients = final_output.get("nutrients") or {}
    if hasattr(nutrients, "model_dump"):
        nutrients = nutrients.model_dump()

    output += "**Nutrient Breakdown:**\n\n"
    for macro in ["protein", "carbohydrates", "fats"]:
        if value := nutrients.get(macro):
            output += f"- **{macro.capitalize()}:** {value}\n"

    vitamins = nutrients.get("vitamins") or []
    if vitamins:
        output += "\n**Vitamins:**\n\n"
        for v in vitamins:
            if hasattr(v, "model_dump"):
                v = v.model_dump()
            output += f"- {v.get('name', 'N/A')}: {v.get('percentage_dv', 'N/A')}\n"

    minerals = nutrients.get("minerals") or []
    if minerals:
        output += "\n**Minerals:**\n\n"
        for m in minerals:
            if hasattr(m, "model_dump"):
                m = m.model_dump()
            output += f"- {m.get('name', 'N/A')}: {m.get('amount', 'N/A')}\n"

    if health_eval := final_output.get("health_evaluation"):
        output += f"\n**Health Evaluation:**\n\n{health_eval}\n"

    output += (
        "\n---\n*Estimates only. Not medical advice — consult a qualified "
        "nutritionist or healthcare provider for personalized guidance.*\n"
    )
    return output


def analyze_food(image, dietary_restrictions, workflow_type):
    if image is None:
        return "Upload an image first."

    try:
        get_crew_llm()
        get_vision_llm()
    except Exception as e:
        return f"LLM config error: {e}"

    UPLOADS.mkdir(parents=True, exist_ok=True)
    image_path = str(UPLOADS / "uploaded_image.jpg")
    try:
        image.save(image_path)
    except Exception:
        # Gradio may pass a path string in some versions
        from PIL import Image as PILImage

        if isinstance(image, (str, Path)):
            PILImage.open(image).convert("RGB").save(image_path)
        else:
            return "Could not save uploaded image."

    dietary = (dietary_restrictions or "").strip()
    workflow = (workflow_type or "recipe").strip().lower()

    try:
        if workflow == "recipe":
            data = run_recipe(image_path=image_path, dietary_restrictions=dietary)
            return format_recipe_output(data)
        if workflow == "analysis":
            data = run_analysis(image_path=image_path)
            return format_analysis_output(data)
        return "Invalid workflow type. Choose 'recipe' or 'analysis'."
    except Exception as e:
        return f"Error: {e}"


def build_ui():
    example_paths = ensure_examples()
    examples = []
    if len(example_paths) >= 1:
        examples.append([example_paths[0], "vegan", "recipe"])
    if len(example_paths) >= 2:
        examples.append([example_paths[1], "", "analysis"])
    if len(example_paths) >= 3:
        examples.append([example_paths[2], "keto", "recipe"])
    if len(example_paths) >= 4:
        examples.append([example_paths[3], "", "analysis"])

    with gr.Blocks(title="AI NourishBot") as demo:
        gr.Markdown("# AI NourishBot")
        gr.Markdown(
            "CrewAI multi-agent coach: **recipe** (fridge → filtered ingredients → "
            "ideas) or **analysis** (dish photo → nutrients/calories).  \n"
            "Needs `GROQ_API_KEY` + vision model (or Ollama + `llava`) in repo-root "
            "`.env`. Related: simpler Flask Coach in `../AI Nutrition Coach/`.  \n"
            "Educational estimates only — not medical advice."
        )
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## Inputs")
                image_input = gr.Image(type="pil", label="Upload Image")
                dietary_input = gr.Textbox(
                    label="Dietary Restrictions (optional)",
                    placeholder="e.g., vegan",
                )
                workflow_radio = gr.Radio(
                    ["recipe", "analysis"],
                    value="recipe",
                    label="Workflow Type",
                )
                submit_btn = gr.Button("Analyze", variant="primary")
            with gr.Column(scale=2):
                if examples:
                    gr.Examples(
                        examples=examples,
                        inputs=[image_input, dietary_input, workflow_radio],
                        label="Examples (autofill, then click Analyze)",
                    )
                result_display = gr.Markdown(
                    "_Results will appear here…_",
                )

        submit_btn.click(
            fn=analyze_food,
            inputs=[image_input, dietary_input, workflow_radio],
            outputs=result_display,
        )
    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name=os.getenv("GRADIO_HOST", "127.0.0.1"),
        server_port=int(os.getenv("GRADIO_PORT", "7869")),
    )
