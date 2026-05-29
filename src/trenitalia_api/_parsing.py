"""Pure response parsers.

These functions take a raw response body (str/dict/bytes) and return a
typed model, raising :exc:`InvalidResponseError` if the shape doesn't
match. They never touch the network, which makes them trivial to test.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import ValidationError
from selectolax.parser import HTMLParser, Node

from .exceptions import InvalidResponseError
from .models import (
    ServiceAlert,
    StationDetail,
    StationMatch,
    StationTrain,
    TrainSearchResult,
    TrainStatus,
)


# ---------------------------------------------------------------------------
# /cercaNumeroTrenoTrenoAutocomplete/{n}
# ---------------------------------------------------------------------------
def parse_search_response(text: str) -> TrainSearchResult:
    """Parse the pipe-separated autocomplete reply.

    Format::

        "<num> - <origin> - <date>|<num>-<train_id>-<timestamp>"
    """
    text = text.strip()
    if not text:
        raise InvalidResponseError("empty search response body")

    if "|" not in text:
        raise InvalidResponseError(f"search response missing '|' separator: {text!r}")

    left, right = text.split("|", 1)

    right_parts = right.strip().split("-")
    if len(right_parts) < 3:
        raise InvalidResponseError(f"search response right side malformed: {right!r}")

    raw_number, train_id, raw_timestamp = right_parts[0], right_parts[1], right_parts[2]

    left_parts = [p.strip() for p in left.split(" - ")]
    if len(left_parts) < 3:
        raise InvalidResponseError(f"search response left side malformed: {left!r}")
    # Rejoin middle parts so origin can contain ' - '.
    origin = " - ".join(left_parts[1:-1])

    try:
        return TrainSearchResult(
            train_number=int(raw_number),
            train_id=train_id,
            timestamp=int(raw_timestamp),
            origin=origin,
        )
    except (ValueError, ValidationError) as exc:
        raise InvalidResponseError(f"search response failed validation: {exc}") from exc


# ---------------------------------------------------------------------------
# /andamentoTreno/{id}/{n}/{ts}
# ---------------------------------------------------------------------------
def parse_status_response(payload: Any) -> TrainStatus:
    if not isinstance(payload, dict):
        raise InvalidResponseError(
            f"status payload must be a JSON object, got {type(payload).__name__}"
        )
    try:
        return TrainStatus.model_validate(payload)
    except ValidationError as exc:
        raise InvalidResponseError(f"status payload failed validation: {exc}") from exc


# ---------------------------------------------------------------------------
# /infomobilitaRSS/{flag}
# ---------------------------------------------------------------------------
def parse_infomobility_response(html: str) -> list[ServiceAlert]:
    """Parse the accordion-style HTML feed into a list of alerts."""
    if not html.strip():
        return []

    tree = HTMLParser(html)
    alerts: list[ServiceAlert] = []
    for node in tree.css("li.editModeCollapsibleElement"):
        alert = _parse_alert(node)
        if alert is not None:
            alerts.append(alert)
    return alerts


def _parse_alert(node: Node) -> ServiceAlert | None:
    title_node = node.css_first("a.headingNewsAccordion")
    body_node = node.css_first(".info-text")
    date_node = node.css_first("h4")

    if title_node is None or body_node is None or date_node is None:
        return None

    title = title_node.text(strip=True)
    if not title:
        return None

    class_attr = title_node.attributes.get("class") or ""
    is_priority = "inEvidenza" in class_attr.split()

    raw_date = date_node.text(strip=True)
    try:
        published_on = datetime.strptime(raw_date, "%d.%m.%Y").date()
    except ValueError:
        return None

    return ServiceAlert(
        title=title,
        body_html=_inner_html(body_node),
        published_on=published_on,
        is_priority=is_priority,
    )


def _inner_html(node: Node) -> str:
    """Return the inner HTML of ``node`` (children only, no wrapper tag)."""
    outer = node.html or ""
    open_end = outer.find(">")
    close_start = outer.rfind("<")
    if open_end == -1 or close_start <= open_end:
        return outer
    return outer[open_end + 1 : close_start]


# ---------------------------------------------------------------------------
# /autocompletaStazione/{q}
# ---------------------------------------------------------------------------
def parse_station_autocomplete(text: str) -> list[StationMatch]:
    """Parse the ``NAME|ID`` newline-separated autocomplete reply."""
    matches: list[StationMatch] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or "|" not in line:
            continue
        name, station_id = line.rsplit("|", 1)
        name, station_id = name.strip(), station_id.strip()
        if not name or not station_id:
            continue
        matches.append(StationMatch(name=name, station_id=station_id))
    return matches


# ---------------------------------------------------------------------------
# /regione/{id}
# ---------------------------------------------------------------------------
def parse_station_region(payload: Any) -> int:
    if isinstance(payload, bool) or not isinstance(payload, int):
        raise InvalidResponseError(f"region payload must be an int, got {type(payload).__name__}")
    return payload


# ---------------------------------------------------------------------------
# /dettaglioStazione/{id}/{region}
# ---------------------------------------------------------------------------
def parse_station_detail(payload: Any) -> StationDetail:
    if not isinstance(payload, dict):
        raise InvalidResponseError(
            f"station detail payload must be a JSON object, got {type(payload).__name__}"
        )
    try:
        return StationDetail.model_validate(payload)
    except ValidationError as exc:
        raise InvalidResponseError(f"station detail failed validation: {exc}") from exc


# ---------------------------------------------------------------------------
# /partenze/{id}/{when} and /arrivi/{id}/{when}
# ---------------------------------------------------------------------------
def parse_station_trains(payload: Any) -> list[StationTrain]:
    if not isinstance(payload, list):
        raise InvalidResponseError(
            f"timetable payload must be a JSON array, got {type(payload).__name__}"
        )
    try:
        return [StationTrain.model_validate(item) for item in payload]
    except ValidationError as exc:
        raise InvalidResponseError(f"timetable entry failed validation: {exc}") from exc
