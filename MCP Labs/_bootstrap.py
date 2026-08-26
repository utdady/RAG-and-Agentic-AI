"""Shared helpers for MCP Labs."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

for p in (ROOT, HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from shared.env_load import load_env

load_env(HERE)

CONTEXT7_HTTP_URL = "https://mcp.context7.com/mcp"
CONTEXT7_STDIO_COMMAND = "npx"
CONTEXT7_STDIO_ARGS = ["-y", "@upstash/context7-mcp"]


def require_npx() -> None:
    if not shutil.which("npx"):
        raise SystemExit(
            "npx not found. Install Node.js (includes npx) to run Context7 via StdioTransport."
        )


def tool_text(response, *, limit: int | None = None) -> str:
    """Extract printable text from a FastMCP call_tool response."""
    content = getattr(response, "content", None) or []
    parts: list[str] = []
    for item in content:
        text = getattr(item, "text", None)
        if text:
            parts.append(text)
        elif isinstance(item, dict) and item.get("text"):
            parts.append(str(item["text"]))
    if not parts and hasattr(response, "data") and response.data is not None:
        parts.append(str(response.data))
    out = "\n".join(parts) if parts else str(response)
    if limit is not None:
        return out[:limit]
    return out


def banner(title: str) -> None:
    print("=" * 60)
    print(title)
    print("=" * 60)
