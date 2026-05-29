"""Integration tests against the real ViaggiaTreno API.

Skipped by default. Run with::

    uv run pytest tests/integration -m integration --no-cov

These tests assume network connectivity and that the upstream answers.
They tolerate temporary upstream failures by skipping rather than
failing — we don't want a Trenitalia outage to break our CI.
"""

from __future__ import annotations

import pytest

from trenitalia_api import AsyncClient, Client, TrenitaliaError

pytestmark = pytest.mark.integration


# A historically-stable Frecciarossa run; even if it's cancelled today,
# the autocomplete should still resolve the identifier.
KNOWN_TRAIN_NUMBER = 9520


class TestSync:
    def test_search_returns_a_real_result(self) -> None:
        with Client() as c:
            try:
                result = c.trains.search(KNOWN_TRAIN_NUMBER)
            except TrenitaliaError as exc:
                pytest.skip(f"upstream unavailable: {exc}")

        assert result.train_number == KNOWN_TRAIN_NUMBER
        assert result.train_id
        assert result.timestamp > 0

    def test_alerts_returns_a_list(self) -> None:
        with Client() as c:
            try:
                alerts = c.alerts.list()
            except TrenitaliaError as exc:
                pytest.skip(f"upstream unavailable: {exc}")
        assert isinstance(alerts, list)


class TestAsync:
    async def test_search_returns_a_real_result(self) -> None:
        async with AsyncClient() as c:
            try:
                result = await c.trains.search(KNOWN_TRAIN_NUMBER)
            except TrenitaliaError as exc:
                pytest.skip(f"upstream unavailable: {exc}")
        assert result.train_number == KNOWN_TRAIN_NUMBER
