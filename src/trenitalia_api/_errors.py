"""Internal helpers translating ``httpx`` errors into our exception hierarchy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import APIError, ConnectionError, NotFoundError, UpstreamError

if TYPE_CHECKING:
    import httpx


def map_transport_error(exc: httpx.HTTPError) -> ConnectionError:
    """Wrap any transport-level ``httpx`` error in :exc:`ConnectionError`."""
    return ConnectionError(f"{type(exc).__name__}: {exc}")


def check_response(response: httpx.Response) -> None:
    """Raise the appropriate exception if ``response`` is not 2xx."""
    if response.is_success:
        return

    status = response.status_code
    url = str(response.request.url) if response.request is not None else None

    cls: type[APIError]
    if status == 404:
        cls = NotFoundError
    elif 500 <= status < 600:
        cls = UpstreamError
    else:
        cls = APIError

    raise cls(f"HTTP {status} from {url or '<unknown>'}", status_code=status, url=url)
