"""10 — AskPermissionRequirement (human-in-the-loop) (course t10)."""

from __future__ import annotations

import asyncio
import sys

from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.middleware.trajectory import GlobalTrajectoryMiddleware
from beeai_framework.tools import Tool
from beeai_framework.tools.search.wikipedia import WikipediaTool
from beeai_framework.tools.think import ThinkTool

from _agents import AskPermissionRequirement, ConditionalRequirement, RequirementAgent
from _bootstrap import banner, get_chat_model, quiet_asyncio_logs
from _cyber import ANALYSIS_QUERY, SYSTEM_INSTRUCTIONS


async def production_security_example() -> None:
    if AskPermissionRequirement is None:
        print("AskPermissionRequirement not available in this beeai-framework version.")
        sys.exit(1)

    llm = get_chat_model(temperature=0)
    secure_agent = RequirementAgent(
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
                max_invocations=2,
                consecutive_allowed=False,
            ),
            AskPermissionRequirement(WikipediaTool),
            ConditionalRequirement(
                WikipediaTool,
                only_after=[ThinkTool],
                min_invocations=0,
                max_invocations=1,
            ),
        ],
    )
    print("Note: you may be prompted to approve Wikipedia tool use.")
    result = await secure_agent.run(ANALYSIS_QUERY)
    print(f"\nSecurity-Approved Analysis:\n{result.answer.text}")


async def main() -> None:
    quiet_asyncio_logs()
    banner("10 — Ask permission")
    await production_security_example()


if __name__ == "__main__":
    asyncio.run(main())
