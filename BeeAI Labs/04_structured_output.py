"""04 — Structured output / Pydantic business plan (course t4)."""

from __future__ import annotations

import asyncio
from typing import List

from beeai_framework.backend import SystemMessage, UserMessage
from pydantic import BaseModel, Field

from _bootstrap import banner, get_chat_model, llm_structure, quiet_asyncio_logs


class BusinessPlan(BaseModel):
    """A comprehensive business plan structure."""

    business_name: str = Field(description="Catchy name for the business")
    elevator_pitch: str = Field(description="30-second description of the business")
    target_market: str = Field(description="Primary target audience")
    unique_value_proposition: str = Field(description="What makes this business special")
    revenue_streams: List[str] = Field(description="Ways the business will make money")
    startup_costs: str = Field(description="Estimated initial investment needed")
    key_success_factors: List[str] = Field(description="Critical elements for success")


async def structured_output_example() -> None:
    llm = get_chat_model(temperature=0)

    messages = [
        SystemMessage(content="You are an expert business consultant and entrepreneur."),
        UserMessage(
            content=(
                "Create a business plan for a mobile app that helps people find and "
                "book unique local experiences in their city."
            )
        ),
    ]

    obj = await llm_structure(llm, BusinessPlan, messages)
    if not isinstance(obj, dict):
        obj = obj.model_dump() if hasattr(obj, "model_dump") else dict(obj)

    print(
        "User: Create a business plan for a mobile app that helps people find and "
        "book unique local experiences in their city."
    )
    print("\nAI-Generated Business Plan:")
    print(f"Business Name: {obj['business_name']}")
    print(f"Elevator Pitch: {obj['elevator_pitch']}")
    print(f"Target Market: {obj['target_market']}")
    print(f"Unique Value Proposition: {obj['unique_value_proposition']}")
    print(f"Revenue Streams: {', '.join(obj['revenue_streams'])}")
    print(f"Startup Costs: {obj['startup_costs']}")
    print("Key Success Factors:")
    for factor in obj["key_success_factors"]:
        print(f"  - {factor}")


async def main() -> None:
    quiet_asyncio_logs()
    banner("04 — Structured output")
    await structured_output_example()


if __name__ == "__main__":
    asyncio.run(main())
