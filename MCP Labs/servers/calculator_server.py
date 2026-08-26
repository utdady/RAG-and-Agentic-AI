"""Shared Calculator FastMCP server (tools, resources, prompts).

Run stdio:  python servers/calculator_server.py
Run HTTP:   python servers/calculator_server.py --http
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from fastmcp import FastMCP

HERE = Path(__file__).resolve().parent
LABS = HERE.parent
DATA_DIR = LABS / "data" / "path"

mcp = FastMCP(
    name="CalculatorMCPServer",
    instructions="""
        This server provides calculator tools and simple document resources.
        Use add() / subtract() for arithmetic. Read documents via resources.
    """,
)


@mcp.tool
def add(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b


@mcp.tool
def subtract(a: int, b: int) -> int:
    """Subtract one integer from another (a - b)."""
    return a - b


@mcp.resource("file:///endpoint/{name}")
def return_template_document(name: str) -> str:
    """Return a templated document stub by name."""
    return f"Document contents of {name}"


@mcp.resource("file://endpoint2/{name}")
def read_document(name: str) -> str:
    """Read a document by name from the data/path directory."""
    try:
        path = DATA_DIR / name
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Document '{name}' not found in path directory"
    except Exception as e:
        return f"Error reading document: {e}"


@mcp.prompt(title="Code Review")
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


def main() -> None:
    if "--http" in sys.argv:
        port = int(os.getenv("MCP_HTTP_PORT", "8000"))
        host = os.getenv("MCP_HTTP_HOST", "127.0.0.1")
        print(f"Starting Calculator MCP HTTP on http://{host}:{port}/mcp")
        # FastMCP 2.x HTTP entrypoint
        import asyncio

        asyncio.run(mcp.run_http_async(host=host, port=port))
    else:
        mcp.run()


if __name__ == "__main__":
    main()
