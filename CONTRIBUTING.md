# Contributing

Thanks for your interest. The library is intentionally small — bug fixes,
new endpoint coverage, and docs improvements are all welcome.

## Setup

```bash
git clone https://github.com/marcocot/trenitalia-api.git
cd trenitalia-api
uv sync
uv run pre-commit install
```

## Workflow

1. Open an issue first for non-trivial changes (new resource, breaking API).
2. Branch from `main`, make your changes, keep commits atomic.
3. Run the checks locally:

   ```bash
   uv run ruff check .
   uv run black --check .
   uv run mypy src tests
   uv run pytest
   ```

4. Open a PR. CI runs on Python 3.11 / 3.12 / 3.13. Coverage gate is 80%.
5. Squash merge once CI is green.

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/) — one-sentence
subject, no body unless there's a breaking change to explain.

Common prefixes: `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `ci:`, `refactor:`.

## Adding a new endpoint

1. URL builder in `src/trenitalia_api/_endpoints.py`.
2. Pydantic model in `src/trenitalia_api/models.py` (alias Italian keys to
   snake_case English).
3. Parser in `src/trenitalia_api/_parsing.py`.
4. Resource method(s) in `src/trenitalia_api/resources/<area>.py` — both sync
   and async.
5. Tests: unit (mocks + parsers) plus a live integration test marked
   `@pytest.mark.integration`.
6. Update the README field reference table.
