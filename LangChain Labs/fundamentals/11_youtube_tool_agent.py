"""11 — YouTube tools + recursive tool-calling chain.

Course: Tool Calling Agent (OpenAI + pytube/yt-dlp).
Here: Groq/Ollama via shared.llm. Search uses yt-dlp (not fragile pytube Search).

Product-style transcript RAG UI → ../../YouTube Summarizer/
"""

from __future__ import annotations

import json
import logging
import re
import warnings
from typing import Any

warnings.filterwarnings("ignore")
logging.getLogger("yt_dlp").setLevel(logging.ERROR)

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import tool
from youtube_transcript_api import YouTubeTranscriptApi

from _bootstrap import banner
from shared.llm import get_llm_info

banner("11 YouTube tool-calling agent")

llm, info = get_llm_info(temperature=0)
print(f"Using {info.provider}:{info.model}")

ID_PATTERN = re.compile(r"(?:v=|be/|embed/|shorts/)([a-zA-Z0-9_-]{11})")


def _as_watch_url(url_or_id: str) -> str:
    text = (url_or_id or "").strip()
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", text):
        return f"https://www.youtube.com/watch?v={text}"
    return text


@tool
def extract_video_id(url: str) -> str:
    """Extract the 11-character YouTube video ID from a URL."""
    match = ID_PATTERN.search(url or "")
    return match.group(1) if match else "Error: Invalid YouTube URL"


@tool
def fetch_transcript(video_id: str, language: str = "en") -> str:
    """Fetch YouTube transcript text for a video_id (e.g. dQw4w9WgXcQ)."""
    try:
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id, languages=[language])
        text = " ".join(snippet.text for snippet in transcript.snippets)
        # Cap size so tool messages stay manageable for the LLM context
        if len(text) > 12000:
            return text[:12000] + "\n…[transcript truncated]"
        return text
    except Exception as e:
        return f"Error: {e}"


@tool
def search_youtube(query: str, max_results: int = 3) -> list[dict[str, str]] | str:
    """
    Search YouTube for videos matching the query.
    Returns [{'title', 'video_id', 'url'}, ...].
    """
    try:
        import yt_dlp

        n = max(1, min(int(max_results), 5))
        opts = {
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch{n}:{query}", download=False)
        entries = info.get("entries") or []
        out = []
        for e in entries:
            if not e:
                continue
            vid = e.get("id") or ""
            out.append(
                {
                    "title": e.get("title") or "",
                    "video_id": vid,
                    "url": f"https://youtu.be/{vid}" if vid else "",
                }
            )
        return out
    except Exception as e:
        return f"Error: {e}"


@tool
def get_full_metadata(url: str) -> dict[str, Any]:
    """
    Extract YouTube metadata (title, views, duration, channel, likes, chapters)
    from a URL or bare video id.
    """
    try:
        import yt_dlp

        watch = _as_watch_url(url)
        opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(watch, download=False)
        return {
            "title": info.get("title"),
            "views": info.get("view_count"),
            "duration": info.get("duration"),
            "channel": info.get("uploader"),
            "likes": info.get("like_count"),
            "comments": info.get("comment_count"),
            "chapters": info.get("chapters") or [],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def get_thumbnails(url: str) -> list[dict[str, Any]]:
    """List thumbnail URLs/resolutions for a YouTube URL or video id."""
    try:
        import yt_dlp

        watch = _as_watch_url(url)
        opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(watch, download=False)
        thumbs = []
        for t in info.get("thumbnails") or []:
            if "url" not in t:
                continue
            w, h = t.get("width"), t.get("height")
            thumbs.append(
                {
                    "url": t["url"],
                    "width": w,
                    "height": h,
                    "resolution": f"{w or ''}x{h or ''}".strip("x"),
                }
            )
        return thumbs
    except Exception as e:
        return [{"error": f"Failed to get thumbnails: {e}"}]


TOOLS = [
    extract_video_id,
    fetch_transcript,
    search_youtube,
    get_full_metadata,
    get_thumbnails,
]
TOOL_MAP = {t.name: t for t in TOOLS}
llm_with_tools = llm.bind_tools(TOOLS)


def execute_tool(tool_call: dict) -> ToolMessage:
    try:
        result = TOOL_MAP[tool_call["name"]].invoke(tool_call["args"])
        content = (
            json.dumps(result) if isinstance(result, (dict, list)) else str(result)
        )
    except Exception as e:
        content = f"Error: {e}"
    return ToolMessage(content=content, tool_call_id=tool_call["id"])


def process_tool_calls(messages: list) -> list:
    last = messages[-1]
    tool_messages = [
        execute_tool(tc) for tc in getattr(last, "tool_calls", []) or []
    ]
    updated = messages + tool_messages
    next_ai = llm_with_tools.invoke(updated)
    return updated + [next_ai]


def should_continue(messages: list) -> bool:
    last = messages[-1]
    return bool(getattr(last, "tool_calls", None))


def recursive_tool_loop(messages: list, max_rounds: int = 8) -> list:
    """Run tool rounds until the model stops calling tools (or cap)."""
    for _ in range(max_rounds):
        if not should_continue(messages):
            break
        messages = process_tool_calls(messages)
    return messages


universal_chain = (
    RunnableLambda(lambda x: [HumanMessage(content=x["query"])])
    | RunnableLambda(lambda msgs: msgs + [llm_with_tools.invoke(msgs)])
    | RunnableLambda(recursive_tool_loop)
)


def analyze_video(url: str) -> str:
    """Course TODO path: tools + one non-tool LLM analysis prompt."""
    vid = extract_video_id.invoke({"url": url})
    if vid.startswith("Error"):
        return vid
    meta = get_full_metadata.invoke({"url": vid})
    if "error" in meta:
        return str(meta)
    transcript = fetch_transcript.invoke({"video_id": vid})
    thumbs = get_thumbnails.invoke({"url": vid})
    prompt = f"""Analyze this YouTube video and provide a comprehensive summary.

VIDEO TITLE: {meta.get('title')}
CHANNEL: {meta.get('channel')}
VIEWS: {meta.get('views')}
DURATION: {meta.get('duration')} seconds
LIKES: {meta.get('likes')}
THUMBNAILS AVAILABLE: {len(thumbs) if isinstance(thumbs, list) else 0}

TRANSCRIPT EXCERPT:
{(transcript or '')[:3000]}

Provide:
1. Concise summary (3-5 bullets)
2. Main topics/themes
3. Intended audience
4. Brief note on likely performance drivers
"""
    return llm.invoke([HumanMessage(content=prompt)]).content


DEMO_SUMMARIZE = (
    "Summarize this YouTube video in English: "
    "https://www.youtube.com/watch?v=T-D1OfcDW1M"
)
DEMO_ANALYZE = "https://www.youtube.com/watch?v=vToG6mOkYh8"


if __name__ == "__main__":
    print("\nTools:", [t.name for t in TOOLS])

    print("\n--- Recursive agent: summarize ---")
    try:
        msgs = universal_chain.invoke({"query": DEMO_SUMMARIZE})
        final = msgs[-1]
        print(getattr(final, "content", final))
    except Exception as e:
        print(f"Skipped summarize demo (network/LLM): {e}")

    print("\n--- Direct analyze_video (course TODO style) ---")
    try:
        print(analyze_video(DEMO_ANALYZE))
    except Exception as e:
        print(f"Skipped analyze demo (network/LLM): {e}")

    print(
        "\nNote: course used a fixed 2-step LCEL chain (brittle) and pytube Search; "
        "this script uses a recursive tool loop + yt-dlp search. "
        "For Gradio summarize+RAG see YouTube Summarizer."
    )
