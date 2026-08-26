"""
AI-Powered YouTube Summarizer + QA (RAG)
Transcript → chunk → local embeddings → FAISS → Groq/Ollama summary & answers → Gradio
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from youtube_transcript_api import YouTubeTranscriptApi

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.embeddings import get_embedding_model, resolve_embedding_model
from shared.llm import describe_setup, get_llm_info

load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(ROOT / ".env")
# Also reuse Meeting Assistant .env if present (same Groq key)
load_dotenv(ROOT / "Meeting Assistant" / ".env")

llm, llm_info = get_llm_info(temperature=0.3)
embeddings = get_embedding_model()
print(describe_setup())
print(f"Embeddings={resolve_embedding_model()}")

# video_id -> {"processed": str, "faiss": FAISS | None}
_cache: dict[str, dict] = {}

VIDEO_ID_RE = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)"
    r"([a-zA-Z0-9_-]{11})"
)

summary_prompt = ChatPromptTemplate.from_template(
    """You are an AI assistant tasked with summarizing YouTube video transcripts.
Provide a concise, informative summary that captures the main points.

Instructions:
1. Summarize in a single concise paragraph (or short bullet list if the video is dense).
2. Ignore timestamps.
3. Focus on spoken content only.

Transcript:
{transcript}
"""
)

summary_chain = summary_prompt | llm | StrOutputParser()

qa_prompt = ChatPromptTemplate.from_template(
    """You are an expert assistant answering questions from YouTube video content.
Use only the relevant context below. If the answer is not in the context, say so.

Relevant Video Context:
{context}

Question: {question}

Answer:"""
)

qa_chain = qa_prompt | llm | StrOutputParser()


def get_video_id(url: str) -> str | None:
    if not url:
        return None
    match = VIDEO_ID_RE.search(url.strip())
    return match.group(1) if match else None


def get_transcript(url: str):
    video_id = get_video_id(url)
    if not video_id:
        return None

    ytt_api = YouTubeTranscriptApi()
    transcripts = ytt_api.list(video_id)

    transcript = None
    for t in transcripts:
        if t.language_code != "en":
            continue
        if t.is_generated:
            if transcript is None:
                transcript = t.fetch()
        else:
            transcript = t.fetch()
            break

    return transcript


def process(transcript) -> str:
    if not transcript:
        return ""

    lines: list[str] = []
    # FetchedTranscript is iterable of snippets with .text / .start
    for item in transcript:
        try:
            if isinstance(item, dict):
                text = item.get("text")
                start = item.get("start")
            else:
                text = getattr(item, "text", None)
                start = getattr(item, "start", None)
            if text is None:
                continue
            lines.append(f"Text: {text} Start: {start}")
        except (AttributeError, TypeError, KeyError):
            continue
    return "\n".join(lines)


def chunk_transcript(
    processed_transcript: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(processed_transcript)


def _ensure_processed(video_url: str) -> tuple[str | None, str]:
    """Return (video_id, processed_transcript) or raise-friendly error message via empty id."""
    video_id = get_video_id(video_url)
    if not video_id:
        return None, "Please provide a valid YouTube URL."

    cached = _cache.get(video_id)
    if cached and cached.get("processed"):
        return video_id, cached["processed"]

    fetched = get_transcript(video_url)
    processed = process(fetched)
    if not processed:
        return video_id, ""

    _cache[video_id] = {"processed": processed, "faiss": None}
    return video_id, processed


def _ensure_faiss(video_id: str, processed: str) -> FAISS:
    entry = _cache.setdefault(video_id, {"processed": processed, "faiss": None})
    if entry.get("faiss") is not None:
        return entry["faiss"]

    chunks = chunk_transcript(processed)
    index = FAISS.from_texts(chunks, embeddings)
    entry["faiss"] = index
    entry["processed"] = processed
    return index


def summarize_video(video_url: str) -> str:
    video_id, processed = _ensure_processed(video_url)
    if video_id is None:
        return processed  # error message
    if not processed:
        return "No English transcript available for this video."

    # Cap very long transcripts for the summary call
    max_chars = int(os.getenv("SUMMARY_MAX_CHARS", "12000"))
    transcript_for_llm = processed[:max_chars]
    return summary_chain.invoke({"transcript": transcript_for_llm})


def answer_question(video_url: str, user_question: str) -> str:
    if not (user_question or "").strip():
        return "Please enter a question."

    video_id, processed = _ensure_processed(video_url)
    if video_id is None:
        return processed
    if not processed:
        return "No English transcript available for this video."

    faiss_index = _ensure_faiss(video_id, processed)
    docs = faiss_index.similarity_search(user_question.strip(), k=7)
    context = "\n\n".join(d.page_content for d in docs)
    return qa_chain.invoke({"context": context, "question": user_question.strip()})


with gr.Blocks(title="YouTube Summarizer & QA") as interface:
    gr.Markdown(
        f"## YouTube Summarizer & QA (RAG)\n"
        f"LLM: `{llm_info.provider}:{llm_info.model}` · "
        f"Embeddings: `{resolve_embedding_model()}`"
    )
    video_url = gr.Textbox(
        label="YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
    )
    with gr.Row():
        summarize_btn = gr.Button("Summarize Video", variant="primary")
        question_btn = gr.Button("Ask a Question")
    summary_output = gr.Textbox(label="Video Summary", lines=6)
    question_input = gr.Textbox(
        label="Ask a Question About the Video",
        placeholder="What is the main topic?",
    )
    answer_output = gr.Textbox(label="Answer", lines=6)

    summarize_btn.click(summarize_video, inputs=video_url, outputs=summary_output)
    question_btn.click(
        answer_question,
        inputs=[video_url, question_input],
        outputs=answer_output,
    )

if __name__ == "__main__":
    interface.launch(server_name="0.0.0.0", server_port=7860)
