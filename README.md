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

## Test

```bash
uv run pytest                                    # unit, 80% coverage gate
uv run pytest tests/integration -m integration   # against the live API (optional)
```
