"""Firi API client built on ``requests.Session`` for HTTP requests."""

from __future__ import annotations

import logging
import warnings
from time import sleep
from typing import Any, Dict, Iterable, Optional

from requests import Response, Session
from requests.exceptions import HTTPError, RequestException

__all__ = ["FiriAPI", "FiriAPIError", "FiriHTTPError"]

log = logging.getLogger(__name__)


class FiriAPIError(Exception):
    """Base exception for all Firi API client errors."""


class FiriHTTPError(FiriAPIError):
    """Raised when ``raise_on_error`` handles non-success HTTP responses."""

    def __init__(
        self,
        status_code: int,
        message: str,
        payload: Any | None = None,
    ):
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
        Seconds to sleep before each request. Set to 0 to disable simple
        client-side pacing.
    base_url : str, default "https://api.firi.com"
        Base URL for the API (override for testing / mocking).
    timeout : float, default 10.0
        Per-request timeout in seconds passed to `requests`.
    raise_on_error : bool, default True
        If True, non-2xx responses raise :class:`FiriHTTPError`. If False,
        returns a dict with keys ``{"error": str, "status": int}``.
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
        self._token = token  # stored for potential refresh; kept private

    # --- Context manager helpers -------------------------------------------
    def __enter__(self) -> "FiriAPI":  # pragma: no cover
        """Enter context by returning the current client."""
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover
        """Exit context by closing the underlying session."""
        self.close()

    def close(self) -> None:  # pragma: no cover (simple)
        """Close the underlying requests session."""
        try:
            self.session.close()
        except Exception:  # defensive
            pass

    # --- Representation ----------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return (
            "FiriAPI("
            f"base_url='{self.apiurl}', "
            f"rate_limit={self.rate_limit}, "
            f"timeout={self.timeout}, "
            f"raise_on_error={self.raise_on_error}, token='***')"
        )

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Send an HTTP request and return parsed JSON.

        Returns
        -------
        dict | list | Any
            Parsed JSON body. If ``raise_on_error`` is False and an HTTP
            error occurs, a dict with keys ``error`` and ``status`` is
            returned.
        """
        if self.rate_limit > 0:
            sleep(self.rate_limit)
        url = self.apiurl + endpoint
        try:
            response: Response = self.session.request(
                method, url, timeout=self.timeout, **kwargs
            )
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
            log.warning(
                "HTTP error (%s) for %s %s: %s",
                status_code,
                method,
                url,
                message,
            )
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
                return {
                    "error": "Invalid JSON in response",
                    "status": response.status_code,
                }

    def get(self, endpoint: str, **kwargs) -> Dict:
        """Send a GET request to the given endpoint."""
        return self._request("GET", endpoint, **kwargs)

    def delete(self, endpoint: str) -> Dict:
        """Send a DELETE request to the given endpoint."""
        return self._request("DELETE", endpoint)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Send a POST request to the given endpoint."""
        return self._request("POST", endpoint, json=data)

    # --- Internal helpers --------------------------------------------------
    def _validate_choice(
        self, name: str, value: Optional[str], choices: Iterable[str]
    ) -> Optional[str]:
        """Ensure provided values stay within the allowed choices."""
        if value is None:
            return None
        ordered_choices = sorted(choices)
        if value not in ordered_choices:
            raise ValueError(
                f"{name} must be one of {ordered_choices} (got {value!r})"
            )
        return value

    def _validate_int(
        self,
        name: str,
        value: Optional[int],
        *,
        minimum: int = 1,
        maximum: Optional[int] = None,
    ) -> Optional[int]:
        """Validate integer bounds while allowing optional input."""
        if value is None:
            return None
        if value < minimum:
            raise ValueError(f"{name} must be >= {minimum} (got {value})")
        if maximum is not None and value > maximum:
            warnings.warn(
                (
                    f"Requested {name} {value} exceeds maximum {maximum}; "
                    "proceeding but the API may reject it."
                ),
                RuntimeWarning,
                stacklevel=3,
            )
        return value

    def time(self) -> Dict:
        """Get the current time from the Firi API."""
        return self.get("/time")

    def history_transactions(
        self, *, count: Optional[int] = None, direction: Optional[str] = None
    ) -> Dict:
        """Get history over all transactions.

        Parameters
        ----------
        count : int | None
            Number of records to request. Defaults to DEFAULT_COUNT when
            omitted.
        direction : {'start', 'end'} | None
            Pagination direction as documented by the API.
        """
        params: Dict[str, Any] = {}
        count = self._validate_int(
            "count", count or self.DEFAULT_COUNT, maximum=self.MAX_COUNT
        )
        params["count"] = count
        if self._validate_choice("direction", direction, {"start", "end"}):
            params["direction"] = direction  # type: ignore[assignment]
        return self.get("/v2/history/transactions", params=params)

    def history_transactions_year(
        self, year: str, *, direction: Optional[str] = None
    ) -> Dict:
        """Get history over transactions by year."""
        params: Dict[str, Any] = {}
        if self._validate_choice("direction", direction, {"start", "end"}):
            params["direction"] = direction  # type: ignore[assignment]
        return self.get(
            f"/v2/history/transactions/{year}", params=params or None
        )

    def history_transactions_month_year(
        self, month: str, year: str, *, direction: Optional[str] = None
    ) -> Dict:
        """Get history over transactions by month and year."""
        params: Dict[str, Any] = {}
        if self._validate_choice("direction", direction, {"start", "end"}):
            params["direction"] = direction  # type: ignore[assignment]
        return self.get(
            f"/v2/history/transactions/{month}/{year}", params=params or None
        )

    def history_orders(
        self, *, type: Optional[str] = None, count: Optional[int] = None
    ) -> Dict:  # noqa: A003
        """Get history over all orders.

        Parameters
        ----------
        type : str | None
            Order type filter as documented by the API.
        count : int | None
            Number of records to request (defaults to DEFAULT_COUNT).
        """
        params: Dict[str, Any] = {}
        count = self._validate_int(
            "count", count or self.DEFAULT_COUNT, maximum=self.MAX_COUNT
        )
        params["count"] = count
        if type is not None:
            params["type"] = type
        return self.get("/v2/history/orders", params=params)

    def history_orders_market(
        self,
        market: str,
        *,
        type: Optional[str] = None,
        count: Optional[int] = None,
    ) -> Dict:  # noqa: A003
        """Get history over orders by market."""
        params: Dict[str, Any] = {}
        count = self._validate_int(
            "count", count or self.DEFAULT_COUNT, maximum=self.MAX_COUNT
        )
        params["count"] = count
        if type is not None:
            params["type"] = type
        return self.get(f"/v2/history/orders/{market}", params=params)

    def markets_market_history(
        self, market: str, *, count: Optional[int] = None
    ) -> Dict:
        """Get history over a specific market."""
        params: Dict[str, Any] = {}
        if count is not None:
            count = self._validate_int("count", count, maximum=self.MAX_COUNT)
            params["count"] = count
        return self.get(f"/v2/markets/{market}/history", params=params or None)

    def markets_market_depth(
        self,
        market: str,
        *,
        bids: Optional[int] = None,
        asks: Optional[int] = None,
    ) -> Dict:
        """Get orderbooks for a market."""
        params: Dict[str, Any] = {}
        if bids is not None:
            params["bids"] = self._validate_int("bids", bids)
        if asks is not None:
            params["asks"] = self._validate_int("asks", asks)
        return self.get(f"/v2/markets/{market}/depth", params=params or None)

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
        return self.coin_withdraw_pending("XRP")

    def xrp_withdraw_address(self) -> Dict:
        """Get a user's XRP address."""
        return self.coin_address("XRP")

    def ltc_withdraw_pending(self) -> Dict:
        """Get a user's pending LTC withdraws."""
        return self.coin_withdraw_pending("LTC")

    def ltc_withdraw_address(self) -> Dict:
        """Get a user's LTC address."""
        return self.coin_address("LTC")

    def eth_withdraw_pending(self) -> Dict:
        """Get a user's pending ETH withdraws."""
        return self.coin_withdraw_pending("ETH")

    # --- Asset address endpoints (normalized names) -------------------------
    def eth_address(self) -> Dict:
        """Get a user's ETH address."""
        return self.coin_address("ETH")

    def dai_withdraw_pending(self) -> Dict:
        """Get a user's pending DAI withdraws."""
        return self.coin_withdraw_pending("DAI")

    def dai_address(self) -> Dict:
        """Get a user's DAI address."""
        return self.coin_address("DAI")

    def dot_address(self) -> Dict:
        """Get a user's DOT address."""
        return self.coin_address("DOT")

    def dot_withdraw_pending(self) -> Dict:
        """Get a user's pending DOT withdraws."""
        return self.coin_withdraw_pending("DOT")

    def btc_withdraw_pending(self) -> Dict:
        """Get a user's pending BTC withdraws."""
        return self.coin_withdraw_pending("BTC")

    def btc_address(self) -> Dict:
        """Get a user's BTC address."""
        return self.coin_address("BTC")

    def ada_withdraw_pending(self) -> Dict:
        """Get a user's pending ADA withdraws."""
        return self.coin_withdraw_pending("ADA")

    def ada_address(self) -> Dict:
        """Get a user's ADA address."""
        return self.coin_address("ADA")

    def deposit_history(
        self, *, count: Optional[int] = None, before: Optional[int] = None
    ) -> Dict:
        """Get a user's history over deposits.

        Parameters
        ----------
        count : int | None
            Number of records (defaults to DEFAULT_COUNT if omitted).
        before : int | None
            Fetch deposits before this API-defined numeric cursor or timestamp.
        """
        params: Dict[str, Any] = {}
        count = self._validate_int(
            "count", count or self.DEFAULT_COUNT, maximum=self.MAX_COUNT
        )
        params["count"] = count
        if before is not None:
            params["before"] = before
        return self.get("/v2/deposit/history", params=params)

    def deposit_address(self) -> Dict:
        """Get a user's deposit address."""
        return self.get("/v2/deposit/address")

    def orders(self) -> Dict:
        """Get orders."""
        return self.get("/v2/orders")

    def orders_market(
        self, market: str, *, count: Optional[int] = None
    ) -> Dict:
        """Get all active orders for a specific market."""
        params: Dict[str, Any] = {}
        if count is not None:
            params["count"] = self._validate_int(
                "count", count, maximum=self.MAX_COUNT
            )
        return self.get(f"/v2/orders/{market}", params=params or None)

    def orders_market_history(
        self, market: str, *, count: Optional[int] = None
    ) -> Dict:
        """Get all filled and closed orders for a specific market."""
        params: Dict[str, Any] = {}
        if count is not None:
            params["count"] = self._validate_int(
                "count", count, maximum=self.MAX_COUNT
            )
        return self.get(f"/v2/orders/{market}/history", params=params or None)

    def orders_history(self, *, count: Optional[int] = None) -> Dict:
        """Get all filled and closed orders."""
        params: Dict[str, Any] = {}
        if count is not None:
            params["count"] = self._validate_int(
                "count", count, maximum=self.MAX_COUNT
            )
        return self.get("/v2/orders/history", params=params or None)

    def order_orderid(self, orderID: str) -> Dict:
        """Get order by orderId."""
        return self.get(f"/v2/order/{orderID}")

    # New concise alias
    def order(self, order_id: str) -> Dict:
        """Get order by order id (preferred concise alias)."""
        return self.order_orderid(order_id)

    def delete_orders(self) -> Dict:
        """Delete your orders."""
        return self.delete("/v2/orders")

    def delete_orders_for_market(self, market_or_market_id: str) -> Dict:
        """Delete your orders by market (preferred name)."""
        return self.delete(f"/v2/orders/{market_or_market_id}")

    # New concise deletion helper
    def delete_order_detailed(
        self, order_id: str, *, market: Optional[str] = None
    ) -> Dict:
        """Delete an order and return matched amount if supported.

        Parameters
        ----------
        order_id : str
            ID of the order.
        market : str | None
            If provided, uses the market-specific detailed deletion endpoint.
        """
        if market:
            return self.delete(f"/v2/orders/{order_id}/{market}/detailed")
        return self.delete(f"/v2/orders/{order_id}/detailed")

    def balances(self) -> Dict:
        """Check the balance for your wallets."""
        return self.get("/v2/balances")

    def post_orders(
        self, market: str, ordertype: str, price: str, amount: str
    ) -> Dict:
        """Create your order."""
        data = {
            "market": market,
            "type": ordertype,
            "price": price,
            "amount": amount,
        }
        return self.post("/v2/orders", data=data)

    # --- Generic coin helpers ----------------------------------------------
    def coin_address(self, symbol: str) -> Dict:
        """Get a deposit/address for a coin symbol (e.g. 'BTC', 'ETH').

        Parameters
        ----------
        symbol : str
            Upper-case asset symbol.
        """
        return self.get(f"/v2/{symbol}/address")

    def coin_withdraw_pending(self, symbol: str) -> Dict:
        """Get pending withdrawals for a coin symbol."""
        return self.get(f"/v2/{symbol}/withdraw/pending")
