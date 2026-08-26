"""06 — Educational storyteller: LLM story + gTTS audio (course: Watsonx Mistral)."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from gtts import gTTS

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(HERE / ".env")
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / "Meeting Assistant" / ".env")

from shared.llm import describe_setup, get_llm_info

llm, info = get_llm_info(temperature=0.5)
print(describe_setup())

STORY_PROMPT = """Write an engaging and educational story about {topic} for beginners.
Use simple and clear language to explain basic concepts.
Include interesting facts and keep it friendly and encouraging.
The story should be around 200-300 words and end with a brief summary of what we learned.
Make it perfect for someone just starting to learn about this topic."""


def generate_story(topic: str) -> str:
    prompt = STORY_PROMPT.format(topic=topic.strip())
    out = llm.invoke(prompt)
    return getattr(out, "content", str(out))


def story_and_speech(topic: str):
    if not (topic or "").strip():
        return "Enter a topic first.", None
    try:
        story = generate_story(topic)
        tts = gTTS(story)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.close()
        tts.save(tmp.name)
        return story, tmp.name
    except Exception as e:
        return f"Error: {e}", None


demo = gr.Interface(
    fn=story_and_speech,
    inputs=gr.Textbox(
        label="Topic",
        placeholder="e.g. the life cycle of butterflies",
        lines=2,
    ),
    outputs=[
        gr.Textbox(label="Generated Story", lines=16),
        gr.Audio(label="Narration (gTTS)", type="filepath"),
    ],
    title="Personal Storyteller",
    description=(
        f"Generate a beginner-friendly educational story "
        f"({info.provider}:{info.model}), then narrate it with gTTS. "
        "Needs network access for text-to-speech."
    ),
    examples=[
        ["the life cycle of butterflies"],
        ["life cycle of a human"],
        ["how volcanoes form"],
    ],
    allow_flagging="never",
)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7869, share=False)
