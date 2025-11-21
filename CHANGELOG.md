# Changelog

All notable changes to this project will be documented in this file. This format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and (loosely) [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Nothing yet.

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

- CamelCase address methods (`eth_Address`, `dai_Address`, `dot_Address`, `btc_Address`, `ada_Address`) – use snake_case versions.

### Fixed

- Consistent error handling path returning JSON error structure when suppression enabled.
- Avoid potential invalid gigantic `count` values by adding a soft MAX warning.

### Security

- Reduced risk of leaking token via logs or repr output.

[0.1.0]: https://github.com/jeircul/firipy/releases/tag/v0.1.0
