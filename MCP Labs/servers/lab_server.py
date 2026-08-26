"""Lab MCP server for the custom ClientSession client (echo, write, resources, prompt).

Run via stdio (spawned by the client):
  python servers/lab_server.py
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastmcp import FastMCP

logging.getLogger("fastmcp").setLevel(logging.WARNING)

HERE = Path(__file__).resolve().parent
BASE_DIR = HERE  # sandbox: servers/ (resources/ under here)
RESOURCES = BASE_DIR / "lab_resources"
RESOURCES.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("lab-server")


@mcp.tool()
def echo(text: str) -> str:
    """Echo back the input text."""
    return f"Echo: {text}"


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write content to a file under the lab server directory."""
    file_path = (BASE_DIR / path).resolve()
    try:
        file_path.relative_to(BASE_DIR)
    except ValueError as e:
        raise ValueError("Path escapes lab server directory") from e
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"Successfully wrote to {path}"


@mcp.resource("file://resources/{filename}")
def read_resource_file(filename: str) -> str:
    """Read a file from the lab_resources directory."""
    file_path = RESOURCES / filename
    if not file_path.exists():
        return f"File not found: {filename}"
    return file_path.read_text(encoding="utf-8")


@mcp.prompt()
def review_file(filename: str) -> str:
    """Generate a prompt to review a file's contents."""
    return f"""Please review the file '{filename}' and provide:

A summary of its contents
Key points or sections
Any suggestions for improvement
Overall quality assessment

Use the appropriate tools to read the file if needed."""


if __name__ == "__main__":
    mcp.run()
