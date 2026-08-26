"""05 — HTTP + Stdio clients against CalculatorMCPServer."""

from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport, StreamableHttpTransport

from _bootstrap import HERE, banner, tool_text
from _data import ensure_sample_docs

SERVER = HERE / "servers" / "calculator_server.py"
PORT = int(os.getenv("MCP_HTTP_PORT", "8000"))


def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return False
        except OSError:
            return True


async def run() -> None:
    ensure_sample_docs()
    banner("05 — Calculator MCP HTTP + Stdio clients")

    # --- Stdio ---
    stdio = Client(
        StdioTransport(
            command=sys.executable,
            args=[str(SERVER)],
        )
    )
    async with stdio:
        tools = await stdio.list_tools()
        print(f"Stdio tools: {[t.name for t in tools]}")
        r = await stdio.call_tool("add", {"a": 4, "b": 5})
        print(f"Stdio add(4,5) = {tool_text(r)}")

    # --- HTTP (spawn server if needed) ---
    proc = None
    if not port_in_use(PORT):
        print(f"\nStarting HTTP server on port {PORT} …")
        proc = subprocess.Popen(
            [sys.executable, str(SERVER), "--http"],
            cwd=str(HERE),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(40):
            if port_in_use(PORT):
                break
            time.sleep(0.25)
        else:
            if proc:
                proc.terminate()
            raise SystemExit(f"HTTP server did not start on port {PORT}")
    else:
        print(f"\nPort {PORT} already in use — reusing existing server.")

    try:
        http = Client(
            StreamableHttpTransport(url=f"http://127.0.0.1:{PORT}/mcp")
        )
        async with http:
            r = await http.call_tool("add", {"a": 4, "b": 5})
            print(f"HTTP add(4,5) = {tool_text(r)}")
            tools = await http.list_tools()
            print(f"HTTP tools: {[t.name for t in tools]}")
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    print("\nDone.")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
