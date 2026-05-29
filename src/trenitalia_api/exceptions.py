"""Exception hierarchy.

All errors raised by this library subclass :class:`TrenitaliaError`, so a
single ``except TrenitaliaError`` catches everything.
"""

from __future__ import annotations


class TrenitaliaError(Exception):
    """Base class for every error raised by this library."""


class APIError(TrenitaliaError):
    """The upstream API returned a non-2xx response."""

    def __init__(self, message: str, *, status_code: int, url: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.url = url


class NotFoundError(APIError):
    """4xx response signalling the resource doesn't exist (typically 404)."""


class UpstreamError(APIError):
    """5xx response — ViaggiaTreno is in trouble."""


class ConnectionError(TrenitaliaError):
    """Network failure, DNS failure, or timeout reaching the upstream.

    Intentionally shadows the built-in for users who import this module
    directly; library code uses :exc:`builtins.ConnectionError` only when
    explicitly qualified.
    """


class InvalidResponseError(TrenitaliaError):
    """The response body could not be parsed into the expected shape."""
