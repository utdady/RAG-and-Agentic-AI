"""Utility helpers for Style Finder."""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

_THINKING_BLOCK_RE = re.compile(
    r"<(?:redacted_)?think(?:ing)?>.*?</(?:redacted_)?think(?:ing)?>",
    re.DOTALL | re.IGNORECASE,
)
_ITEMS_SECTION_RE = re.compile(
    r"(?:^|\n)\s*#{0,3}\s*(?:ITEM\s+DETAILS|SIMILAR\s+ITEMS)\b.*",
    re.IGNORECASE | re.DOTALL,
)


def get_all_items_for_image(image_url, dataset):
    related_items = dataset[dataset["Image URL"] == image_url]
    logger.info("Found %s items for image URL", len(related_items))
    return related_items


def format_price(price) -> str:
    text = str(price).strip()
    if not text or text.lower() in {"?", "nan", "none"}:
        return "?"
    return text if text.startswith("$") else f"${text}"


def strip_model_thinking(text: str) -> str:
    cleaned = _THINKING_BLOCK_RE.sub("", text)
    return cleaned.strip()


def has_items_section(text: str) -> bool:
    return bool(re.search(r"(?:ITEM\s+DETAILS|SIMILAR\s+ITEMS)", text, re.IGNORECASE))


def _escape_markdown_dollars(text: str) -> str:
    """Escape bare $ so Gradio/markdown does not treat prices as math."""
    return re.sub(r"(?<!\\)\$(?!\$)", r"\\$", text)


def process_response(response: str) -> str:
    if not response:
        logger.warning("Empty response received")
        return (
            "## Fashion Analysis\n\n"
            "No detailed analysis was generated. See the catalog match below."
        )

    processed = strip_model_thinking(response)
    if processed.startswith("Error generating response:"):
        return f"## Fashion Analysis\n\n{processed}"

    rejection_phrases = [
        "I'm not able to provide",
        "I cannot provide",
        "I apologize, but I cannot",
        "I don't feel comfortable",
        "violated our content policy",
    ]

    if any(phrase in processed for phrase in rejection_phrases):
        logger.warning("Model rejected the request, extracting item details")
        items_section = None
        if "ITEM DETAILS:" in processed:
            items_section = processed.split("ITEM DETAILS:", 1)[1].strip()
        elif "SIMILAR ITEMS:" in processed:
            items_section = processed.split("SIMILAR ITEMS:", 1)[1].strip()
        if items_section:
            items_section = _ITEMS_SECTION_RE.sub("", items_section).strip()
            formatted = re.sub(r"^\* ", "- ", items_section, flags=re.MULTILINE)
            return (
                "## Fashion Analysis\n\n"
                "Here are the items detected in your image:\n\n"
                + _escape_markdown_dollars(formatted)
            )
        return _escape_markdown_dollars(processed)

    # Drop catalog sections — shown separately in the hub / Gradio catalog panel.
    processed = _ITEMS_SECTION_RE.sub("", processed).strip()
    processed = re.sub(r"\n{3,}", "\n\n", processed)
    processed = re.sub(r"^\* ", "- ", processed, flags=re.MULTILINE)

    if not processed:
        return "## Fashion Analysis\n\nAnalysis could not be generated."

    if not re.match(r"^#{1,3}\s", processed):
        processed = f"## Fashion Analysis\n\n{processed}"

    return _escape_markdown_dollars(processed)


def catalog_table_markdown(items) -> str:
    if items is None or len(items) == 0:
        return "_No catalog rows for this match._"
    lines = ["| Item | Price | Link |", "| --- | --- | --- |"]
    for _, row in items.iterrows():
        name = str(row.get("Item Name", ""))
        price = format_price(row.get("Price", "?"))
        link = str(row.get("Link", ""))
        link_md = f"[link]({link})" if link and link != "nan" else ""
        lines.append(f"| {name} | {price} | {link_md} |")
    return "\n".join(lines)
