"""LinkedIn profile extraction — mock JSON or optional ProxyCurl."""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

import requests

import config

logger = logging.getLogger(__name__)


def _clean_profile(data: dict[str, Any]) -> dict[str, Any]:
    cleaned = {
        k: v
        for k, v in data.items()
        if v not in ([], "", None) and k not in ["people_also_viewed", "certifications"]
    }
    if cleaned.get("groups"):
        for group_dict in cleaned["groups"]:
            if isinstance(group_dict, dict):
                group_dict.pop("profile_pic_url", None)
    return cleaned


def _load_mock() -> dict[str, Any]:
    config.MOCK_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if config.MOCK_DATA_PATH.exists() and config.MOCK_DATA_PATH.stat().st_size > 0:
        import json

        logger.info("Using cached mock data: %s", config.MOCK_DATA_PATH.name)
        return json.loads(config.MOCK_DATA_PATH.read_text(encoding="utf-8"))

    logger.info("Downloading mock LinkedIn JSON…")
    response = requests.get(config.MOCK_DATA_URL, timeout=60)
    response.raise_for_status()
    config.MOCK_DATA_PATH.write_bytes(response.content)
    return response.json()


def extract_linkedin_profile(
    linkedin_profile_url: str,
    api_key: Optional[str] = None,
    mock: bool = False,
) -> dict[str, Any]:
    """
    Extract LinkedIn profile data.

    mock=True → course JSON (cached under data/).
    mock=False → ProxyCurl API (requires api_key).
    """
    start = time.time()
    try:
        if mock:
            data = _load_mock()
            return _clean_profile(data)

        if not api_key:
            raise ValueError("ProxyCurl API key is required when mock is False.")

        logger.info("Extracting LinkedIn profile via ProxyCurl…")
        response = requests.get(
            "https://nubela.co/proxycurl/api/v2/linkedin",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "url": linkedin_profile_url,
                "fallback_to_cache": "on-error",
                "use_cache": "if-present",
                "skills": "include",
            },
            timeout=30,
        )
        logger.info("ProxyCurl responded in %.2fs (status=%s)", time.time() - start, response.status_code)

        if response.status_code != 200:
            logger.error("ProxyCurl failed: %s %s", response.status_code, response.text[:200])
            return {}

        return _clean_profile(response.json())
    except Exception as e:
        logger.error("Error in extract_linkedin_profile: %s", e)
        return {}
