"""``alerts.*`` resource: service news and disruptions feed."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from .. import _endpoints
from .._errors import check_response, map_transport_error
from .._parsing import parse_infomobility_response

if TYPE_CHECKING:
    from ..models import ServiceAlert


class InfomobilityResource:
    """Sync access to the infomobility news feed."""

    def __init__(self, http: httpx.Client, base_url: str) -> None:
        self._http = http
        self._base_url = base_url

    def list(self, *, only_regional: bool = False) -> list[ServiceAlert]:
        """Fetch active service alerts. ``only_regional=True`` narrows to local events."""
        url = _endpoints.infomobility_news(self._base_url, only_regional=only_regional)
        try:
            response = self._http.get(url)
        except httpx.HTTPError as exc:
            raise map_transport_error(exc) from exc
        check_response(response)
        return parse_infomobility_response(_decoded(response))


class AsyncInfomobilityResource:
    """Async equivalent of :class:`InfomobilityResource`."""

    def __init__(self, http: httpx.AsyncClient, base_url: str) -> None:
        self._http = http
        self._base_url = base_url

    async def list(self, *, only_regional: bool = False) -> list[ServiceAlert]:
        url = _endpoints.infomobility_news(self._base_url, only_regional=only_regional)
        try:
            response = await self._http.get(url)
        except httpx.HTTPError as exc:
            raise map_transport_error(exc) from exc
        check_response(response)
        return parse_infomobility_response(_decoded(response))


def _decoded(response: httpx.Response) -> str:
    """Force UTF-8 decoding — the upstream often serves no/wrong charset."""
    return response.content.decode("utf-8", errors="replace")
