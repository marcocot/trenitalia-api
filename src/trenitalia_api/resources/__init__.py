"""Resource classes accessed via ``client.<resource>``."""

from .infomobility import AsyncInfomobilityResource, InfomobilityResource
from .trains import AsyncTrainsResource, TrainsResource

__all__ = [
    "AsyncInfomobilityResource",
    "AsyncTrainsResource",
    "InfomobilityResource",
    "TrainsResource",
]
