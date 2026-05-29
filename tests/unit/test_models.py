"""Pydantic model tests — alias mapping, frozen-ness, defaults."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from tests.conftest import status_payload, stop_payload
from trenitalia_api.models import ServiceAlert, TrainSearchResult, TrainStatus, TrainStop


class TestTrainStop:
    def test_reads_italian_aliases(self) -> None:
        stop = TrainStop.model_validate(stop_payload())

        assert stop.station == "ROMA TERMINI"
        assert stop.station_id == "S08409"
        assert stop.kind == "F"
        assert stop.scheduled_time == 1772718120000

    def test_accepts_english_field_names(self) -> None:
        stop = TrainStop(station="ROMA", station_id="S1", kind="A")
        assert stop.station == "ROMA"

    def test_is_frozen(self) -> None:
        stop = TrainStop.model_validate(stop_payload())
        with pytest.raises(ValidationError):
            stop.station = "OTHER"  # type: ignore[misc]

    def test_unknown_kind_rejected(self) -> None:
        with pytest.raises(ValidationError):
            TrainStop(station="X", station_id="X", kind="Z")  # type: ignore[arg-type]

    def test_extra_keys_ignored(self) -> None:
        stop = TrainStop.model_validate({**stop_payload(), "extraField": "ignored"})
        assert not hasattr(stop, "extraField")


class TestTrainStatus:
    def test_full_payload(self) -> None:
        status = TrainStatus.model_validate(status_payload())
        assert status.train_number == 9642
        assert status.origin == "REGGIO CALABRIA"
        assert status.delay == 5
        assert len(status.stops) == 3
        assert status.stops[0].kind == "P"
        assert status.stops[-1].kind == "A"

    def test_optional_fields_default_to_none(self) -> None:
        minimal = status_payload(stazioneUltimoRilevamento=None, compOraUltimoRilevamento=None)
        status = TrainStatus.model_validate(minimal)
        assert status.last_detected_station is None

    def test_required_fields_enforced(self) -> None:
        with pytest.raises(ValidationError):
            TrainStatus.model_validate({})


class TestTrainSearchResult:
    def test_construction(self) -> None:
        r = TrainSearchResult(train_number=9642, train_id="S11781", timestamp=1, origin="O")
        assert r.train_number == 9642


class TestServiceAlert:
    def test_strips_whitespace(self) -> None:
        a = ServiceAlert(
            title="  hello  ",
            body_html="\n<p>x</p>\n",
            published_on=date(2026, 5, 29),
            is_priority=True,
        )
        assert a.title == "hello"
        assert a.body_html == "<p>x</p>"

    def test_non_string_fields_left_alone(self) -> None:
        a = ServiceAlert(title="t", body_html="b", published_on=date(2026, 1, 1), is_priority=False)
        assert a.published_on == date(2026, 1, 1)
