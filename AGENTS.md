# firipy

Async Python client for the Firi cryptocurrency exchange API.

## Stack

- **Language**: Python 3.13+
- **HTTP**: `httpx.AsyncClient` (async-only)
- **Build**: `hatchling` with `src/` layout
- **Package manager**: `uv`
- **Linter/formatter**: `ruff`
- **Type checker**: `ty`
- **Tests**: `pytest` + `pytest-asyncio` (auto mode) + `respx`
- **CI**: GitHub Actions

## Layout

```
src/firipy/           # Package source (py.typed)
  __init__.py         # Public API re-exports
  api.py              # FiriAPI async client class
tests/
  test_firipy.py      # Unit tests (mocked with respx)
  test_live_firi.py   # Live API integration tests
scripts/              # Dev/release helper scripts
```

## Conventions

- `uv` for all dependency and venv management. No pip/poetry/pipenv.
- `pyproject.toml` is single source of truth. No setup.py/cfg or requirements.txt.
- Google-style docstrings on public API. No docstrings on private helpers unless non-obvious.
- Lowercase generics (`list`, `dict`), `X | None` unions, no `Optional`/`Union`.
- All async — use `async with FiriAPI(...) as client:` context manager pattern.
- `type JSON = dict[str, Any] | list[Any]` alias for API return types.
- Comment **why**, not what.

## Commands

```bash
uv sync                                          # Install deps
uv run pytest                                    # Unit tests
uv run ruff check --fix . && uv run ruff format . # Lint + format
uv run ty check                                  # Type check
LIVE_FIRI_TESTS=1 uv run pytest tests/test_live_firi.py  # Live tests (needs API_KEY_FIRI)
```

## CI Checks (must all pass)

1. `ruff format --check .`
2. `ruff check .`
3. `ty check`
4. `pytest` (unit tests only)

## Release

- Version in `pyproject.toml` `[project].version`
- Publish via GitHub Actions on tag push (`v*`)
- PyPI auth: token-based (repository secret `PYPI_TOKEN`)
