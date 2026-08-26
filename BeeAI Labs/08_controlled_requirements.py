"""08 — Controlled execution via ConditionalRequirement (course t8)."""

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


async def controlled_execution_example() -> None:
    llm = get_chat_model(temperature=0)
    controlled_agent = RequirementAgent(
        llm=llm,
        tools=[ThinkTool(), WikipediaTool()],
        memory=UnconstrainedMemory(),
        instructions=SYSTEM_INSTRUCTIONS,
        middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
        requirements=[
            ConditionalRequirement(
                ThinkTool,
                force_at_step=1,
                min_invocations=1,
                max_invocations=3,
                consecutive_allowed=False,
            ),
            ConditionalRequirement(
                WikipediaTool,
                only_after=[ThinkTool],
                min_invocations=1,
                max_invocations=2,
            ),
        ],
    )
    result = await controlled_agent.run(ANALYSIS_QUERY)
    print(f"\nControlled Execution Analysis:\n{result.answer.text}")


async def main() -> None:
    quiet_asyncio_logs()
    banner("08 — Controlled requirements")
    await controlled_execution_example()


if __name__ == "__main__":
    asyncio.run(main())
