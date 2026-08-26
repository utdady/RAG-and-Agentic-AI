"""Math + Wikipedia tools for the AI Math Assistant agent."""

from __future__ import annotations

import re

from langchain_core.tools import tool

_NUM = re.compile(r"-?\d+(?:\.\d+)?")


def _extract_numbers(text: str) -> list[float]:
    return [float(m) for m in _NUM.findall(text or "")]


@tool
def add_numbers(inputs: str) -> dict:
    """Extract numbers from text and return their sum as {"result": total}."""
    numbers = _extract_numbers(inputs)
    if not numbers:
        return {"result": "No numbers found in input."}
    return {"result": sum(numbers)}


@tool
def subtract_numbers(inputs: str) -> dict:
    """
    Sequential subtraction: first number minus each following number.
    Example: "100, 20, 10" → {"result": 70}.
    """
    numbers = _extract_numbers(inputs)
    if not numbers:
        return {"result": 0}
    result = numbers[0]
    for num in numbers[1:]:
        result -= num
    return {"result": result}


@tool
def multiply_numbers(inputs: str) -> dict:
    """Extract numbers from text and return their product as {"result": total}."""
    numbers = _extract_numbers(inputs)
    if not numbers:
        return {"result": 1}
    result = 1.0
    for num in numbers:
        result *= num
    return {"result": result}


@tool
def divide_numbers(inputs: str) -> dict:
    """
    Sequential division: first number divided by each following number.
    Example: "100, 5, 2" → {"result": 10.0}.
    """
    numbers = _extract_numbers(inputs)
    if not numbers:
        return {"result": 0}
    result = float(numbers[0])
    for num in numbers[1:]:
        if num == 0:
            return {"result": "Error: division by zero."}
        result /= num
    return {"result": result}


@tool
def calculate_power(input_text: str) -> dict:
    """
    Calculate base^exponent from text like "5^2", "5 2", or "5 to the power of 2".
    Returns {"result": value}.
    """
    text = input_text or ""
    match = re.search(r"(\d+(?:\.\d+)?)\s*\^+\s*(\d+(?:\.\d+)?)", text)
    if match:
        return {"result": float(match.group(1)) ** float(match.group(2))}

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:to\s+the\s+power\s+of)\s*(\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )
    if match:
        return {"result": float(match.group(1)) ** float(match.group(2))}

    numbers = _extract_numbers(text)
    if len(numbers) != 2:
        return {
            "result": "Invalid input. Provide exactly two numbers "
            "(e.g. '5^2', '5 2', or '5 to the power of 2')."
        }
    base, exponent = numbers
    return {"result": base**exponent}


@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for factual information about a topic."""
    import wikipedia
    from langchain_community.utilities import WikipediaAPIWrapper

    wikipedia.set_user_agent("AI-Math-Assistant/1.0 (local-lab)")
    wiki = WikipediaAPIWrapper()
    return wiki.run(query)


ALL_TOOLS = [
    add_numbers,
    subtract_numbers,
    multiply_numbers,
    divide_numbers,
    calculate_power,
    search_wikipedia,
]

SYSTEM_PROMPT = (
    "You are a helpful mathematical assistant that can perform arithmetic "
    "(add, subtract, multiply, divide, power) and look up facts on Wikipedia. "
    "Use tools precisely for calculations and lookups. Explain reasoning briefly. "
    "For multi-step questions (e.g. look up a population then multiply), "
    "call tools in order and use prior results."
)
