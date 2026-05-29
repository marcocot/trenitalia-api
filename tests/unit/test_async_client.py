"""Async :class:`AsyncClient` tests.

The full error chain is covered by the sync tests; here we just confirm
the async surface produces the same results and respects the awaited
contract for both happy and unhappy paths.
"""

from __future__ import annotations

import asyncio

import httpx
import pytest
import respx

from tests.conftest import (
    INFOMOBILITY_HTML,
    SEARCH_BODY,
    STATION_AUTOCOMPLETE_BODY,
    departure_payload,
    station_detail_payload,
    status_payload,
)
from trenitalia_api import AsyncClient, ConnectionError, NotFoundError, UpstreamError

BASE = "http://api.test/viaggiatreno"


@pytest.fixture
def aclient() -> AsyncClient:
    return AsyncClient(base_url=BASE, timeout=5)


class TestContextManager:
    async def test_aclose_does_not_close_externally_owned_http(self) -> None:
        http = httpx.AsyncClient()
        c = AsyncClient(base_url=BASE, http=http)
        await c.aclose()
        # Still usable.
        await http.aclose()

    async def test_used_as_async_context_manager(self) -> None:
        async with AsyncClient(base_url=BASE) as c:
            assert c.trains is not None


class TestTrainsSearch:
    @respx.mock
    async def test_returns_parsed_result(self, aclient: AsyncClient) -> None:
        respx.get(f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/9642").mock(
            return_value=httpx.Response(200, text=SEARCH_BODY),
        )
        result = await aclient.trains.search(9642)
        assert result.train_id == "S11781"

    @respx.mock
    async def test_404_raises(self, aclient: AsyncClient) -> None:
        respx.get(f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/0").mock(
            return_value=httpx.Response(404),
        )
        with pytest.raises(NotFoundError):
            await aclient.trains.search(0)

    @respx.mock
    async def test_5xx_raises(self, aclient: AsyncClient) -> None:
        respx.get(f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/9642").mock(
            return_value=httpx.Response(500),
        )
        with pytest.raises(UpstreamError):
            await aclient.trains.search(9642)

    @respx.mock
    async def test_connect_error_wraps(self, aclient: AsyncClient) -> None:
        respx.get(f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/9642").mock(
            side_effect=httpx.ConnectError("boom"),
        )
        with pytest.raises(ConnectionError):
            await aclient.trains.search(9642)


class TestTrainsStatus:
    @respx.mock
    async def test_returns_typed_status(self, aclient: AsyncClient) -> None:
        respx.get(f"{BASE}/andamentoTreno/S11781/9642/1").mock(
            return_value=httpx.Response(200, json=status_payload()),
        )
        s = await aclient.trains.status("S11781", 9642, 1)
        assert s.train_number == 9642


class TestAlerts:
    @respx.mock
    async def test_returns_parsed_alerts(self, aclient: AsyncClient) -> None:
        respx.get(f"{BASE}/infomobilitaRSS/false").mock(
            return_value=httpx.Response(200, content=INFOMOBILITY_HTML.encode("utf-8")),
        )
        alerts = await aclient.alerts.list()
        assert len(alerts) == 2

    @respx.mock
    async def test_connection_error(self, aclient: AsyncClient) -> None:
        respx.get(f"{BASE}/infomobilitaRSS/false").mock(
            side_effect=httpx.ReadTimeout("slow"),
        )
        with pytest.raises(ConnectionError):
            await aclient.alerts.list()


class TestStations:
    @respx.mock
    async def test_autocomplete(self, aclient: AsyncClient) -> None:
        respx.get(f"{BASE}/autocompletaStazione/moncalieri").mock(
            return_value=httpx.Response(200, text=STATION_AUTOCOMPLETE_BODY),
        )
        matches = await aclient.stations.autocomplete("moncalieri")
        assert [m.station_id for m in matches] == ["S00453", "S00510"]

    @respx.mock
    async def test_detail_resolves_region_automatically(self, aclient: AsyncClient) -> None:
        respx.get(f"{BASE}/regione/S00453").mock(return_value=httpx.Response(200, json=3))
        respx.get(f"{BASE}/dettaglioStazione/S00453/3").mock(
            return_value=httpx.Response(200, json=station_detail_payload()),
        )
        detail = await aclient.stations.detail("S00453")
        assert detail.region_id == 3

    @respx.mock
    async def test_departures(self, aclient: AsyncClient) -> None:
        respx.get(url__regex=rf"{BASE}/partenze/S00453/.+").mock(
            return_value=httpx.Response(200, json=[departure_payload()]),
        )
        trains = await aclient.stations.departures("S00453")
        assert trains[0].train_number == 26612


@respx.mock
async def test_parallel_fetches_via_gather(aclient: AsyncClient) -> None:
    respx.get(f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/9642").mock(
        return_value=httpx.Response(200, text=SEARCH_BODY),
    )
    respx.get(f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/1000").mock(
        return_value=httpx.Response(
            200,
            text="1000 - ROMA - 05/03/26|1000-S00001-1772665200000",
        ),
    )
    a, b = await asyncio.gather(aclient.trains.search(9642), aclient.trains.search(1000))
    assert a.train_number == 9642
    assert b.train_number == 1000
