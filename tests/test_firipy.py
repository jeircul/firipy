"""Unit tests for :mod:`firipy` using ``respx`` to mock HTTP calls."""

import asyncio
import time

import httpx
import pytest
import respx

from firipy import FiriAPI, FiriAPIError, FiriHTTPError
from firipy.api import (
    ACCESS_KEY_HEADER,
    LEGACY_ACCESS_KEY_HEADER,
    FiriAuthError,
    FiriRateLimitError,
)

API_KEY = "test-api-key"
BASE_URL = "https://api.firi.com"


@pytest.fixture
async def client() -> FiriAPI:
    return FiriAPI(API_KEY, rate_limit=0, base_url=BASE_URL)


@respx.mock
async def test_get_time(client: FiriAPI) -> None:
    """Ensure the time endpoint response is forwarded unchanged."""
    respx.get(f"{BASE_URL}/time").mock(
        return_value=httpx.Response(200, json={"serverTime": "2022-01-01T00:00:00Z"})
    )
    result = await client.time()
    assert result == {"serverTime": "2022-01-01T00:00:00Z"}


@respx.mock
async def test_history_transactions(client: FiriAPI) -> None:
    """Verify defaults when pulling transaction history."""
    respx.get(f"{BASE_URL}/v2/history/transactions").mock(
        return_value=httpx.Response(200, json=[{"id": "1", "amount": "0.1"}])
    )
    result = await client.history_transactions()
    assert result == [{"id": "1", "amount": "0.1"}]
    # Default count=500 should be sent as query param
    assert respx.calls.last is not None
    assert respx.calls.last.request.url.params["count"] == "500"


@respx.mock
async def test_history_transactions_year(client: FiriAPI) -> None:
    """Ensure yearly transaction helper relays parameters correctly."""
    respx.get(f"{BASE_URL}/v2/history/transactions/2023").mock(
        return_value=httpx.Response(200, json=[{"id": "1", "amount": "0.1"}])
    )
    result = await client.history_transactions_year("2023")
    assert result == [{"id": "1", "amount": "0.1"}]


@respx.mock
async def test_history_transactions_month_year(client: FiriAPI) -> None:
    """Confirm month/year helper feeds path parameters as expected."""
    respx.get(f"{BASE_URL}/v2/history/transactions/6/2023").mock(
        return_value=httpx.Response(200, json=[{"id": "1", "amount": "0.1"}])
    )
    result = await client.history_transactions_month_year("6", "2023")
    assert result == [{"id": "1", "amount": "0.1"}]


@respx.mock
async def test_post_orders(client: FiriAPI) -> None:
    """Verify payloads are forwarded when placing orders."""
    respx.post(f"{BASE_URL}/v2/orders").mock(
        return_value=httpx.Response(200, json={"orderId": "123", "status": "placed"})
    )
    result = await client.post_orders("BTCNOK", "limit", "500000", "0.01")
    assert isinstance(result, dict)
    assert result["orderId"] == "123"


@respx.mock
async def test_history_transactions_with_params(client: FiriAPI) -> None:
    """Pass optional filters through to the request layer."""
    respx.get(f"{BASE_URL}/v2/history/transactions").mock(
        return_value=httpx.Response(200, json=[])
    )
    await client.history_transactions(count=250, direction="start")
    assert respx.calls.last is not None
    assert respx.calls.last.request.url.params["count"] == "250"
    assert respx.calls.last.request.url.params["direction"] == "start"


@respx.mock
async def test_markets_market_depth_with_params(client: FiriAPI) -> None:
    """Check optional depth arguments propagate to the request payload."""
    respx.get(f"{BASE_URL}/v2/markets/BTCNOK/depth").mock(
        return_value=httpx.Response(200, json={"bids": [], "asks": []})
    )
    await client.markets_market_depth("BTCNOK", bids=5, asks=10)
    assert respx.calls.last is not None
    assert respx.calls.last.request.url.params["bids"] == "5"
    assert respx.calls.last.request.url.params["asks"] == "10"


@respx.mock
async def test_deposit_history_before(client: FiriAPI) -> None:
    """Ensure both count and before arguments are honored for deposits."""
    respx.get(f"{BASE_URL}/v2/deposit/history").mock(
        return_value=httpx.Response(200, json={"transactions": []})
    )
    await client.deposit_history(count=100, before=123456)
    assert respx.calls.last is not None
    assert respx.calls.last.request.url.params["count"] == "100"
    assert respx.calls.last.request.url.params["before"] == "123456"


@respx.mock
async def test_orders_market_count(client: FiriAPI) -> None:
    """Honor the count filter when fetching orders for a market."""
    respx.get(f"{BASE_URL}/v2/orders/BTCNOK").mock(
        return_value=httpx.Response(200, json=[])
    )
    await client.orders_market("BTCNOK", count=50)
    assert respx.calls.last is not None
    assert respx.calls.last.request.url.params["count"] == "50"


