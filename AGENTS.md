# firipy

Async Python client for the Firi cryptocurrency exchange API.
Python 3.13+, httpx, hatchling, `src/` layout, `py.typed`.

## Toolchain (non-negotiable)

| Purpose | Tool | Never use |
|---------|------|-----------|
| Deps/venv | `uv` | pip, poetry, pipenv |
| Lint + format | `ruff` | black, flake8, isort |
| Type check | `ty` | mypy, pyright |
| Tests | `pytest` + `pytest-asyncio` (auto mode) + `respx` | unittest |
| HTTP | `httpx.AsyncClient` | requests, aiohttp |
| Task runner | `task` (Taskfile.yml) | make |

## Layout

| Path | What |
|------|------|
| `src/firipy/__init__.py` | public re-exports |
| `src/firipy/api.py` | `FiriAPI` + error hierarchy (~835 lines) |
| `src/firipy/_hmac.py` | private `sign_request()` — HMAC-SHA256 signing |
| `tests/test_firipy.py` | unit tests (respx mocks) |
| `tests/test_hmac.py` | signing unit tests |
| `tests/test_live_firi.py` | live tests — needs `API_KEY_FIRI` + `LIVE_FIRI_TESTS=1` |
| `scripts/bump_version.py` | version + CHANGELOG roll |
| `scripts/check_balance.py` | live smoke helper |

Public surface: `FiriAPI`, `FiriAPIError`, `FiriHTTPError`, `FiriAuthError`, `FiriRateLimitError`. Anything `_`-prefixed is private — do not re-export.

## Validate before proposing changes

**All four, every time. `task qa` does NOT include the format check — CI does, and it fails PRs on its own.**

```
uv sync && uv run ruff format --check . && uv run ruff check . && uv run ty check && uv run pytest
```

## Secrets — hard rule

This client carries live credentials in `client.headers`. **Never print, log, repr, or dict-dump `client.headers`, `os.environ`, or a `FiriAPI` instance's auth attrs.** Check membership or mask instead:

```python
assert ACCESS_KEY_HEADER in client.headers        # yes
print(dict(client.headers))                        # NO — leaks the key
print(key[:4] + "…")                               # masked, if you must
```

Secret-bearing names: `api_key` → `firi-access-key` + legacy `miraiex-access-key`; `secret_key`/`client_id` → `firi-user-signature` + `firi-user-clientid`. Same rule applies to test fixtures, error messages, and debug one-liners.

## Client behaviour (don't regress)

- `rate_limit` is a real min-interval gate (`monotonic` + `asyncio.Lock`), not a blind sleep. `0` disables it.
- Retries/backoff apply to **idempotent methods only** (`GET`, `HEAD`, `DELETE`) on `{429, 500, 502, 503, 504}`; jittered exponential backoff, honours `Retry-After`. Never retry `POST`.
- `secret_key` and `client_id` are all-or-nothing — mismatched pair raises `ValueError`.
- Injected `client=` must already carry an access-key header; `FiriAPI` fails fast if not, and only closes clients it created.

## Style

- Lowercase generics, `X | None`, PEP 695 `type` aliases
- `type JSON = dict[str, Any] | list[Any]` for API returns
- Google docstrings on public API only
- Comment **why**, not what
- `async with FiriAPI(...) as client:` is the documented pattern

## Release

1. `task version PART=patch|minor|major` (or `NEW=x.y.z`; `DRY_RUN=1` to preview) — bumps `pyproject.toml` and rolls `CHANGELOG.md` `[Unreleased]` into a dated entry.
2. `task release-check` → commit → tag `v{version}` → push.
3. **Publish a GitHub Release** — `publish.yml` triggers on `release: published`, not on tag push. It uploads to PyPI via `secrets.PYPI_API_TOKEN`.
