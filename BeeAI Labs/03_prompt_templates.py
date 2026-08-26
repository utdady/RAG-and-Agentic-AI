"""03 — Simple mustache-style prompt templates (course t3)."""

from __future__ import annotations

import asyncio

from beeai_framework.backend import UserMessage

from _bootstrap import banner, get_chat_model, llm_text, quiet_asyncio_logs


class SimplePromptTemplate:
    """Simple prompt template using Python string formatting."""

    def __init__(self, template: str):
        self.template = template

    def render(self, variables: dict) -> str:
        formatted_template = self.template
        for key in variables:
            formatted_template = formatted_template.replace(f"{{{{{key}}}}}", f"{{{key}}}")
        return formatted_template.format(**variables)


async def prompt_template_example() -> None:
    llm = get_chat_model(temperature=0)

    template_content = """
    You are a senior data scientist evaluating a machine learning project proposal.

    Project Details:
    - Project Name: {{project_name}}
    - Business Problem: {{business_problem}}
    - Available Data: {{data_description}}
    - Timeline: {{timeline}}
    - Success Metrics: {{success_metrics}}

    Please provide:
    1. Feasibility assessment (1-10 scale)
    2. Key technical challenges
    3. Recommended approach
    4. Risk mitigation strategies
    5. Expected outcomes

    Be specific and actionable in your recommendations.
    """

    prompt_template = SimplePromptTemplate(template_content)

    project_scenarios = [
        {
            "project_name": "Smart Inventory Optimization",
            "business_problem": (
                "Reduce inventory costs while maintaining 95% product availability"
            ),
            "data_description": (
                "2 years of sales data, supplier lead times, seasonal patterns, 500K records"
            ),
            "timeline": "3 months development, 1 month testing",
            "success_metrics": (
                "15% cost reduction, maintain 95% availability, <2% forecast error"
            ),
        },
        {
            "project_name": "Fraud Detection System",
            "business_problem": (
                "Detect fraudulent transactions in real-time with minimal false positives"
            ),
            "data_description": (
                "1M transaction records, user behavior data, device fingerprints"
            ),
            "timeline": "6 months development, 2 months validation",
            "success_metrics": (
                "95% fraud detection rate, <1% false positive rate, <100ms response time"
            ),
        },
    ]

    for i, scenario in enumerate(project_scenarios, 1):
        print(f"\n=== Project Evaluation {i}: {scenario['project_name']} ===")
        rendered_prompt = prompt_template.render(scenario)
        print("\n  Rendered prompt:")
        print(rendered_prompt)
        messages = [UserMessage(content=rendered_prompt)]
        text = await llm_text(llm, messages)
        print("### LLM response: ###\n")
        print(text)


async def main() -> None:
    quiet_asyncio_logs()
    banner("03 — Prompt templates")
    await prompt_template_example()


if __name__ == "__main__":
    asyncio.run(main())
