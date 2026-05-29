"""``stations.*`` resource: autocomplete, detail, and live timetables."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

import httpx

from .. import _endpoints
from .._errors import check_response, map_transport_error
from .._parsing import (
    parse_station_autocomplete,
    parse_station_detail,
    parse_station_region,
    parse_station_trains,
)
from ..exceptions import InvalidResponseError

if TYPE_CHECKING:
    from ..models import StationDetail, StationMatch, StationTrain

_ROME = ZoneInfo("Europe/Rome")

_TZ_LONG_NAMES = {
    "CET": "Central European Standard Time",
    "CEST": "Central European Summer Time",
}


def _format_when(when: datetime | None) -> str:
    """Serialize a ``datetime`` in the JavaScript ``Date.toString()`` format.

    The upstream ``/partenze`` and ``/arrivi`` endpoints reject ISO 8601 and
    only accept strings shaped like::

        Fri May 29 2026 11:12:13 GMT+0200 (Central European Summer Time)
    """
    moment = when if when is not None else datetime.now(tz=_ROME)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=_ROME)

    head = moment.strftime("%a %b %d %Y %H:%M:%S")
    offset = moment.strftime("%z") or "+0000"
    short_tz = moment.tzname() or "UTC"
    long_tz = _TZ_LONG_NAMES.get(short_tz, short_tz)
    return f"{head} GMT{offset} ({long_tz})"


class StationsResource:
    """Sync access to station autocomplete, detail, and timetables."""

    def __init__(self, http: httpx.Client, base_url: str) -> None:
        self._http = http
        self._base_url = base_url

    def autocomplete(self, query: str) -> list[StationMatch]:
        """Resolve a partial station name into a list of ``(name, id)`` pairs."""
        url = _endpoints.station_autocomplete(self._base_url, query)
        response = self._get(url)
        return parse_station_autocomplete(response.text)

    def region(self, station_id: str) -> int:
        """Fetch the numeric region id a station belongs to."""
        url = _endpoints.station_region(self._base_url, station_id)
        response = self._get(url)
        return parse_station_region(self._json(response))

    def detail(self, station_id: str, *, region: int | None = None) -> StationDetail:
        """Fetch static station info; resolves ``region`` automatically if omitted."""
        resolved_region = region if region is not None else self.region(station_id)
        url = _endpoints.station_detail(self._base_url, station_id, resolved_region)
        response = self._get(url)
        return parse_station_detail(self._json(response))

    def departures(self, station_id: str, *, when: datetime | None = None) -> list[StationTrain]:
        """Live departures board for a station at a given instant (default: now)."""
        url = _endpoints.station_departures(self._base_url, station_id, _format_when(when))
        response = self._get(url)
        return parse_station_trains(self._json(response))

    def arrivals(self, station_id: str, *, when: datetime | None = None) -> list[StationTrain]:
        """Live arrivals board for a station at a given instant (default: now)."""
        url = _endpoints.station_arrivals(self._base_url, station_id, _format_when(when))
        response = self._get(url)
        return parse_station_trains(self._json(response))

    def _get(self, url: str) -> httpx.Response:
        try:
            response = self._http.get(url)
        except httpx.HTTPError as exc:
            raise map_transport_error(exc) from exc
        check_response(response)
        return response

    def _json(self, response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise InvalidResponseError(f"response was not valid JSON: {exc}") from exc


class AsyncStationsResource:
    """Async equivalent of :class:`StationsResource`."""

    def __init__(self, http: httpx.AsyncClient, base_url: str) -> None:
        self._http = http
        self._base_url = base_url

    async def autocomplete(self, query: str) -> list[StationMatch]:
        url = _endpoints.station_autocomplete(self._base_url, query)
        response = await self._get(url)
        return parse_station_autocomplete(response.text)

    async def region(self, station_id: str) -> int:
        url = _endpoints.station_region(self._base_url, station_id)
        response = await self._get(url)
        return parse_station_region(self._json(response))

    async def detail(self, station_id: str, *, region: int | None = None) -> StationDetail:
        resolved_region = region if region is not None else await self.region(station_id)
        url = _endpoints.station_detail(self._base_url, station_id, resolved_region)
        response = await self._get(url)
        return parse_station_detail(self._json(response))

    async def departures(
        self, station_id: str, *, when: datetime | None = None
    ) -> list[StationTrain]:
        url = _endpoints.station_departures(self._base_url, station_id, _format_when(when))
        response = await self._get(url)
        return parse_station_trains(self._json(response))

    async def arrivals(
        self, station_id: str, *, when: datetime | None = None
    ) -> list[StationTrain]:
        url = _endpoints.station_arrivals(self._base_url, station_id, _format_when(when))
        response = await self._get(url)
        return parse_station_trains(self._json(response))

    async def _get(self, url: str) -> httpx.Response:
        try:
            response = await self._http.get(url)
        except httpx.HTTPError as exc:
            raise map_transport_error(exc) from exc
        check_response(response)
        return response

    def _json(self, response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise InvalidResponseError(f"response was not valid JSON: {exc}") from exc
