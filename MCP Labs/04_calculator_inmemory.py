"""04 — LangChain @tool warm-up + in-memory FastMCP Client(mcp)."""

from __future__ import annotations

import asyncio

from langchain_core.tools import tool
from fastmcp import Client

from _bootstrap import banner, tool_text
from _data import ensure_sample_docs
from calculator_server import mcp


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


async def demos() -> None:
    ensure_sample_docs()
    banner("04 — In-memory Calculator MCP")

    print(f"LangChain tool: {multiply.name} — {multiply.description}")
    print(f"2 x 3 = {multiply.invoke({'a': 2, 'b': 3})}")

    client = Client(mcp)
    async with client:
        add_r = await client.call_tool("add", {"a": 4, "b": 5})
        print(f"\nadd(4,5) data={getattr(add_r, 'data', None)} text={tool_text(add_r)}")

        sub_r = await client.call_tool("subtract", {"a": 4, "b": 5})
        print(f"subtract(4,5) = {tool_text(sub_r)}")

        tools = await client.list_tools()
        print("\nAvailable tools:")
        for t in tools:
            print(f"- {t.name}: {t.description}")

        res = await client.read_resource("file:///endpoint/README.txt")
        text = res[0].text if res else ""
        print(f"\nTemplate resource: {text}")

        res2 = await client.read_resource("file://endpoint2/README.txt")
        print(f"File resource README.txt (first 200 chars):\n{(res2[0].text or '')[:200]}")

        missing = await client.read_resource("file://endpoint2/random.txt")
        print(f"Missing file: {missing[0].text}")

        prompt = await client.get_prompt("review_code", {"code": "print('hi')"})
        msg = prompt.messages[0]
        print(f"\nPrompt role={msg.role} content={msg.content.text}")

    print("\nDone.")


def main() -> None:
    asyncio.run(demos())


if __name__ == "__main__":
    main()
