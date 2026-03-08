"""Live integration tests that hit the real Firi API."""

import os

import pytest

from firipy import FiriAPI, FiriHTTPError

API_KEY: str | None = os.getenv("API_KEY_FIRI")
LIVE: bool = os.getenv("LIVE_FIRI_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not (LIVE and API_KEY),
    reason="Set LIVE_FIRI_TESTS=1 and API_KEY_FIRI to run live Firi API tests",
)


@pytest.mark.integration
async def test_live_basic_read_only_endpoints() -> None:
    """Exercise key read-only endpoints against the live API."""
    assert API_KEY is not None
    async with FiriAPI(API_KEY, rate_limit=0.3, raise_on_error=True) as client:
        t = await client.time()
        assert isinstance(t, dict) and t, "time() should return non-empty dict"

        markets = await client.markets()
        assert isinstance(markets, list | dict)

        balances = await client.balances()
        assert isinstance(balances, list | dict)

        tx = await client.history_transactions(count=5)
        assert isinstance(tx, list | dict)


@pytest.mark.integration
async def test_live_error_handling_raise() -> None:
    """Validate that raise_on_error propagates live HTTP failures."""
    assert API_KEY is not None
    async with FiriAPI(API_KEY, raise_on_error=True) as client:
        with pytest.raises(FiriHTTPError):
            await client.get("/this/endpoint/does/not/exist")


@pytest.mark.integration
async def test_live_error_handling_suppressed() -> None:
    """Ensure raise_on_error=False surfaces structured error responses."""
    assert API_KEY is not None
    async with FiriAPI(API_KEY, raise_on_error=False) as client:
        data = await client.get("/this/endpoint/does/not/exist")
        assert isinstance(data, dict)
        assert "error" in data and data.get("status") in {400, 404}
