import os
import warnings
import pytest

from firipy import FiriAPI, FiriHTTPError

API_KEY = os.getenv("API_KEY_FIRI")
LIVE = os.getenv("LIVE_FIRI_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not (LIVE and API_KEY), reason="Set LIVE_FIRI_TESTS=1 and API_KEY_FIRI to run live Firi API tests"
)


@pytest.mark.integration
def test_live_basic_read_only_endpoints():
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
    tx = client.history_transactions(5)
    assert isinstance(tx, (list, dict))

    client.close()


@pytest.mark.integration
def test_live_error_handling_raise():
    assert API_KEY is not None
    client = FiriAPI(API_KEY, raise_on_error=True)
    with pytest.raises(FiriHTTPError):
        # Intentionally invalid endpoint path to trigger a 4xx
        client.get("/this/endpoint/does/not/exist")


@pytest.mark.integration
def test_live_error_handling_suppressed():
    assert API_KEY is not None
    client = FiriAPI(API_KEY, raise_on_error=False)
    data = client.get("/this/endpoint/does/not/exist")
    assert "error" in data and data.get("status") in {400, 404}


@pytest.mark.integration
def test_live_deprecated_method_warning():
    assert API_KEY is not None
    client = FiriAPI(API_KEY, raise_on_error=False)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        client.eth_Address()
        assert any(issubclass(wi.category, DeprecationWarning) for wi in w)
