"""03 — LangGraph ReAct agent + MultiServerMCPClient (Context7 + Met Museum).

Course MCP Application lab: OpenAI gpt-5-nano → Groq/Ollama.
Requires Node/npx for metmuseum-mcp; network for Context7 HTTP.
"""

from __future__ import annotations

import asyncio
import os
import shutil
import sys

from _bootstrap import CONTEXT7_HTTP_URL, banner, require_npx

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from shared.llm import describe_setup, get_chat_llm


def _mcp_servers() -> dict:
    url = os.getenv("CONTEXT7_MCP_URL", CONTEXT7_HTTP_URL).strip() or CONTEXT7_HTTP_URL
    context7: dict = {
        "url": url,
        "transport": "streamable_http",
    }
    api_key = os.getenv("CONTEXT7_API_KEY", "").strip()
    if api_key:
        context7["headers"] = {"Authorization": f"Bearer {api_key}"}

    return {
        "context7": context7,
        "met-museum": {
            "command": "npx",
            "args": ["-y", "metmuseum-mcp"],
            "transport": "stdio",
        },
    }


async def main() -> None:
    require_npx()
    if not shutil.which("npx"):
        raise SystemExit("npx required for Met Museum MCP")

    banner("03 — LangGraph + MultiServer MCP agent")
    print(describe_setup())

    client = MultiServerMCPClient(_mcp_servers())
    llm = get_chat_llm(temperature=0.2)
    tools = await client.get_tools()
    print(f"Loaded {len(tools)} MCP tools from Context7 + Met Museum.\n")

    checkpointer = InMemorySaver()
    config = {"configurable": {"thread_id": "mcp_app_conversation"}}

    agent = create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=checkpointer,
    )

    intro = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a smart, useful agent with tools to access code "
                        "library documentation (Context7) and the Met Museum collection. "
                        "Use tools when helpful; keep answers concise."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Give a brief introduction of what you do and the tools "
                        "you can access."
                    ),
                },
            ]
        },
        config=config,
    )
    print(intro["messages"][-1].content)

    while True:
        choice = input(
            """
Menu:
  1) Ask the agent a question
  2) Quit
Enter your choice (1 or 2): """
        ).strip()
        if choice == "1":
            query = input("Your question\n> ").strip()
            if not query:
                continue
            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": query}]},
                config=config,
            )
            print(response["messages"][-1].content)
        else:
            print("Goodbye!")
            break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)
