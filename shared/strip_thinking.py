"""Strip model chain-of-thought / thinking tags from LLM output."""

from __future__ import annotations

import re

_THINKING_BLOCK_RE = re.compile(
    r"<(?:redacted_)?think(?:ing)?>.*?</(?:redacted_)?think(?:ing)?>",
    re.DOTALL | re.IGNORECASE,
)
# Truncated replies often leave an unclosed think block that eats the rest.
_THINKING_OPEN_RE = re.compile(
    r"<(?:redacted_)?think(?:ing)?>.*",
    re.DOTALL | re.IGNORECASE,
)


def strip_model_thinking(text: str) -> str:
    cleaned = _THINKING_BLOCK_RE.sub("", text or "")
    cleaned = _THINKING_OPEN_RE.sub("", cleaned)
    return cleaned.strip()
