"""07 — ThinkTool + WikipediaTool (course t7)."""

from __future__ import annotations

import asyncio

from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.middleware.trajectory import GlobalTrajectoryMiddleware
from beeai_framework.tools import Tool
from beeai_framework.tools.search.wikipedia import WikipediaTool
from beeai_framework.tools.think import ThinkTool

from _agents import ConditionalRequirement, RequirementAgent
from _bootstrap import banner, get_chat_model, quiet_asyncio_logs
from _cyber import ANALYSIS_QUERY, SYSTEM_INSTRUCTIONS


async def reasoning_enhanced_agent_example() -> None:
    llm = get_chat_model(temperature=0)
    reasoning_agent = RequirementAgent(
        llm=llm,
        tools=[ThinkTool(), WikipediaTool()],
        memory=UnconstrainedMemory(),
        instructions=SYSTEM_INSTRUCTIONS,
        middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
        requirements=[
            ConditionalRequirement(ThinkTool, max_invocations=2),
            ConditionalRequirement(WikipediaTool, max_invocations=2),
        ],
    )
    result = await reasoning_agent.run(ANALYSIS_QUERY)
    print(f"\nReasoning + Research Analysis:\n{result.answer.text}")


async def main() -> None:
    quiet_asyncio_logs()
    banner("07 — Think + Wikipedia")
    await reasoning_enhanced_agent_example()


if __name__ == "__main__":
    asyncio.run(main())
