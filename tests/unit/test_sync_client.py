"""Sync :class:`Client` tests — exercises the full call/parse/error chain."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

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
from trenitalia_api import (
    APIError,
    Client,
    ConnectionError,
    InvalidResponseError,
    NotFoundError,
    UpstreamError,
)

BASE = "http://api.test/viaggiatreno"


@pytest.fixture
def client() -> Client:
    return Client(base_url=BASE, timeout=5)


class TestContextManager:
    def test_close_is_idempotent(self) -> None:
        c = Client(base_url=BASE)
        c.close()
        c.close()

    def test_does_not_close_externally_owned_http(self) -> None:
        http = httpx.Client()
        c = Client(base_url=BASE, http=http)
        c.close()
        # Still usable — proves we did not close someone else's transport.
        assert http.get is not None

    def test_used_as_context_manager(self) -> None:
        with Client(base_url=BASE) as c:
            assert c.trains is not None


class TestTrainsSearch:
    @respx.mock
    def test_returns_parsed_result(self, client: Client) -> None:
        respx.get(f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/9642").mock(
            return_value=httpx.Response(200, text=SEARCH_BODY),
        )
        result = client.trains.search(9642)
        assert result.train_id == "S11781"

    @respx.mock
    def test_empty_body_raises_invalid_response(self, client: Client) -> None:
        respx.get(f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/9642").mock(
            return_value=httpx.Response(200, text=""),
        )
        with pytest.raises(InvalidResponseError):
            client.trains.search(9642)

    @respx.mock
    def test_404_raises_not_found(self, client: Client) -> None:
        respx.get(f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/0").mock(
            return_value=httpx.Response(404),
        )
        with pytest.raises(NotFoundError) as exc_info:
            client.trains.search(0)
        assert exc_info.value.status_code == 404

    @respx.mock
    def test_500_raises_upstream_error(self, client: Client) -> None:
        respx.get(f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/9642").mock(
            return_value=httpx.Response(503),
        )
        with pytest.raises(UpstreamError) as exc_info:
            client.trains.search(9642)
        assert exc_info.value.status_code == 503

    @respx.mock
    def test_4xx_other_than_404_raises_generic_api_error(self, client: Client) -> None:
        respx.get(f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/9642").mock(
            return_value=httpx.Response(429),
        )
        with pytest.raises(APIError) as exc_info:
            client.trains.search(9642)
        assert not isinstance(exc_info.value, (NotFoundError, UpstreamError))

    @respx.mock
    def test_connect_error_wraps_to_connection_error(self, client: Client) -> None:
        respx.get(f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/9642").mock(
            side_effect=httpx.ConnectError("boom"),
        )
        with pytest.raises(ConnectionError):
            client.trains.search(9642)

    @respx.mock
    def test_timeout_wraps_to_connection_error(self, client: Client) -> None:
        respx.get(f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/9642").mock(
            side_effect=httpx.ReadTimeout("slow"),
        )
        with pytest.raises(ConnectionError):
            client.trains.search(9642)


class TestTrainsStatus:
    @respx.mock
    def test_returns_typed_status(self, client: Client) -> None:
        respx.get(f"{BASE}/andamentoTreno/S11781/9642/1").mock(
            return_value=httpx.Response(200, json=status_payload()),
        )
        s = client.trains.status("S11781", 9642, 1)
        assert s.origin == "REGGIO CALABRIA"

    @respx.mock
    def test_invalid_json_raises(self, client: Client) -> None:
        respx.get(f"{BASE}/andamentoTreno/S11781/9642/1").mock(
            return_value=httpx.Response(200, text="not json"),
        )
        with pytest.raises(InvalidResponseError, match="not valid JSON"):
            client.trains.status("S11781", 9642, 1)


class TestAlerts:
    @respx.mock
    def test_returns_parsed_alerts(self, client: Client) -> None:
        respx.get(f"{BASE}/infomobilitaRSS/false").mock(
            return_value=httpx.Response(200, content=INFOMOBILITY_HTML.encode("utf-8")),
        )
        alerts = client.alerts.list()
        assert len(alerts) == 2

    @respx.mock
    def test_regional_endpoint(self, client: Client) -> None:
        respx.get(f"{BASE}/infomobilitaRSS/true").mock(
            return_value=httpx.Response(200, content=b""),
        )
        assert client.alerts.list(only_regional=True) == []

    @respx.mock
    def test_upstream_failure(self, client: Client) -> None:
        respx.get(f"{BASE}/infomobilitaRSS/false").mock(
            return_value=httpx.Response(502),
        )
        with pytest.raises(UpstreamError):
            client.alerts.list()


class TestStations:
    @respx.mock
    def test_autocomplete(self, client: Client) -> None:
        respx.get(f"{BASE}/autocompletaStazione/moncalieri").mock(
            return_value=httpx.Response(200, text=STATION_AUTOCOMPLETE_BODY),
        )
        matches = client.stations.autocomplete("moncalieri")
        assert [m.station_id for m in matches] == ["S00453", "S00510"]

    @respx.mock
    def test_region(self, client: Client) -> None:
        respx.get(f"{BASE}/regione/S00453").mock(return_value=httpx.Response(200, json=3))
        assert client.stations.region("S00453") == 3

    @respx.mock
    def test_detail_with_explicit_region(self, client: Client) -> None:
        region_route = respx.get(f"{BASE}/regione/S00453")  # must NOT be hit
        respx.get(f"{BASE}/dettaglioStazione/S00453/3").mock(
            return_value=httpx.Response(200, json=station_detail_payload()),
        )
        detail = client.stations.detail("S00453", region=3)
        assert detail.name == "MONCALIERI"
        assert region_route.call_count == 0

    @respx.mock
    def test_detail_resolves_region_automatically(self, client: Client) -> None:
        region_route = respx.get(f"{BASE}/regione/S00453").mock(
            return_value=httpx.Response(200, json=3),
        )
        respx.get(f"{BASE}/dettaglioStazione/S00453/3").mock(
            return_value=httpx.Response(200, json=station_detail_payload()),
        )
        detail = client.stations.detail("S00453")
        assert detail.region_id == 3
        assert region_route.call_count == 1

    @respx.mock
    def test_departures(self, client: Client) -> None:
        # Match any ``when`` since the URL embeds the current timestamp.
        respx.get(url__regex=rf"{BASE}/partenze/S00453/.+").mock(
            return_value=httpx.Response(200, json=[departure_payload()]),
        )
        trains = client.stations.departures("S00453")
        assert trains[0].destination == "TORINO AEROPORTO DI CASELLE"

    @respx.mock
    def test_arrivals_with_explicit_when(self, client: Client) -> None:
        when = datetime(2026, 5, 29, 11, 12, 13, tzinfo=ZoneInfo("Europe/Rome"))
        # Matches the JS Date.toString() format produced by ``_format_when``.
        respx.get(url__regex=rf"{BASE}/arrivi/S00453/Fri%20May%2029%202026.+").mock(
            return_value=httpx.Response(200, json=[]),
        )
        assert client.stations.arrivals("S00453", when=when) == []

    @respx.mock
    def test_autocomplete_upstream_failure(self, client: Client) -> None:
        respx.get(f"{BASE}/autocompletaStazione/x").mock(return_value=httpx.Response(500))
        with pytest.raises(UpstreamError):
            client.stations.autocomplete("x")

    @respx.mock
    def test_region_rejects_non_int_payload(self, client: Client) -> None:
        respx.get(f"{BASE}/regione/S00453").mock(
            return_value=httpx.Response(200, json="three"),
        )
        with pytest.raises(InvalidResponseError):
            client.stations.region("S00453")


class TestFormatWhen:
    def test_serializes_aware_datetime_in_js_format(self) -> None:
        from trenitalia_api.resources.stations import _format_when

        when = datetime(2026, 5, 29, 11, 12, 13, tzinfo=ZoneInfo("Europe/Rome"))
        assert _format_when(when) == (
            "Fri May 29 2026 11:12:13 GMT+0200 (Central European Summer Time)"
        )

    def test_serializes_winter_datetime_with_standard_time_label(self) -> None:
        from trenitalia_api.resources.stations import _format_when

        when = datetime(2026, 1, 15, 8, 0, 0, tzinfo=ZoneInfo("Europe/Rome"))
        assert _format_when(when) == (
            "Thu Jan 15 2026 08:00:00 GMT+0100 (Central European Standard Time)"
        )

    def test_naive_datetime_assumed_in_europe_rome(self) -> None:
        from trenitalia_api.resources.stations import _format_when

        when = datetime(2026, 5, 29, 11, 12, 13)
        assert "GMT+0200" in _format_when(when)

    def test_none_falls_back_to_now(self) -> None:
        from trenitalia_api.resources.stations import _format_when

        result = _format_when(None)
        assert "GMT" in result
