# firipy

Async Python client for the Firi cryptocurrency exchange API.

## Stack

- Python 3.13+, `httpx.AsyncClient` (async-only)
- Build: `hatchling`, `src/` layout, `py.typed`
- Package manager: `uv` — no pip/poetry/pipenv
- Linter/formatter: `ruff` — no black/flake8/isort
- Type checker: `ty` — no mypy/pyright
- Tests: `pytest` + `pytest-asyncio` (auto mode) + `respx`

## Layout

```
src/firipy/
  __init__.py     # public API re-exports
  api.py          # FiriAPI async client class
tests/
  test_firipy.py      # unit tests (mocked with respx)
  test_live_firi.py   # live integration tests (needs API_KEY_FIRI)
scripts/              # dev/release helpers
```

## Key Conventions

- Lowercase generics: `list`, `dict`, `tuple` — never `List`, `Dict`
- `X | None` unions — never `Optional[X]`
- No `from __future__ import annotations` on 3.13+
- PEP 695 `type` statement for aliases: `type JSON = dict[str, Any] | list[Any]`
- Google-style docstrings on public API; skip on private helpers unless non-obvious
- Comment **why**, not what
- All async — `async with FiriAPI(...) as client:` context manager pattern

## Commands

```bash
uv sync                                           # install deps
uv run pytest                                     # unit tests
uv run ruff check --fix . && uv run ruff format . # lint + format
uv run ty check                                   # type check
LIVE_FIRI_TESTS=1 uv run pytest tests/test_live_firi.py  # live tests
```

## CI Checks (all must pass before proposing changes)

1. `ruff format --check .`
2. `ruff check .`
3. `ty check`
4. `uv run pytest`

## Release

- Version in `pyproject.toml` `[project].version`
- Publish via GitHub Actions on tag push (`v*`)
- PyPI auth: repository secret `PYPI_TOKEN`
