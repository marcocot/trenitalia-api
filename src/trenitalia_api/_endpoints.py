"""URL builders for the ViaggiaTreno endpoints we support.

Kept as plain functions so they can be unit-tested without spinning up
an HTTP client.
"""

from __future__ import annotations

from urllib.parse import quote

DEFAULT_BASE_URL = "http://www.viaggiatreno.it/infomobilita/resteasy/viaggiatreno"


def search_train(base_url: str, train_number: str | int) -> str:
    return f"{base_url}/cercaNumeroTrenoTrenoAutocomplete/{train_number}"


def train_status(base_url: str, train_id: str, train_number: int, timestamp: int) -> str:
    return f"{base_url}/andamentoTreno/{train_id}/{train_number}/{timestamp}"


def infomobility_news(base_url: str, *, only_regional: bool = False) -> str:
    flag = "true" if only_regional else "false"
    return f"{base_url}/infomobilitaRSS/{flag}"


def station_autocomplete(base_url: str, query: str) -> str:
    return f"{base_url}/autocompletaStazione/{quote(query, safe='')}"


def station_region(base_url: str, station_id: str) -> str:
    return f"{base_url}/regione/{station_id}"


def station_detail(base_url: str, station_id: str, region: int) -> str:
    return f"{base_url}/dettaglioStazione/{station_id}/{region}"


def station_departures(base_url: str, station_id: str, when: str) -> str:
    return f"{base_url}/partenze/{station_id}/{quote(when, safe='')}"


def station_arrivals(base_url: str, station_id: str, when: str) -> str:
    return f"{base_url}/arrivi/{station_id}/{quote(when, safe='')}"
