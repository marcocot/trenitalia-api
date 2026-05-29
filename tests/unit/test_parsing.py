"""Parser tests — pure functions, no network."""

from __future__ import annotations

from datetime import date

import pytest

from tests.conftest import (
    INFOMOBILITY_HTML,
    SEARCH_BODY,
    STATION_AUTOCOMPLETE_BODY,
    arrival_payload,
    departure_payload,
    station_detail_payload,
    status_payload,
)
from trenitalia_api._parsing import (
    parse_infomobility_response,
    parse_search_response,
    parse_station_autocomplete,
    parse_station_detail,
    parse_station_region,
    parse_station_trains,
    parse_status_response,
)
from trenitalia_api.exceptions import InvalidResponseError


class TestParseSearchResponse:
    def test_valid_response(self) -> None:
        r = parse_search_response(SEARCH_BODY)
        assert r.train_number == 9642
        assert r.train_id == "S11781"
        assert r.timestamp == 1772665200000
        assert r.origin == "REGGIO DI CALABRIA CENTRALE"

    def test_origin_with_hyphen_is_preserved(self) -> None:
        # Some station names contain hyphens — ensure we don't lose them.
        body = "1000 - SAN GIORGIO - DI NOGARO - 05/03/26|1000-S00001-1234567890000"
        r = parse_search_response(body)
        assert r.origin == "SAN GIORGIO - DI NOGARO"

    def test_empty_body_raises(self) -> None:
        with pytest.raises(InvalidResponseError, match="empty"):
            parse_search_response("")

    def test_missing_separator_raises(self) -> None:
        with pytest.raises(InvalidResponseError, match="separator"):
            parse_search_response("no pipe here")

    def test_malformed_right_side_raises(self) -> None:
        with pytest.raises(InvalidResponseError, match="right side"):
            parse_search_response("9642 - X - 05/03/26|onlyone")

    def test_malformed_left_side_raises(self) -> None:
        with pytest.raises(InvalidResponseError, match="left side"):
            parse_search_response("nope|9642-S11781-1772665200000")

    def test_non_numeric_fields_raise(self) -> None:
        with pytest.raises(InvalidResponseError, match="validation"):
            parse_search_response("abc - X - 05/03/26|abc-S1-notanumber")


class TestParseStatusResponse:
    def test_valid_payload(self) -> None:
        status = parse_status_response(status_payload())
        assert status.train_number == 9642

    def test_non_dict_raises(self) -> None:
        with pytest.raises(InvalidResponseError, match="must be a JSON object"):
            parse_status_response([1, 2, 3])

    def test_validation_failure_raises(self) -> None:
        with pytest.raises(InvalidResponseError, match="validation"):
            parse_status_response({"some": "garbage"})


class TestParseInfomobilityResponse:
    def test_parses_two_items(self) -> None:
        alerts = parse_infomobility_response(INFOMOBILITY_HTML)
        assert len(alerts) == 2

    def test_priority_flag_set_from_class(self) -> None:
        alerts = parse_infomobility_response(INFOMOBILITY_HTML)
        assert alerts[0].is_priority is True
        assert alerts[1].is_priority is False

    def test_date_parsed(self) -> None:
        alerts = parse_infomobility_response(INFOMOBILITY_HTML)
        assert alerts[0].published_on == date(2026, 5, 29)

    def test_body_keeps_inner_html(self) -> None:
        alerts = parse_infomobility_response(INFOMOBILITY_HTML)
        assert "<p>" in alerts[0].body_html
        assert "ripresa" in alerts[0].body_html

    def test_empty_html_returns_empty_list(self) -> None:
        assert parse_infomobility_response("") == []
        assert parse_infomobility_response("   \n  ") == []

    def test_unparseable_dates_are_skipped(self) -> None:
        html = """
        <ul>
          <li class="editModeCollapsibleElement">
            <a class="headingNewsAccordion">Title</a>
            <div class="info-text"><p>body</p></div>
            <h4>not-a-date</h4>
          </li>
        </ul>
        """
        assert parse_infomobility_response(html) == []

    def test_missing_required_nodes_are_skipped(self) -> None:
        # Missing <h4> entirely
        html = '<ul><li class="editModeCollapsibleElement"><a class="headingNewsAccordion">x</a></li></ul>'
        assert parse_infomobility_response(html) == []

    def test_empty_title_is_skipped(self) -> None:
        html = """
        <ul>
          <li class="editModeCollapsibleElement">
            <a class="headingNewsAccordion"></a>
            <div class="info-text"><p>x</p></div>
            <h4>29.05.2026</h4>
          </li>
        </ul>
        """
        assert parse_infomobility_response(html) == []


