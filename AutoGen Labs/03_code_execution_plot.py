"""03 — AssistantAgent + UserProxyAgent code execution (matplotlib sine wave)."""

from __future__ import annotations

from pathlib import Path

from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor

from _bootstrap import HERE, banner, get_llm_config

CODING = HERE / "coding"


def main() -> None:
    banner("03 — Code execution (sine plot)")
    llm_config = get_llm_config()
    CODING.mkdir(parents=True, exist_ok=True)

    assistant = AssistantAgent(
        name="assistant",
        system_message=(
            "You are a helpful assistant who writes and explains Python code clearly. "
            "When asked to plot, write complete runnable code that saves the figure "
            f"to {CODING.as_posix()}/sine_wave.png (or relative sine_wave.png in the "
            "working directory). Use matplotlib and numpy."
        ),
        llm_config=llm_config,
    )

    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        code_execution_config={
            "executor": LocalCommandLineCodeExecutor(
                work_dir=str(CODING),
                timeout=60,
            ),
        },
    )

    chat_result = user_proxy.initiate_chat(
        recipient=assistant,
        message=(
            "Plot a sine wave using matplotlib from -2π to 2π and save the plot "
            "as sine_wave.png in the current working directory."
        ),
        max_turns=4,
        summary_method="reflection_with_llm",
    )

    image_path = CODING / "sine_wave.png"
    if image_path.is_file():
        print(f"\nPlot saved: {image_path}")
    else:
        print(f"\nPlot not found at {image_path}")

    print("\nFinal Summary:")
    print(getattr(chat_result, "summary", chat_result))


if __name__ == "__main__":
    main()
