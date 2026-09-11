"""LinkedIn profile extraction — mock JSON, ProxyCurl, or pasted text."""

from __future__ import annotations

import json
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
        logger.info("Using cached mock data: %s", config.MOCK_DATA_PATH.name)
        return json.loads(config.MOCK_DATA_PATH.read_text(encoding="utf-8"))

    logger.info("Downloading mock LinkedIn JSON…")
    response = requests.get(config.MOCK_DATA_URL, timeout=60)
    response.raise_for_status()
    config.MOCK_DATA_PATH.write_bytes(response.content)
    return response.json()


def profile_from_text(text: str) -> dict[str, Any]:
    """Build a minimal profile dict from pasted JSON or plain text."""
    raw = (text or "").strip()
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict) and obj:
            return _clean_profile(obj)
        if isinstance(obj, list) and obj:
            return _clean_profile({"experiences": obj})
    except Exception:
        pass
    return _clean_profile({"summary": raw, "source": "pasted_text"})


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
        logger.info(
            "ProxyCurl responded in %.2fs (status=%s)",
            time.time() - start,
            response.status_code,
        )

        if response.status_code != 200:
            logger.error(
                "ProxyCurl failed: %s %s",
                response.status_code,
                response.text[:200],
            )
            return {}

        return _clean_profile(response.json())
    except Exception as e:
        logger.error("Error in extract_linkedin_profile: %s", e)
        return {}


def resolve_profile(
    linkedin_url: str = "",
    api_key: Optional[str] = None,
    pasted_text: str = "",
) -> tuple[dict[str, Any], str]:
    """
    Cascade: ProxyCurl (URL+key) → pasted text → mock sample.

    Returns (profile_dict, source) where source is proxycurl|pasted|mock.
    """
    url = (linkedin_url or "").strip()
    key = (api_key if api_key is not None else config.PROXYCURL_API_KEY) or ""
    key = key.strip()
    pasted = (pasted_text or "").strip()

    if url and "linkedin.com" in url.lower() and key:
        data = extract_linkedin_profile(url, key, mock=False)
        if data:
            logger.info("Profile resolved via ProxyCurl")
            return data, "proxycurl"
        logger.warning("ProxyCurl failed; trying pasted text / mock")

    if pasted:
        data = profile_from_text(pasted)
        if data:
            logger.info("Profile resolved from pasted text")
            return data, "pasted"

    data = extract_linkedin_profile(config.DEFAULT_MOCK_URL, None, mock=True)
    logger.info("Profile resolved via mock sample")
    return data or {}, "mock"
