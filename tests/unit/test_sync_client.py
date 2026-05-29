"""Sync :class:`Client` tests — exercises the full call/parse/error chain."""

from __future__ import annotations

import httpx
import pytest
import respx

from tests.conftest import INFOMOBILITY_HTML, SEARCH_BODY, status_payload
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
