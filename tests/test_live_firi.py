"""Live integration tests that hit the real Firi API via ``pytest``."""

import os

import pytest

from firipy import FiriAPI, FiriHTTPError

API_KEY: str | None = os.getenv("API_KEY_FIRI")
LIVE: bool = os.getenv("LIVE_FIRI_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not (LIVE and API_KEY),
    reason=(
        "Set LIVE_FIRI_TESTS=1 and API_KEY_FIRI to run live Firi API tests"
    ),
)


@pytest.mark.integration
def test_live_basic_read_only_endpoints() -> None:
    """Exercise key read-only endpoints against the live API."""
    assert API_KEY is not None  # for type checker
    client = FiriAPI(API_KEY, rate_limit=0.3, raise_on_error=True)
    # Time endpoint
    t = client.time()
    assert isinstance(t, dict) and t, "time() should return non-empty dict"

    # Markets
    markets = client.markets()
    assert isinstance(markets, (list, dict))

    # Balances (auth required)
    balances = client.balances()
    assert isinstance(balances, (list, dict))

    # Transaction history limited count
    tx = client.history_transactions(count=5)
    assert isinstance(tx, (list, dict))

    client.close()


@pytest.mark.integration
def test_live_error_handling_raise() -> None:
    """Validate that raise_on_error propagates live HTTP failures."""
    assert API_KEY is not None
    client = FiriAPI(API_KEY, raise_on_error=True)
    with pytest.raises(FiriHTTPError):
        # Intentionally invalid endpoint path to trigger a 4xx
        client.get("/this/endpoint/does/not/exist")


@pytest.mark.integration
def test_live_error_handling_suppressed() -> None:
    """Ensure raise_on_error=False surfaces structured error responses."""
    assert API_KEY is not None
    client = FiriAPI(API_KEY, raise_on_error=False)
    data = client.get("/this/endpoint/does/not/exist")
    assert isinstance(data, dict)
    assert "error" in data and data.get("status") in {400, 404}

