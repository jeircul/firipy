# firipy

Async Python client for the Firi cryptocurrency exchange API.
Python 3.13+, httpx, hatchling, src/ layout, py.typed.

## Toolchain (non-negotiable)

| Purpose | Tool | Never use |
|---------|------|-----------|
| Deps/venv | `uv` | pip, poetry, pipenv |
| Lint + format | `ruff` | black, flake8, isort |
| Type check | `ty` | mypy, pyright |
| Tests | `pytest` + `pytest-asyncio` (auto) + `respx` | unittest |
| HTTP | `httpx.AsyncClient` | requests, aiohttp |

## Layout

`src/firipy/__init__.py` — public re-exports
`src/firipy/api.py` — FiriAPI async client (~600 lines)
`tests/test_firipy.py` — unit tests (respx mocks)
`tests/test_live_firi.py` — live tests (needs `API_KEY_FIRI`, `LIVE_FIRI_TESTS=1`)
`scripts/` — dev helpers

## Validate before proposing changes

`uv sync && uv run ruff format --check . && uv run ruff check . && uv run ty check && uv run pytest`

## Style

- Lowercase generics, `X | None`, PEP 695 `type` aliases
- Google docstrings on public API only
- Comment **why**, not what
- `async with FiriAPI(...) as client:` context manager pattern
- `type JSON = dict[str, Any] | list[Any]` for API returns

## Release

Bump `[project].version` in `pyproject.toml` → commit → tag `v{version}` → push tag.
GitHub Actions `publish.yml` uploads to PyPI via `PYPI_TOKEN`.
