"""06 — RequirementAgent + WikipediaTool + trajectory (course t6)."""

from __future__ import annotations

import asyncio

from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.middleware.trajectory import GlobalTrajectoryMiddleware
from beeai_framework.tools import Tool
from beeai_framework.tools.search.wikipedia import WikipediaTool

from _agents import ConditionalRequirement, RequirementAgent
from _bootstrap import banner, get_chat_model, quiet_asyncio_logs
from _cyber import ANALYSIS_QUERY, SYSTEM_INSTRUCTIONS


async def wikipedia_enhanced_agent_example() -> None:
    llm = get_chat_model(temperature=0)
    wikipedia_agent = RequirementAgent(
        llm=llm,
        tools=[WikipediaTool()],
        memory=UnconstrainedMemory(),
        instructions=SYSTEM_INSTRUCTIONS,
        middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
        requirements=[ConditionalRequirement(WikipediaTool, max_invocations=2)],
    )
    result = await wikipedia_agent.run(ANALYSIS_QUERY)
    print(f"\nResearch-Enhanced Analysis:\n{result.answer.text}")


async def main() -> None:
    quiet_asyncio_logs()
    banner("06 — Wikipedia-enhanced agent")
    await wikipedia_enhanced_agent_example()


if __name__ == "__main__":
    asyncio.run(main())
