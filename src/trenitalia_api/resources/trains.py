"""``trains.*`` resource: search + live status."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from .. import _endpoints
from .._errors import check_response, map_transport_error
from .._parsing import parse_search_response, parse_status_response
from ..exceptions import InvalidResponseError

if TYPE_CHECKING:
    from ..models import TrainSearchResult, TrainStatus


class TrainsResource:
    """Sync access to train search + status."""

    def __init__(self, http: httpx.Client, base_url: str) -> None:
        self._http = http
        self._base_url = base_url

    def search(self, train_number: str | int) -> TrainSearchResult:
        """Resolve a train number into ``(train_id, train_number, timestamp, origin)``."""
        url = _endpoints.search_train(self._base_url, train_number)
        try:
            response = self._http.get(url)
        except httpx.HTTPError as exc:
            raise map_transport_error(exc) from exc
        check_response(response)
        if not response.text.strip():
            raise InvalidResponseError("search returned an empty body")
        return parse_search_response(response.text)

    def status(self, train_id: str, train_number: int, timestamp: int) -> TrainStatus:
        """Fetch live status for a given train triple."""
        url = _endpoints.train_status(self._base_url, train_id, train_number, timestamp)
        try:
            response = self._http.get(url)
        except httpx.HTTPError as exc:
            raise map_transport_error(exc) from exc
        check_response(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise InvalidResponseError(f"status response was not valid JSON: {exc}") from exc
        return parse_status_response(payload)


class AsyncTrainsResource:
    """Async equivalent of :class:`TrainsResource`."""

    def __init__(self, http: httpx.AsyncClient, base_url: str) -> None:
        self._http = http
        self._base_url = base_url

    async def search(self, train_number: str | int) -> TrainSearchResult:
        url = _endpoints.search_train(self._base_url, train_number)
        try:
            response = await self._http.get(url)
        except httpx.HTTPError as exc:
            raise map_transport_error(exc) from exc
        check_response(response)
        if not response.text.strip():
            raise InvalidResponseError("search returned an empty body")
        return parse_search_response(response.text)

    async def status(self, train_id: str, train_number: int, timestamp: int) -> TrainStatus:
        url = _endpoints.train_status(self._base_url, train_id, train_number, timestamp)
        try:
            response = await self._http.get(url)
        except httpx.HTTPError as exc:
            raise map_transport_error(exc) from exc
        check_response(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise InvalidResponseError(f"status response was not valid JSON: {exc}") from exc
        return parse_status_response(payload)