@respx.mock
async def test_coin_generic_helpers(client: FiriAPI) -> None:
    """Ensure the generic coin helper builds the proper endpoint."""
    respx.get(f"{BASE_URL}/v2/BTC/address").mock(
        return_value=httpx.Response(200, json={"address": "xyz"})
    )
    result = await client.coin_address("BTC")
    assert result == {"address": "xyz"}


@respx.mock
async def test_delete_order_detailed_market(client: FiriAPI) -> None:
    """Preferred delete helper should include the market when provided."""
    respx.delete(f"{BASE_URL}/v2/orders/345/BTCNOK/detailed").mock(
        return_value=httpx.Response(200, json={"matched": "0.0"})
    )
    result = await client.delete_order_detailed("345", market="BTCNOK")
    assert result == {"matched": "0.0"}


@respx.mock
async def test_raise_on_error_false_returns_error_dict() -> None:
    """Return an error payload when raise_on_error is disabled."""
    respx.get(f"{BASE_URL}/v2/markets").mock(
        return_value=httpx.Response(400, json={"error": "Bad Request"})
    )
    client = FiriAPI(API_KEY, rate_limit=0, raise_on_error=False)
    data = await client.get("/v2/markets")
    assert isinstance(data, dict)
    assert "error" in data
    assert data["status"] == 400


@respx.mock
async def test_raise_on_error_true_raises_http_error() -> None:
    """Raise FiriHTTPError when raise_on_error is enabled."""
    respx.get(f"{BASE_URL}/v2/markets").mock(
        return_value=httpx.Response(404, json={"message": "Not Found"})
    )
    client = FiriAPI(API_KEY, rate_limit=0, raise_on_error=True)
    with pytest.raises(FiriHTTPError) as exc_info:
        await client.get("/v2/markets")
    assert exc_info.value.status_code == 404


@respx.mock
async def test_network_error_raises_api_error() -> None:
    """Raise FiriAPIError on transport-level failures."""
    respx.get(f"{BASE_URL}/v2/markets").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )
    client = FiriAPI(API_KEY, rate_limit=0, raise_on_error=True)
    with pytest.raises(FiriAPIError, match="Connection refused"):
        await client.get("/v2/markets")


@respx.mock
async def test_network_error_suppressed() -> None:
    """Return error dict on transport failure when raise_on_error is False."""
    respx.get(f"{BASE_URL}/v2/markets").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )
    client = FiriAPI(API_KEY, rate_limit=0, raise_on_error=False)
    data = await client.get("/v2/markets")
    assert isinstance(data, dict)
    assert "error" in data
    assert data["status"] is None


async def test_context_manager() -> None:
    """Ensure the async context manager closes the underlying client."""
    async with FiriAPI(API_KEY, rate_limit=0) as client:
        assert client is not None
    # After exit, the client should be closed
    assert client.client.is_closed


async def test_injected_client_not_closed_by_aclose() -> None:
    """aclose() must be a no-op when the client was injected by the caller."""
    inner = httpx.AsyncClient(headers={"miraiex-access-key": API_KEY})
    api = FiriAPI(API_KEY, rate_limit=0, client=inner)
    await api.aclose()
    assert not inner.is_closed, "FiriAPI must not close a caller-owned client"
    await inner.aclose()


async def test_injected_client_headers_not_mutated() -> None:
    """FiriAPI must not add or change headers on an injected client."""
    inner = httpx.AsyncClient(headers={"miraiex-access-key": "caller-set-value"})
    original = dict(inner.headers)
    FiriAPI("different-api-key", rate_limit=0, client=inner)
    assert dict(inner.headers) == original, (
        "FiriAPI must not mutate headers on a caller-owned client"
    )
    await inner.aclose()


async def test_injected_client_missing_auth_header_raises() -> None:
    """FiriAPI must raise ValueError when injected client has no auth header."""
    bare = httpx.AsyncClient()
    with pytest.raises(ValueError, match="miraiex-access-key"):
        FiriAPI(API_KEY, rate_limit=0, client=bare)
    await bare.aclose()


@pytest.mark.parametrize(
    "method_name,endpoint",
    [
        ("eth_address", "/v2/ETH/address"),
        ("btc_withdraw_pending", "/v2/BTC/withdraw/pending"),
        ("ada_address", "/v2/ADA/address"),
    ],
)
@respx.mock
async def test_per_coin_helpers_emit_deprecation_warning(
    method_name: str, endpoint: str
) -> None:
    """Per-coin convenience methods must emit DeprecationWarning."""
    api = FiriAPI(API_KEY, rate_limit=0)
    respx.get(f"{BASE_URL}{endpoint}").mock(return_value=httpx.Response(200, json={}))
    with pytest.warns(DeprecationWarning):
        await getattr(api, method_name)()


async def test_self_created_client_has_both_access_key_headers() -> None:
    """A self-created client must send both current and legacy auth headers."""
    api = FiriAPI(API_KEY, rate_limit=0)
    assert api.client.headers[ACCESS_KEY_HEADER] == API_KEY
    assert api.client.headers[LEGACY_ACCESS_KEY_HEADER] == API_KEY
    await api.aclose()