class TestParseStationAutocomplete:
    def test_two_matches(self) -> None:
        matches = parse_station_autocomplete(STATION_AUTOCOMPLETE_BODY)
        assert len(matches) == 2
        assert matches[0].name == "MONCALIERI"
        assert matches[0].station_id == "S00453"
        assert matches[1].name == "MONCALIERI SANGONE"
        assert matches[1].station_id == "S00510"

    def test_skips_empty_and_separator_less_lines(self) -> None:
        body = "MONCALIERI|S00453\n\nno-pipe-here\n|\nFOO|S99999\n"
        matches = parse_station_autocomplete(body)
        assert [m.station_id for m in matches] == ["S00453", "S99999"]

    def test_empty_body_yields_empty_list(self) -> None:
        assert parse_station_autocomplete("") == []

    def test_name_with_pipe_is_split_on_the_last_pipe(self) -> None:
        # Unlikely but defensive — rsplit lets the ID stay intact.
        matches = parse_station_autocomplete("FOO|BAR|S00001\n")
        assert matches[0].name == "FOO|BAR"
        assert matches[0].station_id == "S00001"


class TestParseStationRegion:
    def test_int_passthrough(self) -> None:
        assert parse_station_region(3) == 3

    def test_zero_is_valid(self) -> None:
        assert parse_station_region(0) == 0

    def test_string_rejected(self) -> None:
        with pytest.raises(InvalidResponseError):
            parse_station_region("3")

    def test_bool_rejected(self) -> None:
        # ``bool`` is a subclass of ``int`` — guard against silent acceptance.
        with pytest.raises(InvalidResponseError):
            parse_station_region(True)


class TestParseStationDetail:
    def test_valid_payload(self) -> None:
        detail = parse_station_detail(station_detail_payload())
        assert detail.station_id == "S00453"
        assert detail.region_id == 3
        assert detail.latitude == 44.998187
        assert detail.longitude == 7.678027
        assert detail.name == "MONCALIERI"
        assert detail.label == "Moncalieri"

    def test_non_dict_rejected(self) -> None:
        with pytest.raises(InvalidResponseError, match="JSON object"):
            parse_station_detail([1, 2])

    def test_missing_localita_falls_back_to_empty_strings(self) -> None:
        payload = station_detail_payload()
        del payload["localita"]
        # Without localita, name/short_name/label come up missing entirely → validation fails.
        with pytest.raises(InvalidResponseError, match="validation"):
            parse_station_detail(payload)


class TestParseStationTrains:
    def test_departure(self) -> None:
        trains = parse_station_trains([departure_payload()])
        assert len(trains) == 1
        t = trains[0]
        assert t.train_number == 26612
        assert t.destination == "TORINO AEROPORTO DI CASELLE"
        assert t.scheduled_departure == "10:58"
        assert t.scheduled_arrival is None
        assert t.actual_departure_platform == "5"
        assert t.delay == 2

    def test_arrival(self) -> None:
        trains = parse_station_trains([arrival_payload()])
        t = trains[0]
        assert t.origin == "ASTI"
        assert t.scheduled_arrival == "10:57"
        assert t.scheduled_departure is None
        assert t.actual_arrival_platform == "5"

    def test_empty_list(self) -> None:
        assert parse_station_trains([]) == []

    def test_non_list_rejected(self) -> None:
        with pytest.raises(InvalidResponseError, match="JSON array"):
            parse_station_trains({"not": "a list"})

    def test_extra_fields_ignored(self) -> None:
        payload = departure_payload(extraGarbage="x", compRitardo=["delay 2 min."])
        trains = parse_station_trains([payload])
        assert trains[0].train_number == 26612

    def test_validation_failure_raises(self) -> None:
        with pytest.raises(InvalidResponseError, match="validation"):
            parse_station_trains([{"garbage": True}])
