"""Resource classes accessed via ``client.<resource>``."""

from .infomobility import AsyncInfomobilityResource, InfomobilityResource
from .stations import AsyncStationsResource, StationsResource
from .trains import AsyncTrainsResource, TrainsResource

__all__ = [
    "AsyncInfomobilityResource",
    "AsyncStationsResource",
    "AsyncTrainsResource",
    "InfomobilityResource",
    "StationsResource",
    "TrainsResource",
]
