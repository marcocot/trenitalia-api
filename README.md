# trenitalia-api

[![PyPI version](https://img.shields.io/pypi/v/trenitalia-api.svg)](https://pypi.org/project/trenitalia-api/)
[![Python versions](https://img.shields.io/pypi/pyversions/trenitalia-api.svg)](https://pypi.org/project/trenitalia-api/)
[![CI](https://github.com/marcocot/trenitalia-api/actions/workflows/ci.yml/badge.svg)](https://github.com/marcocot/trenitalia-api/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/marcocot/trenitalia-api/branch/main/graph/badge.svg)](https://codecov.io/gh/marcocot/trenitalia-api)
[![License: MIT](https://img.shields.io/pypi/l/trenitalia-api.svg)](https://github.com/marcocot/trenitalia-api/blob/main/LICENSE)

Python client (sync + async) for the public ViaggiaTreno (Trenitalia) API.

## Install

```bash
pip install trenitalia-api
```

## Quick start

```python
from trenitalia_api import Client

with Client() as c:
    r = c.trains.search(9642)
    status = c.trains.status(r.train_id, r.train_number, r.timestamp)
    print(f"{status.origin} → {status.destination} ({status.delay} min)")
```

Same interface, async:

```python
import asyncio
from trenitalia_api import AsyncClient

async def main():
    async with AsyncClient() as c:
        r = await c.trains.search(9642)
        status = await c.trains.status(r.train_id, r.train_number, r.timestamp)
        print(status)

asyncio.run(main())
```

Errors (network, 404, malformed payload) raise an exception. They all inherit from `TrenitaliaError`. See `trenitalia_api/exceptions.py`.

## What you get back

### `trains.search(train_number)` → `TrainSearchResult`

```python
>>> c.trains.search(9642)
TrainSearchResult(
    train_number=9642,
    train_id='S11781',
    timestamp=1780005600000,
    origin='REGGIO DI CALABRIA CENTRALE',
)
```

### `trains.status(train_id, train_number, timestamp)` → `TrainStatus`

```python
>>> c.trains.status('S11781', 9642, 1780005600000)
TrainStatus(
    train_number=9642,
    train_label='IC 9642',
    train_type='Intercity',
    origin='REGGIO CALABRIA',
    destination='ROMA TERMINI',
    running=True,
    arrived=False,
    not_departed=False,
    delay=5,
    delay_text=['5 minuti', '5 minutes', '5 Min.', ...],
    scheduled_departure='07:00',
    scheduled_arrival='13:30',
    last_detected_station='NAPOLI CENTRALE',
    last_detected_time='10:15',
    stops=[
        TrainStop(station='REGGIO CALABRIA', station_id='S00001', kind='P', ...),
        TrainStop(station='NAPOLI CENTRALE', station_id='S00002', kind='F', ...),
        TrainStop(station='ROMA TERMINI', station_id='S00003', kind='A', ...),
    ],
)
```

### `alerts.list(only_regional=False)` → `list[ServiceAlert]`

```python
>>> c.alerts.list()
[
    ServiceAlert(
        title='Linea Ancona - Bologna: ripresa graduale',
        body_html='<p>La circolazione è in graduale ripresa.</p>...',
        published_on=date(2026, 5, 29),
        is_priority=True,
    ),
    ServiceAlert(
        title='INFOTRENI FRECCE',
        body_html='<p>I treni indicati viaggiano con ritardo > 60 minuti.</p>',
        published_on=date(2026, 5, 29),
        is_priority=False,
    ),
]
```

### `stations.autocomplete(query)` → `list[StationMatch]`

```python
>>> c.stations.autocomplete("moncalieri")
[
    StationMatch(name='MONCALIERI', station_id='S00453'),
    StationMatch(name='MONCALIERI SANGONE', station_id='S00510'),
]
```

### `stations.detail(station_id, region=None)` → `StationDetail`

If `region` is omitted, one extra call resolves it automatically.

```python
>>> c.stations.detail("S00453")
StationDetail(
    station_id='S00453',
    region_id=3,
    latitude=44.998187,
    longitude=7.678027,
    name='MONCALIERI',
    short_name='MONCALIERI',
    label='Moncalieri',
)
```

### `stations.departures(station_id, when=None)` / `arrivals(...)` → `list[StationTrain]`

`when` defaults to "now" in Europe/Rome.

```python
>>> c.stations.departures("S00453")
[
    StationTrain(
        train_number=26612,
        train_label='REG 26612',
        category='REG',
        train_type='regionale',
        delay=2,
        running=True,
        arrived=True,
        not_departed=False,
        in_station=True,
        origin=None,
        destination='TORINO AEROPORTO DI CASELLE',
        scheduled_departure='10:58',
        scheduled_arrival=None,
        scheduled_departure_platform='5',
        actual_departure_platform='5',
        ...
    ),
    ...
]
```

`arrivals()` returns the same `StationTrain` shape with `origin` / `scheduled_arrival` / `*_arrival_platform` populated instead.

## Field reference

### `TrainSearchResult`

| Field          | Type  | Description                                                |
| -------------- | ----- | ---------------------------------------------------------- |
| `train_number` | `int` | Public train number (the one printed on the timetable).    |
| `train_id`     | `str` | Internal ViaggiaTreno identifier, e.g. `S11781`.           |
| `timestamp`    | `int` | Unix epoch (ms) of the operating day's midnight in Italy.  |
| `origin`       | `str` | Full station name of the train's origin.                   |

### `TrainStatus`

| Field                   | Type              | Description                                                                  |
| ----------------------- | ----------------- | ---------------------------------------------------------------------------- |
| `train_number`          | `int`             | Public train number.                                                         |
| `train_label`           | `str \| None`     | Human-readable label, e.g. `IC 9642`.                                        |
| `train_type`            | `str \| None`     | Train category, e.g. `Intercity`, `Frecciarossa`.                            |
| `origin`                | `str`             | Origin station name.                                                         |
| `destination`           | `str`             | Destination station name.                                                    |
| `running`               | `bool`            | `True` if the train is currently moving (between origin and destination).    |
| `arrived`               | `bool`            | `True` once the train has reached its final stop.                            |
| `not_departed`          | `bool`            | `True` if the train hasn't left the origin yet.                              |
| `delay`                 | `int`             | Current delay in minutes (negative means ahead of schedule).                 |
| `delay_text`            | `list[str]\|None` | Pre-formatted delay message in 9 languages (it/en/de/fr/es/ro/ja/zh/ru).     |
| `scheduled_departure`   | `str \| None`     | Scheduled origin departure as `HH:MM`.                                       |
| `scheduled_arrival`     | `str \| None`     | Scheduled final arrival as `HH:MM`.                                          |
| `last_detected_station` | `str \| None`     | Name of the latest station that recorded the train's passage.                |
| `last_detected_time`    | `str \| None`     | Time of that detection as `HH:MM`.                                           |
| `stops`                 | `list[TrainStop]` | Full stop-by-stop itinerary.                                                 |

### `TrainStop`

| Field                          | Type           | Description                                                              |
| ------------------------------ | -------------- | ------------------------------------------------------------------------ |
| `station`                      | `str`          | Station name.                                                            |
| `station_id`                   | `str`          | Station code, e.g. `S08409`.                                             |
| `kind`                         | `"P"\|"F"\|"A"`| `P` = origin (Partenza), `F` = intermediate (Fermata), `A` = destination (Arrivo). |
| `progressive`                  | `int`          | Position in the itinerary, starting at 0.                                |
| `scheduled_time`               | `int \| None`  | Scheduled time at this stop as Unix epoch (ms).                          |
| `actual_time`                  | `int \| None`  | Actual time at this stop as Unix epoch (ms), once recorded.              |
| `actual_kind`                  | `int \| None`  | Numeric flag set when the train actually transits this stop.             |
| `arrival_delay`                | `int \| None`  | Delay on arrival, in minutes.                                            |
| `departure_delay`              | `int \| None`  | Delay on departure, in minutes.                                          |
| `delay`                        | `int \| None`  | Generic delay value (when arrival/departure aren't split).               |
| `scheduled_arrival_platform`   | `str \| None`  | Scheduled platform for arrival.                                          |
| `actual_arrival_platform`      | `str \| None`  | Actual platform on arrival.                                              |
| `scheduled_departure_platform` | `str \| None`  | Scheduled platform for departure.                                        |
| `actual_departure_platform`    | `str \| None`  | Actual platform on departure.                                            |

### `ServiceAlert`

| Field          | Type   | Description                                                              |
| -------------- | ------ | ------------------------------------------------------------------------ |
| `title`        | `str`  | Headline of the alert.                                                   |
| `body_html`    | `str`  | Body of the alert as raw HTML (use a sanitizer if rendering as trusted). |
| `published_on` | `date` | Day the alert was issued.                                                |
| `is_priority` | `bool`  | `True` for high-impact / ongoing disruptions (the "inEvidenza" flag).    |

### `StationMatch`

| Field        | Type  | Description                                                |
| ------------ | ----- | ---------------------------------------------------------- |
| `name`       | `str` | Full uppercase station name as the upstream returns it.    |
| `station_id` | `str` | Station code, e.g. `S00453` — feed it into `detail()` etc. |

### `StationDetail`

| Field        | Type    | Description                                          |
| ------------ | ------- | ---------------------------------------------------- |
| `station_id` | `str`   | Station code.                                        |
| `region_id`  | `int`   | Numeric ID of the Italian region the station is in.  |
| `latitude`   | `float` | WGS84 latitude.                                      |
| `longitude`  | `float` | WGS84 longitude.                                     |
| `name`       | `str`   | Long station name (uppercase).                       |
| `short_name` | `str`   | Short station name (uppercase).                      |
| `label`      | `str`   | Display-friendly station name (mixed case).          |

### `StationTrain`

Returned by both `departures()` and `arrivals()`. Side-specific fields are
populated according to which endpoint produced the row.

| Field                          | Type            | Description                                                              |
| ------------------------------ | --------------- | ------------------------------------------------------------------------ |
| `train_number`                 | `int`           | Public train number.                                                     |
| `train_label`                  | `str`           | Human-readable label, e.g. `REG 26612`.                                  |
| `category`                     | `str`           | Short category code, e.g. `REG`, `IC`, `FR`.                             |
| `train_type`                   | `str \| None`   | Long category, e.g. `regionale`, `intercity`.                            |
| `delay`                        | `int`           | Current delay in minutes.                                                |
| `running`                      | `bool`          | Train is moving right now.                                               |
| `arrived`                      | `bool`          | Train has reached its destination.                                       |
| `not_departed`                 | `bool`          | Train hasn't left yet.                                                   |
| `in_station`                   | `bool`          | Train is currently sitting at *this* station.                            |
| `origin`                       | `str \| None`   | Set on arrivals timetable: the station the train came from.              |
| `destination`                  | `str \| None`   | Set on departures timetable: where the train is going.                   |
| `scheduled_departure`          | `str \| None`   | `HH:MM` — set on departures.                                             |
| `scheduled_arrival`            | `str \| None`   | `HH:MM` — set on arrivals.                                               |
| `scheduled_departure_platform` | `str \| None`   | Scheduled platform — set on departures.                                  |
| `actual_departure_platform`    | `str \| None`   | Actual platform — set on departures.                                     |
| `scheduled_arrival_platform`   | `str \| None`   | Scheduled platform — set on arrivals.                                    |
| `actual_arrival_platform`      | `str \| None`   | Actual platform — set on arrivals.                                       |
| `last_detection`               | `int \| None`   | Unix epoch (ms) of the latest position fix for this train.               |

## Test

```bash
uv run pytest                                    # unit, 80% coverage gate
uv run pytest tests/integration -m integration   # against the live API (optional)
```
