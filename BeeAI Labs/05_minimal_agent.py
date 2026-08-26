"""05 — Minimal RequirementAgent, no tools (course t5)."""

from __future__ import annotations

import asyncio

from beeai_framework.memory import UnconstrainedMemory

from _agents import RequirementAgent
from _bootstrap import banner, get_chat_model, quiet_asyncio_logs
from _cyber import ANALYSIS_QUERY, SYSTEM_INSTRUCTIONS


async def minimal_tracked_agent_example() -> None:
    llm = get_chat_model(temperature=0)
    minimal_agent = RequirementAgent(
        llm=llm,
        tools=[],
        memory=UnconstrainedMemory(),
        instructions=SYSTEM_INSTRUCTIONS,
    )
    result = await minimal_agent.run(ANALYSIS_QUERY)
    print(f"\nPure LLM Analysis:\n{result.answer.text}")


async def main() -> None:
    quiet_asyncio_logs()
    banner("05 — Minimal RequirementAgent")
    await minimal_tracked_agent_example()


if __name__ == "__main__":
    asyncio.run(main())
