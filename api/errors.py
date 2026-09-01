"""Map provider/infra exceptions to user-facing demo messages."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class UserFacingError:
    title: str
    message: str
    code: str


def demo_unavailable() -> UserFacingError:
    return UserFacingError(
        title="This demo isn't available right now",
        message="We couldn't start this demo. Try another one from the lab, or check back later.",
        code="demo_unavailable",
    )


def unknown_demo() -> UserFacingError:
    return UserFacingError(
        title="Demo not found",
        message="That demo doesn't exist. Head back to the lab and pick another one.",
        code="unknown_demo",
    )


def parse_error() -> UserFacingError:
    return UserFacingError(
        title="Couldn't finish the response",
        message="The demo had trouble reading the model output. Please try again.",
        code="parse_error",
    )


def something_wrong() -> UserFacingError:
    return UserFacingError(
        title="Something went wrong",
        message="We couldn't complete your request. Please try again in a moment.",
        code="unknown",
    )


def _wait_hint(raw: str) -> str:
    match = re.search(r"try again in (\d+(?:\.\d+)?)\s*m", raw, re.I)
    if match:
        minutes = max(1, int(float(match.group(1))))
        return f" Please try again in about {minutes} minute{'s' if minutes != 1 else ''}."
    match = re.search(r"try again in (\d+(?:\.\d+)?)\s*s", raw, re.I)
    if match:
        seconds = max(5, int(float(match.group(1))))
        if seconds >= 60:
            minutes = max(1, round(seconds / 60))
            return f" Please try again in about {minutes} minute{'s' if minutes != 1 else ''}."
        return f" Please try again in about {seconds} seconds."
    return " Please try again in a few minutes."


def humanize_exception(exc: BaseException) -> UserFacingError:
    raw = str(exc)
    lower = raw.lower()

    if isinstance(exc, json.JSONDecodeError) or "jsondecodeerror" in lower:
        return parse_error()
    if "expecting" in lower and "delimiter" in lower:
        return parse_error()
    if "no json object found" in lower:
        return parse_error()

    if "429" in raw or "rate limit" in lower or "rate_limit" in lower:
        if "tokens per day" in lower or "tpd" in lower or "per day" in lower:
            return UserFacingError(
                title="Daily usage limit reached",
                message=(
                    "This demo has used its allowed tokens for today."
                    + _wait_hint(raw)
                    + " You can also come back tomorrow."
                ),
                code="usage_daily",
            )
        return UserFacingError(
            title="Please wait a moment",
            message=(
                "The demo is getting a lot of requests right now."
                + _wait_hint(raw)
            ),
            code="usage_minute",
        )

    if "groq_api_key" in lower or "api key" in lower and "not set" in lower:
        return demo_unavailable()

    if "model_not_found" in lower or (
        "does not exist" in lower and "model" in lower
    ):
        return UserFacingError(
            title="Vision model unavailable",
            message=(
                "This demo's vision model isn't available right now. "
                "Try again in a moment — the lab will use an updated model automatically."
            ),
            code="model_unavailable",
        )

    if "401" in raw or "invalid api key" in lower or "authentication" in lower:
        return demo_unavailable()

    if "upload" in lower and "first" in lower:
        return UserFacingError(
            title="Upload a file first",
            message="Add a document, then ask your question.",
            code="upload_required",
        )

    if "unknown demo" in lower:
        return unknown_demo()

    if "timeout" in lower or "timed out" in lower:
        return UserFacingError(
            title="That took too long",
            message="The demo didn't finish in time. Try a shorter question and run it again.",
            code="timeout",
        )

    if "connection" in lower and ("refused" in lower or "reset" in lower):
        return UserFacingError(
            title="Can't load the demo",
            message="The demo hub isn't responding. Refresh the page and try again.",
            code="connection",
        )

    return something_wrong()


def humanize_message(raw: str) -> UserFacingError:
    """Map a raw error string (already serialized) to a user-facing message."""
    try:
        return humanize_exception(Exception(raw))
    except Exception:
        return something_wrong()
