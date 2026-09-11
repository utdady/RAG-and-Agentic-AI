from __future__ import annotations

import os

from api.adapters.common import hub_heavy_retrieval


def test_hub_heavy_retrieval_default_off(monkeypatch):
    monkeypatch.delenv("HUB_HEAVY_RETRIEVAL", raising=False)
    assert hub_heavy_retrieval() is False


def test_hub_heavy_retrieval_truthy(monkeypatch):
    for val in ("1", "true", "YES", "on"):
        monkeypatch.setenv("HUB_HEAVY_RETRIEVAL", val)
        assert hub_heavy_retrieval() is True


def test_hub_heavy_retrieval_falsy(monkeypatch):
    for val in ("0", "false", "no", ""):
        monkeypatch.setenv("HUB_HEAVY_RETRIEVAL", val)
        assert hub_heavy_retrieval() is False
