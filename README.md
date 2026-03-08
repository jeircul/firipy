# Firipy

[![Upload Python Package](https://github.com/jeircul/firipy/actions/workflows/publish.yml/badge.svg)](https://github.com/jeircul/firipy/actions/workflows/publish.yml)
[![Run Tests](https://github.com/jeircul/firipy/actions/workflows/run_tests.yml/badge.svg)](https://github.com/jeircul/firipy/actions/workflows/run_tests.yml)
![PyPI - Version](https://img.shields.io/pypi/v/firipy)
![GitHub](https://img.shields.io/github/license/jeircul/firipy)

Async Python client for the [Firi](https://www.firi.com/) cryptocurrency exchange API.

## Installation

```bash
pip install firipy
```

Requires **Python 3.13+**.

## Usage

All methods are async and must be awaited:

```python
import asyncio
from firipy import FiriAPI

async def main():
    async with FiriAPI("your-api-key") as client:
        time = await client.time()
        print(time)

        markets = await client.markets()
        print(markets)

        balances = await client.balances()
        print(balances)

asyncio.run(main())
```

## Rate Limiting

Built-in client-side pacing (seconds to sleep before each request). Default is 1 second:

```python
client = FiriAPI("your-api-key", rate_limit=2)    # 2 second delay
client = FiriAPI("your-api-key", rate_limit=0)    # no delay
```

Uses `asyncio.sleep` so it won't block the event loop.

## Error Handling

Structured exceptions are raised by default:

| Exception | Description |
|---|---|
| `FiriAPIError` | Base class for client errors |
| `FiriHTTPError` | Non-success HTTP responses (status >= 400) |

Suppress exceptions with `raise_on_error=False`:

```python
async with FiriAPI("your-api-key", raise_on_error=False) as client:
    data = await client.markets()
    if isinstance(data, dict) and "error" in data:
        print("Failed:", data)
```

Error dict shape: `{"error": str, "status": int | None}`.

## Endpoint Overview

| Method | Endpoint | Purpose | Key Optional Params |
|---|---|---|---|
| `time()` | `/time` | Server time | -- |
| `markets()` | `/v2/markets` | List markets | -- |
| `markets_market(m)` | `/v2/markets/{m}` | Market details | -- |
| `markets_market_depth(m, bids=, asks=)` | `/v2/markets/{m}/depth` | Order book | `bids`, `asks` |
| `markets_market_history(m, count=)` | `/v2/markets/{m}/history` | Market trade history | `count` |
| `markets_market_ticker(m)` | `/v2/markets/{m}/ticker` | Single ticker | -- |
| `markets_tickers()` | `/v2/markets/tickers` | All tickers | -- |
| `balances()` | `/v2/balances` | Wallet balances | -- |
| `history_transactions(count=, direction=)` | `/v2/history/transactions` | Transaction history | `count`, `direction` |
| `history_transactions_year(year, direction=)` | `/v2/history/transactions/{year}` | Yearly transactions | `direction` |
| `history_transactions_month_year(month, year, direction=)` | `/v2/history/transactions/{month}/{year}` | Monthly transactions | `direction` |
| `history_orders(type=, count=)` | `/v2/history/orders` | Order history | `type`, `count` |
| `history_orders_market(m, type=, count=)` | `/v2/history/orders/{m}` | Market order history | `type`, `count` |
| `deposit_history(count=, before=)` | `/v2/deposit/history` | Deposit history | `count`, `before` |
| `deposit_address()` | `/v2/deposit/address` | Multi-coin deposit info | -- |
| `orders()` | `/v2/orders` | Active orders | -- |
| `orders_market(m, count=)` | `/v2/orders/{m}` | Active orders (market) | `count` |
| `orders_market_history(m, count=)` | `/v2/orders/{m}/history` | Closed orders (market) | `count` |
| `orders_history(count=)` | `/v2/orders/history` | Closed orders | `count` |
| `order(order_id)` | `/v2/order/{id}` | Get order | -- |
| `post_orders(market, type, price, amount)` | `/v2/orders` | Create order | -- |
| `delete_orders()` | `/v2/orders` | Cancel all orders | -- |
| `delete_orders_for_market(market)` | `/v2/orders/{market}` | Cancel market orders | -- |
| `delete_order_detailed(order_id, market=)` | `/v2/orders/{id}/detailed` | Cancel + matched amt | `market` |
| `coin_address(symbol)` | `/v2/{symbol}/address` | Coin deposit address | -- |
| `coin_withdraw_pending(symbol)` | `/v2/{symbol}/withdraw/pending` | Pending withdrawals | -- |

Default `count` is 500 (`DEFAULT_COUNT`). A warning is emitted above `MAX_COUNT` (10,000).

### Generic Coin Helpers

Instead of `btc_address()`, `eth_address()`, etc. you can use:

```python
await client.coin_address("BTC")
await client.coin_withdraw_pending("ETH")
```

Per-asset convenience methods remain available.

## Official Docs Sync

- Checked against [developers.firi.com](https://developers.firi.com/) (Trading API 1.0.0) on **2025-11-21**.
- When Firi updates their spec, diff it against the endpoint table above.
- Use the rate-limit guardrails (`DEFAULT_COUNT`, `MAX_COUNT`) to stay within API constraints.

## Contributing

Contributions welcome! Submit a pull request or create an issue on the [GitHub page](https://github.com/jeircul/firipy).

### Development Setup

```bash
git clone https://github.com/jeircul/firipy
cd firipy
uv sync
uv run pytest -q
```

Linting and type checking:

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
```

### go-task shortcuts (optional)

If you have [go-task](https://taskfile.dev) installed:

```bash
task install        # uv sync
task lint           # ruff check
task format         # ruff format
task typecheck      # ty check
task test           # pytest
task qa             # lint + typecheck + test
task balance        # print live balances (API_KEY_FIRI required)
task live-test      # read-only smoke against production (LIVE_FIRI_TESTS=1)
task build          # uv build (sdist + wheel)
task release-check  # qa + build
# Version bump helpers (patch by default)
task version PART=minor
task version NEW=1.1.0
task version DRY_RUN=1
```

### Release workflow

1. Document all changes under the `[Unreleased]` section in `CHANGELOG.md`.
2. Run `task version PART=major|minor|patch` (or `NEW=x.y.z`). This updates `pyproject.toml` and moves changelog entries into a dated section. Preview first with `DRY_RUN=1`.
3. Run `task release-check` to verify lint, type-check, tests, and build all pass.
4. Commit the version bump, push to a feature branch, open a PR into `main`, and merge once CI is green.
5. Tag `vX.Y.Z` on `main` (or draft a GitHub Release). Publishing the release triggers `publish.yml` which uploads to PyPI.
6. Optionally run `LIVE_FIRI_TESTS=1 task live-test` before tagging to smoke-test against production.
7. Quick manual check: `task balance` prints balances from `/v2/balances`.

## Migrating from v0.x

v1.0.0 is async-only and uses `httpx` instead of `requests`. See the [CHANGELOG](CHANGELOG.md#100---2026-03-08) for a full migration guide.

## Disclaimer

This client was developed by Ove Aursland and is not officially associated with Firi.
