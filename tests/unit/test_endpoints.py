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
