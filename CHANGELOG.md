# Changelog

All notable changes to this project will be documented in this file. This format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- HMAC request signing: pass `secret_key` and `client_id` to `FiriAPI` to sign
  requests for access keys whose security level requires it beyond plain
  API-key auth. Adds a `firi-user-signature` header, a `firi-user-clientid`
  header, and `timestamp`/`validity` query parameters. `validity_ms` (default
  `2000`) controls the signed timestamp's validity window; `hmac_compact_json`
  (default `True`) controls whether the JSON body is serialized compactly
  before signing, since Firi's own reference examples disagree on spacing.
- Automatic retries for `GET`, `HEAD`, and `DELETE` requests on `429`, `500`,
  `502`, `503`, and `504` responses and on transport errors, with exponential
  backoff and jitter (honoring `Retry-After` when present). Configurable via
  `max_retries` (default `2`), `backoff_base` (default `0.5`), and
  `max_backoff` (default `30.0`). `POST` requests are never auto-retried,
  since placing an order is not idempotent.
- `FiriAuthError` and `FiriRateLimitError`, new subclasses of `FiriHTTPError`
  for 401/403 and 429 responses respectively. `FiriRateLimitError` carries a
  `retry_after` attribute.
- `error_name` attribute on `FiriHTTPError`: Firi's machine-readable error code
  from the response body's `"name"` field (e.g. `ApiKeyNotFound`,
  `SecurityLevelTooLow`), when available.

### Changed

- `post_orders` signature clarified to `(market, ordertype, price, amount)`;
  `ordertype` is mapped to the API's `type` field internally.
- The auth header is now sent as `firi-access-key` (Firi's current documented
  header name), with `miraiex-access-key` sent alongside for backward
  compatibility.
- `rate_limit` is now a true minimum-interval pacing gate rather than an
  unconditional pre-request sleep: concurrent calls are serialized through a
  lock to respect the interval instead of all sleeping in parallel.
- Clarified that `MAX_COUNT` (10,000) is a firipy client-side guardrail, not a
  limit enforced by the Firi API itself.

## [1.1.0] - 2026-04-22

### Fixed

- Injected `httpx.AsyncClient` is no longer mutated (headers) or closed by
  `FiriAPI`. Ownership stays with the caller; only internally-created clients
  are closed on `aclose()` / `async with` exit.
- Removed unused `_api_key` instance attribute that was stored but never read.

### Deprecated

- Per-coin convenience methods (`xrp_withdraw_pending`, `xrp_withdraw_address`,
  `ltc_withdraw_pending`, `ltc_withdraw_address`, `eth_withdraw_pending`,
  `eth_address`, `dai_withdraw_pending`, `dai_address`, `dot_address`,
  `dot_withdraw_pending`, `btc_withdraw_pending`, `btc_address`,
  `ada_withdraw_pending`, `ada_address`) now emit `DeprecationWarning`.
  Use `coin_address(symbol)` / `coin_withdraw_pending(symbol)` instead.

## [1.0.0] - 2026-03-08

### Changed

- **Breaking:** Entire client is now async-only. All API methods are `async def`
  and must be `await`ed. Use `async with FiriAPI(...) as client:` for the
  context manager.
- **Breaking:** Replaced `requests` dependency with `httpx`. The constructor
  parameter `session` has been renamed to `client` (accepts
  `httpx.AsyncClient`). The `close()` method is now `aclose()`.
- **Breaking:** Minimum Python version raised from 3.10 to 3.13.
- Migrated to `src/` package layout with `py.typed` marker for PEP 561
  typed-package support.
- Switched project toolchain to `uv` (replaces pip/venv). Dependencies are
  now locked via `uv.lock`.
- Replaced `mypy` with `ty` (ruff-native type checker) for type checking.
- Docstrings converted from NumPy-style to Google-style.
- All type annotations modernised: `dict[str, Any]` instead of `Dict[str, Any]`,
  PEP 695 `type` statement for type aliases, `X | None` union syntax.
- Rate limiting now uses `asyncio.sleep` instead of `time.sleep` to avoid
  blocking the event loop.
- CI workflows updated to use `uv` and `astral-sh/setup-uv` action.
- Taskfile commands updated to use `uv run`.

### Removed

- `requests` dependency (replaced by `httpx`).
- `mypy`, `types-requests`, `build`, `twine` dev dependencies.
- Sync context manager (`__enter__`/`__exit__`), use async
  (`__aenter__`/`__aexit__`) instead.
- Python 3.10, 3.11, 3.12 support.

### Migration Guide

**Before (v0.2.x):**

```python
from firipy import FiriAPI

with FiriAPI("your-api-key") as client:
    markets = client.markets()
```

**After (v1.0.0):**

```python
import asyncio
from firipy import FiriAPI

async def main():
    async with FiriAPI("your-api-key") as client:
        markets = await client.markets()

asyncio.run(main())
```

## [0.2.0] - 2026-02-07

### Changed

- **Breaking:** Renamed the `FiriAPI` constructor parameter from `token` to
  `api_key` to match Firi's own terminology (resolves #21). Positional usage
  (`FiriAPI("key")`) is unaffected; keyword callers must update from
  `token=` to `api_key=`.
- Updated README, examples, docstrings, and scripts to consistently use
  "API key" instead of "token."


## [0.1.1] - 2025-11-21

### Removed

- Legacy camelCase deposit address helpers (e.g., `eth_Address`) now that snake_case
  variants have been stable for multiple releases.
- Undocumented `history_trades*` endpoints that no longer appear in the public API
  documentation.
- Deprecated delete helpers (`delete_orders_orderid_detailed`,
  `delete_orders_orderid_market_detailed`, `delete_orders_marketormarketsid`) in favor of
  the concise `delete_order_detailed` and `delete_orders_for_market` methods.
- Dropped Python 3.9 support; the client now requires Python 3.10 or newer.


## [0.1.0] - 2025-09-25

### Added

- Structured exception hierarchy: `FiriAPIError`, `FiriHTTPError`.
- `raise_on_error` flag for optional error suppression.
- Context manager support (`with FiriAPI(...) as c:`) and `close()` method.
- Configurable `timeout`, `base_url`, and adjustable `rate_limit` (can be 0).
- Safer default pagination (`DEFAULT_COUNT=500`, warning for very large counts).
- Deprecation wrappers for legacy camelCase address methods (`eth_Address`, etc.).
- Live integration test file (skipped unless `LIVE_FIRI_TESTS=1` and `API_KEY_FIRI`).
- Task automation via `Taskfile.yml` (lint, typecheck, test, coverage, build, live tests).
- README endpoint table, error handling documentation, development setup notes.

### Changed

- Default history/deposit `count` drastically reduced from huge arbitrary number to 500.
- Logging replaces bare `print` statements; token redacted in `__repr__`.
- Dependency pin for `requests>=2.31,<3` and Python version raised to `>=3.9`.

### Deprecated

- CamelCase address methods (`eth_Address`, `dai_Address`, `dot_Address`, `btc_Address`, `ada_Address`) -- use snake_case versions.

### Fixed

- Consistent error handling path returning JSON error structure when suppression enabled.
- Avoid potential invalid gigantic `count` values by adding a soft MAX warning.

### Security

- Reduced risk of leaking token via logs or repr output.

[0.1.0]: https://github.com/jeircul/firipy/releases/tag/v0.1.0
