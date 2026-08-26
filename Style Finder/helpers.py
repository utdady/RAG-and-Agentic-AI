"""Utility helpers for Style Finder."""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


def get_all_items_for_image(image_url, dataset):
    related_items = dataset[dataset["Image URL"] == image_url]
    logger.info("Found %s items for image URL", len(related_items))
    return related_items


def process_response(response: str) -> str:
    if not response:
        logger.warning("Empty response received")
        return (
            "# Fashion Analysis\n\n"
            "No detailed analysis was generated. Please refer to the item details below."
        )

    rejection_phrases = [
        "I'm not able to provide",
        "I cannot provide",
        "I apologize, but I cannot",
        "I don't feel comfortable",
        "violated our content policy",
    ]

    if any(phrase in response for phrase in rejection_phrases):
        logger.warning("Model rejected the request, extracting item details")
        items_section = None
        if "ITEM DETAILS:" in response:
            items_section = "## Item Details\n\n" + response.split("ITEM DETAILS:")[1].strip()
        elif "SIMILAR ITEMS:" in response:
            items_section = "## Similar Items\n\n" + response.split("SIMILAR ITEMS:")[1].strip()
        if items_section:
            formatted = re.sub(r"^\* ", "- ", items_section, flags=re.MULTILINE)
            return (
                "# Fashion Analysis\n\n"
                "Here are the items detected in your image:\n\n" + formatted
            )
        return response.replace("$", "\\$")

    processed = response.replace("$", "\\$")
    processed = processed.replace("ITEM DETAILS:", "## Item Details")
    processed = processed.replace("SIMILAR ITEMS:", "## Similar Items")
    if not processed.startswith("#"):
        processed = "# Fashion Analysis\n\n" + processed
    processed = re.sub(r"^\* ", "- ", processed, flags=re.MULTILINE)
    return processed


def catalog_table_markdown(items) -> str:
    if items is None or len(items) == 0:
        return "_No catalog rows for this match._"
    lines = ["| Item | Price | Link |", "| --- | --- | --- |"]
    for _, row in items.iterrows():
        name = str(row.get("Item Name", ""))
        price = str(row.get("Price", ""))
        link = str(row.get("Link", ""))
        link_md = f"[link]({link})" if link and link != "nan" else ""
        lines.append(f"| {name} | {price} | {link_md} |")
    return "\n".join(lines)
