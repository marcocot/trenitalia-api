"""URL builder tests."""

from __future__ import annotations

from trenitalia_api import _endpoints

BASE = "http://api.test/viaggiatreno"


def test_search_url() -> None:
    assert _endpoints.search_train(BASE, 9642) == f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/9642"


def test_search_url_accepts_string() -> None:
    assert _endpoints.search_train(BASE, "9642") == f"{BASE}/cercaNumeroTrenoTrenoAutocomplete/9642"


def test_status_url() -> None:
    assert (
        _endpoints.train_status(BASE, "S11781", 9642, 1772665200000)
        == f"{BASE}/andamentoTreno/S11781/9642/1772665200000"
    )


def test_infomobility_url_default_national() -> None:
    assert _endpoints.infomobility_news(BASE) == f"{BASE}/infomobilitaRSS/false"


def test_infomobility_url_regional() -> None:
    assert _endpoints.infomobility_news(BASE, only_regional=True) == f"{BASE}/infomobilitaRSS/true"


def test_station_autocomplete_url() -> None:
    assert (
        _endpoints.station_autocomplete(BASE, "moncalieri")
        == f"{BASE}/autocompletaStazione/moncalieri"
    )


def test_station_autocomplete_url_encodes_spaces_and_special_chars() -> None:
    assert (
        _endpoints.station_autocomplete(BASE, "torino porta n.")
        == f"{BASE}/autocompletaStazione/torino%20porta%20n."
    )


def test_station_region_url() -> None:
    assert _endpoints.station_region(BASE, "S00453") == f"{BASE}/regione/S00453"


def test_station_detail_url() -> None:
    assert _endpoints.station_detail(BASE, "S00453", 3) == f"{BASE}/dettaglioStazione/S00453/3"


def test_station_departures_url_encodes_when() -> None:
    when = "Fri May 29 2026 11:12:13 GMT+0200 (Central European Summer Time)"
    url = _endpoints.station_departures(BASE, "S00453", when)
    assert url.startswith(f"{BASE}/partenze/S00453/Fri%20May%2029%202026")
    assert "%20GMT%2B0200" in url


def test_station_arrivals_url_encodes_when() -> None:
    when = "Fri May 29 2026 11:12:13 GMT+0200 (Central European Summer Time)"
    url = _endpoints.station_arrivals(BASE, "S00453", when)
    assert url.startswith(f"{BASE}/arrivi/S00453/Fri%20May%2029%202026")
