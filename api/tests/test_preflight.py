from __future__ import annotations

from api.diagnostics.preflight import (
    check_catalog_sync,
    check_groq_env,
    check_require_groq_unit,
    check_runners_registered,
)


def test_catalog_in_sync_with_web():
    result = check_catalog_sync()
    assert result.ok, result.detail


def test_all_demos_have_runners():
    result = check_runners_registered()
    assert result.ok, result.detail


def test_require_groq_does_not_swallow_events():
    result = check_require_groq_unit()
    assert result.ok, result.detail


def test_groq_key_present_for_live():
    """Informational in CI without secrets — skip if no key."""
    result = check_groq_env()
    if not result.ok:
        import pytest

        pytest.skip(result.detail)
