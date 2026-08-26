"""02 — Basic BeeAI ChatModel chat (course t2)."""

from __future__ import annotations

import asyncio

from beeai_framework.backend import SystemMessage, UserMessage

from _bootstrap import banner, get_chat_model, llm_text, quiet_asyncio_logs


async def basic_chat_example() -> None:
    llm = get_chat_model(temperature=0)
    messages = [
        SystemMessage(content="You are a helpful AI assistant and creative writing expert."),
        UserMessage(
            content=(
                "Help me brainstorm a unique business idea for a food delivery "
                "service that doesn't exist yet."
            )
        ),
    ]
    text = await llm_text(llm, messages)
    print(
        "User: Help me brainstorm a unique business idea for a food delivery "
        "service that doesn't exist yet."
    )
    print(f"Assistant: {text}")


async def main() -> None:
    quiet_asyncio_logs()
    banner("02 — Basic chat")
    await basic_chat_example()


if __name__ == "__main__":
    asyncio.run(main())
