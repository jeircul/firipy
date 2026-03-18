# firipy — Agent Behavioral Rules

## Before making changes

- Run `uv sync` first to ensure deps are up to date.
- Run all 4 CI checks before proposing any code changes:
  1. `uv run ruff format --check .`
  2. `uv run ruff check .`
  3. `uv run ty check`
  4. `uv run pytest`
- Only touch files relevant to the task. No opportunistic refactoring.

## Toolchain rules (non-negotiable)

- `uv` only — never `pip`, `poetry`, or `pipenv`
- `ruff` only — never `black`, `flake8`, `isort`, or `pylint`
- `ty` only — never `mypy` or `pyright`
- `pytest` with `asyncio_mode = "auto"` — never `unittest`
- `httpx.AsyncClient` — never `requests` or `aiohttp`

## Code conventions

- Lowercase generics, `X | None` unions, PEP 695 type aliases — see `copilot-instructions.md`
- Google-style docstrings on public API only
- Comment **why**, not what
- All public API must be re-exported from `src/firipy/__init__.py`

## Release process

1. Bump version in `pyproject.toml` `[project].version`
2. Commit, tag `v{version}`, push tag
3. GitHub Actions `publish.yml` handles PyPI upload via `PYPI_TOKEN`
