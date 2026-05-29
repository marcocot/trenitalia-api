"""Pydantic models exposed by the library.

The Italian API keys are mapped to snake_case English field names via
``Field(alias=...)``. Models are frozen — they're value objects, not
mutable state — and accept both alias and canonical names so they can
be constructed from raw API payloads or from hand-built dicts in tests.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

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
