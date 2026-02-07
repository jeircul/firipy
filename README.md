# Firipy

[![Upload Python Package](https://github.com/jeircul/firipy/actions/workflows/publish.yml/badge.svg)](https://github.com/jeircul/firipy/actions/workflows/publish.yml)
[![Run Tests](https://github.com/jeircul/firipy/actions/workflows/run_tests.yml/badge.svg)](https://github.com/jeircul/firipy/actions/workflows/run_tests.yml)
![PyPI - Version](https://img.shields.io/pypi/v/firipy)
![GitHub](https://img.shields.io/github/license/jeircul/firipy)

Firipy is a ⚡ Python client for the Firi API.

## 📦 Installation

You can install Firipy using pip:

```bash
pip install firipy
```

## 🚀 Usage

First, import the `FiriAPI` class from the `firipy` module:

```python
from firipy import FiriAPI
```

Then, initialize the client with your API key from [Firi](https://platform.firi.com/).
You can generate an API key in your Firi account under **Settings > API**.

```python
client = FiriAPI("your-api-key")
```

Now you can use the client to interact with the Firi API. For example, to get the current time:

```python
time = client.time()
print(time)
```

To get history over all transactions:

```python
history = client.history_transactions()
print(history)
```

To get balances:

```python
balances = client.balances()
print(balances)
```

### Using as a context manager

Automatically closes the underlying HTTP session when done:

```python
from firipy import FiriAPI

with FiriAPI("your-api-key") as client:
    markets = client.markets()
    print(markets)
```

## ⏳ Rate Limiting

Firipy includes a rate limit (seconds to sleep before each request). By default this is 1 second.
You can change it or disable it:

```python
client = FiriAPI("your-api-key", rate_limit=2)  # wait 2 seconds between requests
client_fast = FiriAPI("your-api-key", rate_limit=0)  # no client-side delay
```

## 🚩 Error Handling

Structured exceptions are raised by default:

| Exception | Description |
|-----------|-------------|
| `FiriAPIError` | Base class for client errors |
| `FiriHTTPError` | Non-success HTTP responses (status >=400) |

Suppress exceptions by setting `raise_on_error=False`:

```python
client = FiriAPI("your-api-key", raise_on_error=False)
data = client.markets()
if "error" in data:
    print("Failed:", data)
```

Error dict shape: `{ "error": str, "status": int | None }`.

## 📡 Endpoint Overview (selection)

| Method | Endpoint | Purpose | Key Optional Params |
|--------|----------|---------|---------------------|
| `time()` | `/time` | Server time | – |
| `markets()` | `/v2/markets` | List markets | – |
| `markets_market(m)` | `/v2/markets/{m}` | Market details | – |
| `markets_market_depth(m, bids=None, asks=None)` | `/v2/markets/{m}/depth` | Order book | `bids`, `asks` |
| `markets_market_history(m, count=None)` | `/v2/markets/{m}/history` | Market trade history | `count` |
| `markets_market_ticker(m)` | `/v2/markets/{m}/ticker` | Single ticker | – |
| `markets_tickers()` | `/v2/markets/tickers` | All tickers | – |
| `balances()` | `/v2/balances` | Wallet balances | – |
| `history_transactions(count=None, direction=None)` | `/v2/history/transactions` | Transactions history | `count`, `direction` (`start`/`end`) |
| `history_transactions_year(year, direction=None)` | `/v2/history/transactions/{year}` | Transactions history (year) | `direction` |
| `history_transactions_month_year(month, year, direction=None)` | `/v2/history/transactions/{month}/{year}` | Transactions history (month+year) | `direction` |
| `history_orders(type=None, count=None)` | `/v2/history/orders` | Orders history | `type`, `count` |
| `history_orders_market(m, type=None, count=None)` | `/v2/history/orders/{m}` | Orders history (market) | `type`, `count` |
| `deposit_history(count=None, before=None)` | `/v2/deposit/history` | Deposit history | `count`, `before` |
| `deposit_address()` | `/v2/deposit/address` | Multi-coin deposit info | – |
| `orders()` | `/v2/orders` | Active orders | – |
| `orders_market(m, count=None)` | `/v2/orders/{m}` | Active orders (market) | `count` |
| `orders_market_history(m, count=None)` | `/v2/orders/{m}/history` | Closed orders (market) | `count` |
| `orders_history(count=None)` | `/v2/orders/history` | Closed orders | `count` |
| `order(order_id)` | `/v2/order/{id}` | Get order | – |
| `post_orders(market, type, price, amount)` | `/v2/orders` | Create order | – |
| `delete_orders()` | `/v2/orders` | Cancel all orders | – |
| `delete_orders_for_market(market)` | `/v2/orders/{market}` | Cancel orders for market | – |
| `delete_order_detailed(order_id, market=None)` | `/v2/orders/{id}/detailed` | Cancel order + matched amt | `market` |
| `coin_address(symbol)` | `/v2/{symbol}/address` | Coin deposit address | `symbol` (e.g. BTC) |
| `coin_withdraw_pending(symbol)` | `/v2/{symbol}/withdraw/pending` | Pending withdrawals | `symbol` |

Defaults like `count` fall back to 500 (internal `DEFAULT_COUNT`) when omitted. A warning is emitted if you go above the internal `MAX_COUNT` (10,000) so you can reconsider the request size.

## 🔗 Official Docs Sync

- Checked against [developers.firi.com](https://developers.firi.com/) (Trading API 1.0.0) on **2025-11-21** so every method above maps to a documented endpoint under Time, Market, History, Coin, Deposit, Order, and Balance.
- When Firi updates their spec, diff it against the table above plus the client methods to keep things in lockstep.
- Use the rate-limit guardrails (`DEFAULT_COUNT`, `MAX_COUNT`) to stay within the constraints noted in the public docs.

### Generic Coin Helpers

Instead of calling `btc_address()`, `eth_address()`, etc. directly you can write:

```python
client.coin_address("BTC")
client.coin_withdraw_pending("ETH")
```

Concrete per-asset helpers remain for convenience.

## 🔥 Contributing

Contributions to Firipy are welcome! Please submit a pull request or create an issue on the [GitHub page](https://github.com/jeircul/firipy).

### 🧪 Development Setup

```bash
git clone https://github.com/jeircul/firipy
cd firipy
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
```

Optional tooling:

```bash
ruff check .
mypy firipy
```

### 🛠️ go-task shortcuts (optional)

If you have [go-task](https://taskfile.dev) installed you can automate the usual workflows:

```bash
task install        # ensure venv + install dev extras
task lint           # ruff checks
task typecheck      # mypy
task test           # unit tests
task qa             # lint + typecheck + test
task balance        # print live balances (API_KEY_FIRI required)
task live-test      # read-only smoke against production (LIVE_FIRI_TESTS=1)
task build          # sdist + wheel
task release-check  # qa + build
# Version bump helpers (patch by default)
task version PART=minor
task version NEW=0.1.1
task version DRY_RUN=1
```

### Release workflow

1. Make sure `CHANGELOG.md` has everything for the upcoming release under the `Unreleased` section.
2. Run `task version PART=patch` (set `PART` or `NEW=x.y.z`). This updates `pyproject.toml` and moves the changelog entries into a dated section. Use `DRY_RUN=1` first if you want to preview.
3. Execute `task release-check` to rerun lint, type-check, tests, and the build.
4. Commit the version bump, push to `dev`, open a PR into `main`, and merge once CI is green.
5. Tag `vX.Y.Z` on `main` (or draft a GitHub Release). Publishing the release triggers the `publish.yml` workflow to upload to PyPI.
6. Optionally run `task live-test` with `LIVE_FIRI_TESTS=1 API_KEY_FIRI=...` before tagging to double-check against production.
7. Need a quick manual sanity check? `task balance` prints the raw payload returned by `/v2/balances` using your configured `API_KEY_FIRI`.

## 📝 Disclaimer

This client was developed by Ove Aursland and is not officially associated with Firi.
