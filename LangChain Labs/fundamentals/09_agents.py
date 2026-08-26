"""09 — ReAct agent with simple tools (safe calculator; text formatter)."""

from __future__ import annotations

import ast
import operator
from typing import Any

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool

from _bootstrap import banner
from shared.llm import get_llm_info

banner("09 Agents (ReAct)")
llm, _ = get_llm_info(temperature=0)

# Safe arithmetic — do NOT use eval() on model output
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> Any:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Only simple arithmetic is allowed")


def calculator(expression: str) -> str:
    """Evaluate a simple arithmetic expression safely."""
    try:
        tree = ast.parse(expression.strip(), mode="eval")
        return str(_eval_node(tree))
    except Exception as e:
        return f"Error: {e}"


def format_text(text: str) -> str:
    """
    Format text. Input examples:
      uppercase: hello world
      lowercase: Hello
      titlecase: langchain is awesome
    """
    text = text.strip()
    for mode in ("uppercase", "lowercase", "titlecase"):
        prefix = f"{mode}:"
        if text.lower().startswith(prefix):
            body = text[len(prefix) :].strip()
            if mode == "uppercase":
                return body.upper()
            if mode == "lowercase":
                return body.lower()
            return body.title()
    return text.upper()


tools = [
    Tool(
        name="calculator",
        func=calculator,
        description="Useful for simple math. Input: an expression like '25 + 63'.",
    ),
    Tool(
        name="format_text",
        func=format_text,
        description=(
            "Format text. Input like 'uppercase: hello' or "
            "'titlecase: langchain is awesome'."
        ),
    ),
]

prompt_template = """You are a helpful assistant who can use tools.
You have access to these tools:

{tools}

The available tools are: {tool_names}

Follow this format:

Question: the user's question
Thought: think about what to do
Action: the tool to use, should be one of [{tool_names}]
Action Input: the input to the tool
Observation: the result from the tool
Thought: I now know the final answer
Final Answer: your final answer to the user's question

Question: {input}
{agent_scratchpad}
"""

prompt = PromptTemplate.from_template(prompt_template)
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5,
)

questions = [
    "What is 25 + 63?",
    "Can you convert 'hello world' to uppercase?",
    "Calculate 15 * 7",
    "titlecase: langchain is awesome",
]

for q in questions:
    print(f"\n===== Testing: {q} =====")
    result = executor.invoke({"input": q})
    print(f"Final Answer: {result['output']}")

print(
    "\nWarning: the original lab used eval() for the calculator — "
    "this script uses ast instead."
)
