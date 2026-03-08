---
description: 'Python coding conventions and guidelines'
applyTo: '**/*.py'
---

# Python Coding Conventions

## Toolchain

- **uv** for package management, virtualenvs, and running commands (`uv sync`, `uv run`).
- **ruff** for linting and formatting (replaces flake8, isort, black).
- **ty** for type checking (ruff-native, Rust-based).
- **pytest** + **pytest-asyncio** for testing with `asyncio_mode = "auto"`.
- **httpx** for async HTTP (never `requests` in new code).

## Type Annotations

- Use **lowercase built-in generics**: `list`, `dict`, `tuple`, `set`, `type`.
- Use `X | None` union syntax (never `Optional[X]`).
- Use `X | Y` union syntax (never `Union[X, Y]`).
- Annotate all function signatures (params + return type).
- Use PEP 695 `type` statement for type aliases.
- No `from __future__ import annotations` on Python 3.13+.

## Code Style

- **Google-style docstrings** on all public functions, classes, and modules.
- Comment **why**, not what.
- Prefer `dataclasses` or Pydantic `BaseModel` over plain dicts for structured data.
- Use `pathlib.Path` (never `os.path`).
- Use `logging` module (never bare `print()` in library code).
- Use f-strings for all string formatting.

## Async

- Prefer `async`/`await` with `asyncio` for I/O-bound work.
- Use `httpx.AsyncClient` for HTTP.
- Use `asyncio.TaskGroup` (3.11+) over `asyncio.gather`.
- Context managers: `async with` for clients and sessions.

## Testing

- Test files: `tests/test_<module>.py`.
- Use pytest fixtures, `tmp_path`, `monkeypatch` (avoid `unittest.TestCase`).
- Use `pytest-asyncio` with `asyncio_mode = "auto"`.
- Mock external services with `respx` (httpx).

## Error Handling

- Catch specific exceptions (never bare `except:`).
- Use custom exception classes for domain errors.
- Let unexpected errors propagate.
