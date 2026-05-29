"""Async + sync Python client for the public ViaggiaTreno (Trenitalia) API."""

from ._endpoints import DEFAULT_BASE_URL
from .client import AsyncClient, Client
from .exceptions import (
    APIError,
    ConnectionError,
    InvalidResponseError,
    NotFoundError,
    TrenitaliaError,
    UpstreamError,
)
from .models import (
    ServiceAlert,
    StationDetail,
    StationMatch,
    StationTrain,
    StopKind,
    TrainSearchResult,
    TrainStatus,
    TrainStop,
)

__version__ = "0.2.0"

__all__ = [
    "DEFAULT_BASE_URL",
    "APIError",
    "AsyncClient",
    "Client",
    "ConnectionError",
    "InvalidResponseError",
    "NotFoundError",
    "ServiceAlert",
    "StationDetail",
    "StationMatch",
    "StationTrain",
    "StopKind",
    "TrainSearchResult",
    "TrainStatus",
    "TrainStop",
    "TrenitaliaError",
    "UpstreamError",
]
