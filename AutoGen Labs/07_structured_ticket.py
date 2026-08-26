"""07 — Structured ticket summary via Pydantic response_format."""

from __future__ import annotations

from autogen import ConversableAgent
from pydantic import BaseModel

from _bootstrap import banner, get_llm_config


class TicketSummary(BaseModel):
    customer_name: str
    issue_type: str
    urgency_level: str
    recommended_action: str


def main() -> None:
    banner("07 — Structured ticket summary")
    llm_config = get_llm_config(response_format=TicketSummary)

    support_agent = ConversableAgent(
        name="support_agent",
        system_message=(
            "You are a support assistant. Summarize a customer ticket using:\n"
            "- customer_name\n"
            "- issue_type (e.g. login issue, billing problem, bug report)\n"
            "- urgency_level (Low, Medium, High)\n"
            "- recommended_action"
        ),
        llm_config=llm_config,
    )

    result = support_agent.initiate_chat(
        recipient=support_agent,
        message=(
            "Ticket: John Doe is unable to reset his password and has an "
            "important meeting in 30 minutes."
        ),
        max_turns=1,
    )
    print("\nChat finished.")
    print(getattr(result, "summary", result))


if __name__ == "__main__":
    main()
