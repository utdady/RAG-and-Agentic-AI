"""
AI Meeting Assistant
Whisper → optional financial-term cleanup → minutes/tasks (Groq or Ollama) → Gradio
"""

import os
import sys
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from transformers import pipeline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.llm import describe_setup, get_llm_info, resolve_whisper_model

# Project .env first, then repo-root .env (does not override existing vars)
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(ROOT / ".env")

ENABLE_PRODUCT_ASSISTANT = (
    os.getenv("ENABLE_PRODUCT_ASSISTANT", "false").lower() == "true"
)
OUTPUT_FILE = Path("meeting_minutes_and_tasks.txt")

llm, llm_info = get_llm_info(temperature=0.5)
whisper_model = resolve_whisper_model()
print(describe_setup())

asr_pipe = pipeline(
    "automatic-speech-recognition",
    model=whisper_model,
    chunk_length_s=30,
)

minutes_prompt = ChatPromptTemplate.from_template(
    """Generate meeting minutes and a list of tasks based on the provided context.

Context:
{context}

Meeting Minutes:
- Key points discussed
- Decisions made

Task List:
- Actionable items with assignees and deadlines
"""
)

minutes_chain = minutes_prompt | llm | StrOutputParser()

PRODUCT_SYSTEM_PROMPT = """You are an intelligent assistant specializing in financial products;
your task is to process transcripts of earnings calls, ensuring that all references to
financial products and common financial terms are in the correct format. For each
financial product or common term that is typically abbreviated as an acronym, the full term
should be spelled out followed by the acronym in parentheses. For example, '401k' should be
transformed to '401(k) retirement savings plan', 'HSA' should be transformed to
'Health Savings Account (HSA)', 'ROA' should be transformed to 'Return on Assets (ROA)',
'VaR' should be transformed to 'Value at Risk (VaR)', and 'PB' should be transformed to
'Price to Book (PB) ratio'. Similarly, transform spoken numbers representing financial
products into their numeric representations, followed by the full name of the product in
parentheses. For instance, 'five two nine' to '529 (Education Savings Plan)' and
'four zero one k' to '401(k) (Retirement Savings Plan)'. However, be aware that some
acronyms can have different meanings based on the context (e.g., 'LTV' can stand for
'Loan to Value' or 'Lifetime Value'). You will need to discern from the context which
term is being referred to and apply the appropriate transformation. In cases where
numerical figures or metrics are spelled out but do not represent specific financial
products (like 'twenty three percent'), these should be left as is. Your role is to
analyze and adjust financial product terminology in the text. Once you've done that,
produce the adjusted transcript and a list of the words you've changed"""


def remove_non_ascii(text: str) -> str:
    return "".join(ch for ch in text if ord(ch) < 128)


def product_assistant(ascii_transcript: str) -> str:
    """Normalize financial product terms using the same chat LLM."""
    prompt = PRODUCT_SYSTEM_PROMPT + "\n\nTranscript:\n" + ascii_transcript
    response = llm.invoke(prompt)
    return getattr(response, "content", response)


def transcript_audio(audio_file: str):
    if not audio_file:
        return "Please upload an audio file.", None

    raw_transcript = asr_pipe(audio_file, batch_size=8)["text"]
    ascii_transcript = remove_non_ascii(raw_transcript)

    if ENABLE_PRODUCT_ASSISTANT:
        context = product_assistant(ascii_transcript)
    else:
        context = ascii_transcript

    result = minutes_chain.invoke({"context": context})

    OUTPUT_FILE.write_text(result, encoding="utf-8")
    return result, str(OUTPUT_FILE)


audio_input = gr.Audio(
    sources=["upload"],
    type="filepath",
    label="Upload your audio file",
)
output_text = gr.Textbox(label="Meeting Minutes and Tasks")
download_file = gr.File(label="Download the Generated Meeting Minutes and Tasks")

iface = gr.Interface(
    fn=transcript_audio,
    inputs=audio_input,
    outputs=[output_text, download_file],
    title="AI Meeting Assistant",
    description=(
        f"Upload meeting audio → Whisper transcript → minutes & tasks "
        f"via {llm_info.provider}:{llm_info.model}."
    ),
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=5000)
