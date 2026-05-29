# trenitalia-api

Python client (sync + async) for the public ViaggiaTreno (Trenitalia) API.

## Install

```bash
uv add git+ssh://git@git.homelab.devncode.it:2222/marco/trenitalia-api.git
```

## Example

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

Service alerts: `client.alerts.list()`.

Errors (network, 404, malformed payload) raise an exception. They all inherit from `TrenitaliaError`. See `trenitalia_api/exceptions.py`.

## Test

```bash
uv run pytest                                    # unit, 80% coverage gate
uv run pytest tests/integration -m integration   # against the live API (optional)
```