async def test_injected_client_with_only_legacy_header_is_accepted() -> None:
    """Injecting a client with only the legacy header must not raise."""
    inner = httpx.AsyncClient(headers={LEGACY_ACCESS_KEY_HEADER: API_KEY})
    api = FiriAPI(API_KEY, rate_limit=0, client=inner)
    assert api.client is inner
    await inner.aclose()


@respx.mock
async def test_first_request_not_delayed() -> None:
    """The first request must not be delayed by the pacing gate."""
    respx.get(f"{BASE_URL}/time").mock(
        return_value=httpx.Response(200, json={"serverTime": "now"})
    )
    client = FiriAPI(API_KEY, rate_limit=0.2, base_url=BASE_URL)
    start = time.monotonic()
    await client.time()
    elapsed = time.monotonic() - start
    assert elapsed < 0.15
    await client.aclose()


@respx.mock
async def test_concurrent_requests_are_paced() -> None:
    """Concurrent requests must be serialized by the pacing gate, not parallel."""
    respx.get(f"{BASE_URL}/time").mock(
        return_value=httpx.Response(200, json={"serverTime": "now"})
    )
    client = FiriAPI(API_KEY, rate_limit=0.05, base_url=BASE_URL)
    start = time.monotonic()
    await asyncio.gather(client.time(), client.time(), client.time())
    elapsed = time.monotonic() - start
    assert elapsed >= 0.08
    await client.aclose()


@respx.mock
async def test_get_retries_once_after_503() -> None:
    """A GET returning 503 then 200 must succeed after one retry."""
    route = respx.get(f"{BASE_URL}/v2/markets").mock(
        side_effect=[
            httpx.Response(503, json={"message": "unavailable"}),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    client = FiriAPI(
        API_KEY, rate_limit=0, base_url=BASE_URL, max_retries=2, backoff_base=0.01
    )
    result = await client.get("/v2/markets")
    assert result == {"ok": True}
    assert route.call_count == 2
    await client.aclose()


@respx.mock
async def test_get_honors_retry_after_on_429() -> None:
    """A 429 with a numeric Retry-After header must be honored on retry."""
    route = respx.get(f"{BASE_URL}/v2/markets").mock(
        side_effect=[
            httpx.Response(
                429, json={"message": "too many"}, headers={"Retry-After": "0"}
            ),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    client = FiriAPI(
        API_KEY, rate_limit=0, base_url=BASE_URL, max_retries=2, backoff_base=0.01
    )
    result = await client.get("/v2/markets")
    assert result == {"ok": True}
    assert route.call_count == 2
    await client.aclose()


@respx.mock
async def test_get_raises_rate_limit_error_when_retries_exhausted() -> None:
    """Persistent 429s must eventually raise FiriRateLimitError."""
    route = respx.get(f"{BASE_URL}/v2/markets").mock(
        return_value=httpx.Response(
            429, json={"message": "too many"}, headers={"Retry-After": "0"}
        )
    )
    client = FiriAPI(
        API_KEY, rate_limit=0, base_url=BASE_URL, max_retries=1, backoff_base=0.01
    )
    with pytest.raises(FiriRateLimitError):
        await client.get("/v2/markets")
    assert route.call_count == 2
    await client.aclose()


@respx.mock
async def test_post_503_is_not_retried() -> None:
    """POST is not idempotent and must not be retried on 503."""
    route = respx.post(f"{BASE_URL}/v2/orders").mock(
        return_value=httpx.Response(503, json={"message": "unavailable"})
    )
    client = FiriAPI(
        API_KEY, rate_limit=0, base_url=BASE_URL, max_retries=2, backoff_base=0.01
    )
    with pytest.raises(FiriHTTPError):
        await client.post_orders("BTCNOK", "limit", "500000", "0.01")
    assert route.call_count == 1
    await client.aclose()


@respx.mock
async def test_get_raises_http_error_after_retries_exhausted() -> None:
    """Persistent 503s must raise FiriHTTPError after max_retries+1 attempts."""
    route = respx.get(f"{BASE_URL}/v2/markets").mock(
        return_value=httpx.Response(503, json={"message": "unavailable"})
    )
    client = FiriAPI(
        API_KEY, rate_limit=0, base_url=BASE_URL, max_retries=2, backoff_base=0.01
    )
    with pytest.raises(FiriHTTPError):
        await client.get("/v2/markets")
    assert route.call_count == 3
    await client.aclose()


@respx.mock
async def test_auth_error_exposes_error_name() -> None:
    """A 401 with a machine-readable error name must raise FiriAuthError."""
    respx.get(f"{BASE_URL}/v2/markets").mock(
        return_value=httpx.Response(
            401, json={"name": "ApiKeyNotFound", "message": "Invalid API key"}
        )
    )
    client = FiriAPI(API_KEY, rate_limit=0, base_url=BASE_URL)
    with pytest.raises(FiriAuthError) as exc_info:
        await client.get("/v2/markets")
    assert exc_info.value.error_name == "ApiKeyNotFound"
    await client.aclose()
