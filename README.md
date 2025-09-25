# Firipy

[![Upload Python Package](https://github.com/jeircul/firipy/actions/workflows/publish.yml/badge.svg)](https://github.com/jeircul/firipy/actions/workflows/publish.yml)
[![Run Tests](https://github.com/jeircul/firipy/actions/workflows/run_tests.yml/badge.svg)](https://github.com/jeircul/firipy/actions/workflows/run_tests.yml)
![PyPI - Version](https://img.shields.io/pypi/v/firipy)
![GitHub](https://img.shields.io/github/license/jeircul/firipy)

Firipy is a Python client for the Firi API.

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

Then, initialize the client with your API token from [Firi](https://platform.firi.com/):

```python
client = FiriAPI("your-token")
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

with FiriAPI("your-token") as client:
    markets = client.markets()
    print(markets)
```

## ⏳ Rate Limiting

Firipy includes a rate limit (seconds to sleep before each request). By default this is 1 second.
You can change it or disable it:

```python
client = FiriAPI("your-token", rate_limit=2)  # wait 2 seconds between requests
client_fast = FiriAPI("your-token", rate_limit=0)  # no client-side delay
```

## 🚩 Error Handling

Structured exceptions are raised by default:

| Exception | Description |
|-----------|-------------|
| `FiriAPIError` | Base class for client errors |
| `FiriHTTPError` | Non-success HTTP responses (status >=400) |

Suppress exceptions by setting `raise_on_error=False`:

```python
client = FiriAPI("your-token", raise_on_error=False)
data = client.markets()
if "error" in data:
    print("Failed:", data)
```

Error dict shape: `{ "error": str, "status": int | None }`.

Legacy camelCase address methods (e.g. `eth_Address`) are deprecated—use `eth_address`. They emit a `DeprecationWarning` and will be removed in a future release.

## 📡 Endpoint Overview (selection)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `time()` | `/time` | Server time |
| `markets()` | `/v2/markets` | List markets |
| `markets_market(m)` | `/v2/markets/{m}` | Market details |
| `markets_market_depth(m)` | `/v2/markets/{m}/depth` | Order book |
| `markets_market_history(m)` | `/v2/markets/{m}/history` | Market history |
| `balances()` | `/v2/balances` | Wallet balances |
| `history_transactions(count=None)` | `/v2/history/transactions` | Transactions history |
| `deposit_history(count=None)` | `/v2/deposit/history` | Deposit history |
| `post_orders(market, type, price, amount)` | `/v2/orders` | Create order |
| `delete_orders()` | `/v2/orders` | Cancel all orders |

Defaults like `count` are limited to a safe value (500) unless explicitly overridden.

## 🔥 Contributing

Contributions to Firipy are welcome! Please submit a pull request or create an issue on the [GitHub page](https://github.com/jeircul/firipy).

### Development Setup

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

### Using go-task (optional)

If you have [go-task](https://taskfile.dev) installed you can automate workflows:

```bash
task install       # create venv & install deps
task lint          # ruff checks
task typecheck     # mypy
task test          # run tests
task coverage      # coverage report
task release-check # lint + typecheck + coverage + build
```

## 📝 Disclaimer

This client was developed by Ove Aursland and is not officially associated with Firi.
