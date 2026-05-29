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


# Stations endpoints. Torino Porta Nuova (S00219) has frequent traffic — a safe
# pick for non-empty timetables.
PORTA_NUOVA = "S00219"


class TestStations:
    def test_autocomplete_finds_moncalieri(self) -> None:
        with Client() as c:
            try:
                matches = c.stations.autocomplete("moncalieri")
            except TrenitaliaError as exc:
                pytest.skip(f"upstream unavailable: {exc}")
        codes = {m.station_id for m in matches}
        assert "S00453" in codes

    def test_detail_resolves_region(self) -> None:
        with Client() as c:
            try:
                detail = c.stations.detail("S00453")
            except TrenitaliaError as exc:
                pytest.skip(f"upstream unavailable: {exc}")
        assert detail.station_id == "S00453"
        assert detail.name.lower().startswith("moncalieri")

    def test_departures_returns_a_list(self) -> None:
        with Client() as c:
            try:
                trains = c.stations.departures(PORTA_NUOVA)
            except TrenitaliaError as exc:
                pytest.skip(f"upstream unavailable: {exc}")
        assert isinstance(trains, list)

    def test_arrivals_returns_a_list(self) -> None:
        with Client() as c:
            try:
                trains = c.stations.arrivals(PORTA_NUOVA)
            except TrenitaliaError as exc:
                pytest.skip(f"upstream unavailable: {exc}")
        assert isinstance(trains, list)
