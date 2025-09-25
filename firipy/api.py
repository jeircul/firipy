from __future__ import annotations

from typing import Any, Dict, Optional
from requests import Session, Response
from time import sleep
from requests.exceptions import HTTPError, RequestException
import logging
import warnings

__all__ = ["FiriAPI", "FiriAPIError", "FiriHTTPError"]

log = logging.getLogger(__name__)


class FiriAPIError(Exception):
    """Base exception for all Firi API client errors."""


class FiriHTTPError(FiriAPIError):
    """Raised when the Firi API returns a non-success HTTP status and raise_on_error=True."""

    def __init__(self, status_code: int, message: str, payload: Any | None = None):
        super().__init__(f"{status_code}: {message}")
        self.status_code = status_code
        self.payload = payload

class FiriAPI:
    """Client for the Firi API.

    Parameters
    ----------
    token : str
        API access token (miraiex-access-key) for authenticating with Firi.
    rate_limit : float, default 1.0
        Seconds to sleep before each request. Set to 0 to disable simple client-side pacing.
    base_url : str, default "https://api.firi.com"
        Base URL for the API (override for testing / mocking).
    timeout : float, default 10.0
        Per-request timeout in seconds passed to `requests`.
    raise_on_error : bool, default True
        If True, non-2xx responses raise :class:`FiriHTTPError`. If False, returns a dict
        with keys: ``{"error": str, "status": int}``.
    """

    DEFAULT_COUNT: int = 500
    MAX_COUNT: int = 10_000

    def __init__(
        self,
        token: str,
        *,
        rate_limit: float = 1.0,
        base_url: str = "https://api.firi.com",
        timeout: float = 10.0,
        raise_on_error: bool = True,
        session: Session | None = None,
    ):
        headers = {"miraiex-access-key": token}
        self.apiurl = base_url.rstrip("/")
        self.session = session or Session()
        self.session.headers.update(headers)
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.raise_on_error = raise_on_error
        self._token = token  # stored for potential future refresh; do not expose directly

    # --- Context manager support -------------------------------------------------
    def __enter__(self) -> "FiriAPI":  # pragma: no cover (trivial)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover (trivial)
        self.close()

    def close(self):  # pragma: no cover (simple)
        """Close the underlying requests session."""
        try:
            self.session.close()
        except Exception:  # defensive
            pass

    # --- Representation ----------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover (cosmetic)
        return (
            f"FiriAPI(base_url='{self.apiurl}', rate_limit={self.rate_limit}, "
            f"timeout={self.timeout}, raise_on_error={self.raise_on_error}, token='***')"
        )

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Send an HTTP request and return parsed JSON.

        Returns
        -------
        dict | list | Any
            Parsed JSON body. If ``raise_on_error`` is False and an HTTP error occurs,
            a dict with keys ``error`` and ``status`` is returned.
        """
        if self.rate_limit > 0:
            sleep(self.rate_limit)
        url = self.apiurl + endpoint
        try:
            response: Response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
        except HTTPError as http_err:
            status_code = getattr(http_err.response, "status_code", None)
            payload: Any | None = None
            try:
                if http_err.response is not None:
                    payload = http_err.response.json()
            except Exception:  # pragma: no cover - robustness
                payload = None
            message = None
            if isinstance(payload, dict):
                message = payload.get("message") or payload.get("error")
            if not message:
                message = str(http_err)
            if self.raise_on_error:
                raise FiriHTTPError(status_code or -1, message, payload)
            log.warning("HTTP error (%s) for %s %s: %s", status_code, method, url, message)
            return {"error": message, "status": status_code}
        except RequestException as err:
            if self.raise_on_error:
                raise FiriAPIError(str(err)) from err
            log.error("Request error for %s %s: %s", method, url, err)
            return {"error": str(err), "status": None}
        except Exception as err:  # pragma: no cover - unexpected defensive
            if self.raise_on_error:
                raise FiriAPIError(str(err)) from err
            log.exception("Unexpected error during request")
            return {"error": str(err), "status": None}
        else:
            try:
                return response.json()
            except ValueError:  # pragma: no cover - unlikely
                return {"error": "Invalid JSON in response", "status": response.status_code}

    def get(self, endpoint: str, **kwargs) -> Dict:
        """Send a GET request to the given endpoint."""
        return self._request("GET", endpoint, **kwargs)

    def delete(self, endpoint: str) -> Dict:
        """Send a DELETE request to the given endpoint."""
        return self._request("DELETE", endpoint)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Send a POST request to the given endpoint."""
        return self._request("POST", endpoint, json=data)

    def time(self) -> Dict:
        """Get the current time from the Firi API."""
        return self.get("/time")

    def history_transactions(self, count: Optional[int] = None) -> Dict:
        """Get history over all transactions.

        Parameters
        ----------
        count : int | None
            Number of records to request. If None, uses DEFAULT_COUNT. A warning is emitted if
            the provided count exceeds MAX_COUNT.
        """
        if count is None:
            count = self.DEFAULT_COUNT
        elif count > self.MAX_COUNT:
            warnings.warn(
                f"Requested count {count} exceeds MAX_COUNT {self.MAX_COUNT}; proceeding but this may be rejected by the API.",
                RuntimeWarning,
                stacklevel=2,
            )
        return self.get("/v2/history/transactions", params={"count": count})

    def history_transactions_year(self, year: str) -> Dict:
        """Get history over transactions by year."""
        return self.get(f"/v2/history/transactions/{year}")

    def history_transactions_month_year(self, month: str, year: str) -> Dict:
        """Get history over transactions by month and year."""
        return self.get(f"/v2/history/transactions/{month}/{year}")

    def history_trades(self) -> Dict:
        """Get history over all trades."""
        return self.get("/v2/history/trades")

    def history_trades_year(self, year: str) -> Dict:
        """Get history over trades by year."""
        return self.get(f"/v2/history/trades/{year}")

    def history_trades_month_year(self, month: str, year: str) -> Dict:
        """Get history over trades by month and year."""
        return self.get(f"/v2/history/trades/{month}/{year}")

    def history_orders(self) -> Dict:
        """Get history over all orders."""
        return self.get("/v2/history/orders")

    def history_orders_market(self, market: str) -> Dict:
        """Get history over orders by market."""
        return self.get(f"/v2/history/orders/{market}")

    def markets_market_history(self, market: str) -> Dict:
        """Get history over a specific market."""
        return self.get(f"/v2/markets/{market}/history")

    def markets_market_depth(self, market: str) -> Dict:
        """Get orderbooks for a market."""
        return self.get(f"/v2/markets/{market}/depth")

    def markets_market(self, market: str) -> Dict:
        """Get info about specific market."""
        return self.get(f"/v2/markets/{market}")

    def markets(self) -> Dict:
        """Get available markets."""
        return self.get("/v2/markets")

    def markets_market_ticker(self, market: str) -> Dict:
        """Get ticker for specific market."""
        return self.get(f"/v2/markets/{market}/ticker")

    def markets_tickers(self) -> Dict:
        """Get available tickers."""
        return self.get("/v2/markets/tickers")

    def xrp_withdraw_pending(self) -> Dict:
        """Get a user's pending XRP withdraws."""
        return self.get("/v2/XRP/withdraw/pending")

    def xrp_withdraw_address(self) -> Dict:
        """Get a user's XRP address."""
        return self.get("/v2/XRP/address")

    def ltc_withdraw_pending(self) -> Dict:
        """Get a user's pending LTC withdraws."""
        return self.get("/v2/LTC/withdraw/pending")

    def ltc_withdraw_address(self) -> Dict:
        """Get a user's LTC address."""
        return self.get("/v2/LTC/address")

    def eth_withdraw_pending(self) -> Dict:
        """Get a user's pending ETH withdraws."""
        return self.get("/v2/ETH/withdraw/pending")

    # --- Asset address endpoints (normalized names) ------------------------------
    def eth_address(self) -> Dict:
        """Get a user's ETH address."""
        return self.get("/v2/ETH/address")

    def eth_Address(self) -> Dict:  # backwards compatibility
        warnings.warn("eth_Address is deprecated; use eth_address", DeprecationWarning, stacklevel=2)
        return self.eth_address()

    def dai_withdraw_pending(self) -> Dict:
        """Get a user's pending DAI withdraws."""
        return self.get("/v2/DAI/withdraw/pending")

    def dai_address(self) -> Dict:
        """Get a user's DAI address."""
        return self.get("/v2/DAI/address")

    def dai_Address(self) -> Dict:  # deprecated
        warnings.warn("dai_Address is deprecated; use dai_address", DeprecationWarning, stacklevel=2)
        return self.dai_address()

    def dot_address(self) -> Dict:
        """Get a user's DOT address."""
        return self.get("/v2/DOT/address")

    def dot_Address(self) -> Dict:
        warnings.warn("dot_Address is deprecated; use dot_address", DeprecationWarning, stacklevel=2)
        return self.dot_address()

    def dot_withdraw_pending(self) -> Dict:
        """Get a user's pending DOT withdraws."""
        return self.get("/v2/DOT/withdraw/pending")

    def btc_withdraw_pending(self) -> Dict:
        """Get a user's pending BTC withdraws."""
        return self.get("/v2/BTC/withdraw/pending")

    def btc_address(self) -> Dict:
        """Get a user's BTC address."""
        return self.get("/v2/BTC/address")

    def btc_Address(self) -> Dict:
        warnings.warn("btc_Address is deprecated; use btc_address", DeprecationWarning, stacklevel=2)
        return self.btc_address()

    def ada_withdraw_pending(self) -> Dict:
        """Get a user's pending ADA withdraws."""
        return self.get("/v2/ADA/withdraw/pending")

    def ada_address(self) -> Dict:
        """Get a user's ADA address."""
        return self.get("/v2/ADA/address")

    def ada_Address(self) -> Dict:
        warnings.warn("ada_Address is deprecated; use ada_address", DeprecationWarning, stacklevel=2)
        return self.ada_address()

    def deposit_history(self, count: Optional[int] = None) -> Dict:
        """Get a user's history over deposits.

        Uses DEFAULT_COUNT if count is not provided and warns if exceeding MAX_COUNT.
        """
        if count is None:
            count = self.DEFAULT_COUNT
        elif count > self.MAX_COUNT:
            warnings.warn(
                f"Requested count {count} exceeds MAX_COUNT {self.MAX_COUNT}; proceeding but this may be rejected by the API.",
                RuntimeWarning,
                stacklevel=2,
            )
        return self.get("/v2/deposit/history", params={"count": count})

    def deposit_address(self) -> Dict:
        """Get a user's deposit address."""
        return self.get("/v2/deposit/address")

    def orders(self) -> Dict:
        """Get orders."""
        return self.get("/v2/orders")

    def orders_market(self, market: str) -> Dict:
        """Get all active orders for a specific market."""
        return self.get(f"/v2/orders/{market}")

    def orders_market_history(self, market: str) -> Dict:
        """Get all filled and closed orders for a specific market."""
        return self.get(f"/v2/orders/{market}/history")

    def orders_history(self) -> Dict:
        """Get all filled and closed orders."""
        return self.get("/v2/orders/history")

    def order_orderid(self, orderID: str) -> Dict:
        """Get order by orderId."""
        return self.get(f"/v2/order/{orderID}")

    def delete_orders(self) -> Dict:
        """Delete your orders."""
        return self.delete("/v2/orders")

    def delete_orders_orderid_market_detailed(self, orderID: str, market: str) -> Dict:
        """Delete your order by market and orderID, returns matched amount in cancelled order."""
        return self.delete(f"/v2/orders/{orderID}/{market}/detailed")

    def delete_orders_orderid_detailed(self, orderID: str) -> Dict:
        """Delete your order by orderID, returns matched amount in cancelled order."""
        return self.delete(f"/v2/orders/{orderID}/detailed")

    def delete_orders_marketormarketsid(self, marketOrMarketID: str) -> Dict:
        """Delete your orders by market.

        Deprecated naming retained for backward compatibility; prefer :meth:`delete_orders_for_market`.
        """
        warnings.warn(
            "delete_orders_marketormarketsid is deprecated; use delete_orders_for_market",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.delete_orders_for_market(marketOrMarketID)

    def delete_orders_for_market(self, market_or_market_id: str) -> Dict:
        """Delete your orders by market (preferred name)."""
        return self.delete(f"/v2/orders/{market_or_market_id}")

    def balances(self) -> Dict:
        """Check the balance for your wallets."""
        return self.get("/v2/balances")

    def post_orders(self, market: str, ordertype: str, price: str, amount: str) -> Dict:
        """Create your order."""
        data = {
            "market": market,
            "type": ordertype,
            "price": price,
            "amount": amount
        }
        return self.post("/v2/orders", data=data)
