"""Top-level :class:`Client` and :class:`AsyncClient`.

Both share the same surface (resource accessors, ``close()``, context
manager). Pick whichever fits your event-loop story.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

import httpx

from ._endpoints import DEFAULT_BASE_URL
from .resources import (
    AsyncInfomobilityResource,
    AsyncStationsResource,
    AsyncTrainsResource,
    InfomobilityResource,
    StationsResource,
    TrainsResource,
)

if TYPE_CHECKING:
    from types import TracebackType

DEFAULT_TIMEOUT: float = 10.0


class Client:
    """Synchronous client.

    Example::

        with Client() as c:
            search = c.trains.search(9642)
            status = c.trains.status(search.train_id, search.train_number, search.timestamp)
    """

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._http = http if http is not None else httpx.Client(timeout=timeout)
        self._owns_http = http is None

        self.trains = TrainsResource(self._http, self._base_url)
        self.alerts = InfomobilityResource(self._http, self._base_url)
        self.stations = StationsResource(self._http, self._base_url)

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()


class AsyncClient:
    """Asynchronous client.

    Example::

        async with AsyncClient() as c:
            search = await c.trains.search(9642)
            status = await c.trains.status(
                search.train_id, search.train_number, search.timestamp,
            )
    """

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._http = http if http is not None else httpx.AsyncClient(timeout=timeout)
        self._owns_http = http is None

        self.trains = AsyncTrainsResource(self._http, self._base_url)
        self.alerts = AsyncInfomobilityResource(self._http, self._base_url)
        self.stations = AsyncStationsResource(self._http, self._base_url)

    async def aclose(self) -> None:
        if self._owns_http:
            await self._http.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()
