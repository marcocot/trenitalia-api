"""Parser tests — pure functions, no network."""

from __future__ import annotations

from datetime import date

import pytest

from tests.conftest import INFOMOBILITY_HTML, SEARCH_BODY, status_payload
from trenitalia_api._parsing import (
    parse_infomobility_response,
    parse_search_response,
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
