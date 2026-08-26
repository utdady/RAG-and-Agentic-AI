"""09 — Think after every tool (force_after=Tool) (course t9)."""

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
            ConditionalRequirement(
                ThinkTool,
                force_at_step=1,
                force_after=Tool,
                min_invocations=1,
                max_invocations=5,
                consecutive_allowed=False,
            ),
        ],
    )
    result = await reasoning_agent.run(ANALYSIS_QUERY)
    print(f"\nReasoning + Research Analysis:\n{result.answer.text}")


async def main() -> None:
    quiet_asyncio_logs()
    banner("09 — Force think after tools")
    await reasoning_enhanced_agent_example()


if __name__ == "__main__":
    asyncio.run(main())
