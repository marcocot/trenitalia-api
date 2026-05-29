"""Pydantic models exposed by the library.

The Italian API keys are mapped to snake_case English field names via
``Field(alias=...)``. Models are frozen — they're value objects, not
mutable state — and accept both alias and canonical names so they can
be constructed from raw API payloads or from hand-built dicts in tests.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

StopKind = Literal["P", "F", "A"]
"""``P`` = departure (Partenza), ``F`` = intermediate (Fermata), ``A`` = arrival (Arrivo)."""


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True, extra="ignore")


class TrainStop(_FrozenModel):
    """A single stop on a train's itinerary."""

    station: str = Field(alias="stazione")
    station_id: str = Field(alias="id")
    kind: StopKind = Field(alias="tipoFermata")
    progressive: int = Field(alias="progressivo", default=0)

    scheduled_time: int | None = Field(alias="programmata", default=None)
    actual_time: int | None = Field(alias="effettiva", default=None)
    actual_kind: int | None = Field(alias="actualFermataType", default=None)

    arrival_delay: int | None = Field(alias="ritardoArrivo", default=None)
    departure_delay: int | None = Field(alias="ritardoPartenza", default=None)
    delay: int | None = Field(alias="ritardo", default=None)

    scheduled_arrival_platform: str | None = Field(
        alias="binarioProgrammatoArrivoDescrizione", default=None
    )
    actual_arrival_platform: str | None = Field(
        alias="binarioEffettivoArrivoDescrizione", default=None
    )
    scheduled_departure_platform: str | None = Field(
        alias="binarioProgrammatoPartenzaDescrizione", default=None
    )
    actual_departure_platform: str | None = Field(
        alias="binarioEffettivoPartenzaDescrizione", default=None
    )


class TrainSearchResult(_FrozenModel):
    """Result of the autocomplete lookup — enough to fetch the live status."""

    train_number: int
    train_id: str
    timestamp: int
    origin: str


class TrainStatus(_FrozenModel):
    """Live train status returned by ``andamentoTreno``."""

    train_number: int = Field(alias="numeroTreno")
    train_label: str | None = Field(alias="compNumeroTreno", default=None)
    train_type: str | None = Field(alias="compTipologiaTreno", default=None)

    origin: str = Field(alias="origine")
    destination: str = Field(alias="destinazione")

    running: bool = Field(alias="circolante", default=False)
    arrived: bool = Field(alias="arrivato", default=False)
    not_departed: bool = Field(alias="nonPartito", default=False)

    delay: int = Field(alias="ritardo", default=0)
    delay_text: list[str] | None = Field(alias="compRitardo", default=None)

    scheduled_departure: str | None = Field(alias="compOrarioPartenzaZero", default=None)
    scheduled_arrival: str | None = Field(alias="compOrarioArrivoZero", default=None)

    last_detected_station: str | None = Field(alias="stazioneUltimoRilevamento", default=None)
    last_detected_time: str | None = Field(alias="compOraUltimoRilevamento", default=None)

    stops: list[TrainStop] = Field(alias="fermate", default_factory=list)


class ServiceAlert(_FrozenModel):
    """A single news / disruption item from the infomobility feed."""

    title: str
    body_html: str
    published_on: date
    is_priority: bool

    @field_validator("title", "body_html", mode="before")
    @classmethod
    def _strip_strings(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class StationMatch(_FrozenModel):
    """One entry of the station autocomplete result."""

    name: str
    station_id: str


class StationDetail(_FrozenModel):
    """Static information about a station."""

    station_id: str = Field(alias="codiceStazione")
    region_id: int = Field(alias="codReg")
    latitude: float = Field(alias="lat")
    longitude: float = Field(alias="lon")
    name: str
    short_name: str
    label: str

    @model_validator(mode="before")
    @classmethod
    def _flatten_localita(cls, data: object) -> object:
        if isinstance(data, dict) and isinstance(data.get("localita"), dict):
            loc = data["localita"]
            return {
                **data,
                "name": loc.get("nomeLungo", ""),
                "short_name": loc.get("nomeBreve", ""),
                "label": loc.get("label", ""),
            }
        return data


class StationTrain(_FrozenModel):
    """One row of a station's departures or arrivals timetable.

    Fields specific to either side (e.g. ``origin`` for arrivals,
    ``destination`` for departures, the various ``scheduled_*`` and
    ``*_platform`` couples) are optional and populated only where the
    upstream payload provides them.
    """

    train_number: int = Field(alias="numeroTreno")
    train_label: str = Field(alias="compNumeroTreno")
    category: str = Field(alias="categoria")
    train_type: str | None = Field(alias="compTipologiaTreno", default=None)

    delay: int = Field(alias="ritardo", default=0)
    running: bool = Field(alias="circolante", default=False)
    arrived: bool = Field(alias="arrivato", default=False)
    not_departed: bool = Field(alias="nonPartito", default=False)
    in_station: bool = Field(alias="inStazione", default=False)

    origin: str | None = Field(alias="origine", default=None)
    destination: str | None = Field(alias="destinazione", default=None)

    scheduled_departure: str | None = Field(alias="compOrarioPartenza", default=None)
    scheduled_arrival: str | None = Field(alias="compOrarioArrivo", default=None)

    scheduled_departure_platform: str | None = Field(
        alias="binarioProgrammatoPartenzaDescrizione", default=None
    )
    actual_departure_platform: str | None = Field(
        alias="binarioEffettivoPartenzaDescrizione", default=None
    )
    scheduled_arrival_platform: str | None = Field(
        alias="binarioProgrammatoArrivoDescrizione", default=None
    )
    actual_arrival_platform: str | None = Field(
        alias="binarioEffettivoArrivoDescrizione", default=None
    )

    last_detection: int | None = Field(alias="ultimoRilev", default=None)
