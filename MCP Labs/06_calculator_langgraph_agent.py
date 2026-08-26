"""06 — LangGraph ReAct agent over Calculator MCP (stdio + optional HTTP)."""

from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from shared.llm import describe_setup, get_chat_llm

from _bootstrap import HERE, banner
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


def _message_label(msg) -> str:
    if isinstance(msg, HumanMessage):
        return "HUMAN"
    if isinstance(msg, AIMessage):
        return "AI"
    if isinstance(msg, ToolMessage):
        return "TOOL"
    return "OTHER"


async def run() -> None:
    ensure_sample_docs()
    banner("06 — LangGraph + Calculator MCP")
    print(describe_setup())

    proc = None
    if not port_in_use(PORT):
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

    try:
        client = MultiServerMCPClient(
            {
                "stdio-calculator": {
                    "command": sys.executable,
                    "args": [str(SERVER)],
                    "transport": "stdio",
                },
                "http-calculator": {
                    "url": f"http://127.0.0.1:{PORT}/mcp",
                    "transport": "streamable_http",
                },
            }
        )
        tools = await client.get_tools()
        print(f"Tools: {[t.name for t in tools]}")

        llm = get_chat_llm(temperature=0)
        agent = create_react_agent(model=llm, tools=tools)
        agent_response = await agent.ainvoke(
            {"messages": "whats 8 + 7? use tools"}
        )

        for msg in agent_response["messages"]:
            content = getattr(msg, "content", "") or ""
            if content == "":
                content = "tool call"
            print(f"[{_message_label(msg)}] {content}")
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
