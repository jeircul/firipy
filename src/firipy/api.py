"""Async Firi API client built on ``httpx.AsyncClient``."""

import logging
import warnings
from asyncio import sleep
from collections.abc import Iterable
from typing import Any

import httpx

__all__ = ["FiriAPI", "FiriAPIError", "FiriHTTPError"]

log = logging.getLogger(__name__)

type JSON = dict[str, Any] | list[Any]


class FiriAPIError(Exception):
    """Base exception for all Firi API client errors."""


class FiriHTTPError(FiriAPIError):
    """Raised when ``raise_on_error`` handles non-success HTTP responses.

    Attributes:
        status_code: HTTP status code from the failed response.
        payload: Parsed JSON body from the error response, if available.
    """

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
    """Async client for the Firi cryptocurrency exchange API.

    Args:
        api_key: Your Firi API key (sent as the ``miraiex-access-key`` header).
            Generate one at https://platform.firi.com/ under account settings.
        rate_limit: Seconds to sleep before each request. Set to ``0`` to
            disable client-side pacing.
        base_url: Base URL for the API (override for testing/mocking).
        timeout: Per-request timeout in seconds.
        raise_on_error: If ``True``, non-2xx responses raise
            :class:`FiriHTTPError`. If ``False``, returns a dict with keys
            ``{"error": str, "status": int}``.
        client: Optional pre-configured ``httpx.AsyncClient`` to use instead
            of creating a new one.
    """

    DEFAULT_COUNT: int = 500
    MAX_COUNT: int = 10_000

    def __init__(
        self,
        api_key: str,
        *,
        rate_limit: float = 1.0,
        base_url: str = "https://api.firi.com",
        timeout: float = 10.0,
        raise_on_error: bool = True,
        client: httpx.AsyncClient | None = None,
    ):
        self.apiurl = base_url.rstrip("/")
        # Track ownership so we only close clients we created ourselves.
        self._owns_client = client is None
        if client is None:
            self.client = httpx.AsyncClient(
                headers={"miraiex-access-key": api_key},
                timeout=timeout,
            )
        else:
            # Caller owns this client and is responsible for auth headers.
            # Fail fast if the required auth header is absent rather than
            # letting requests silently return 401s at call time.
            if "miraiex-access-key" not in client.headers:
                raise ValueError(
                    "Injected client is missing the 'miraiex-access-key' header. "
                    "Set it before passing the client to FiriAPI, or omit 'client' "
                    "and pass 'api_key' to let FiriAPI create its own client."
                )
            self.client = client
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.raise_on_error = raise_on_error

    # --- Context manager helpers -------------------------------------------

    async def __aenter__(self) -> "FiriAPI":
        """Enter async context by returning the current client."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> None:
        """Exit async context by closing the underlying HTTP client."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying httpx client.

        No-op when the client was supplied by the caller — ownership stays
        with the caller in that case.
        """
        if self._owns_client:
            await self.client.aclose()

    # --- Representation ----------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return (
            "FiriAPI("
            f"base_url='{self.apiurl}', "
            f"rate_limit={self.rate_limit}, "
            f"timeout={self.timeout}, "
            f"raise_on_error={self.raise_on_error}, api_key='***')"
        )

    # --- Core HTTP ---------------------------------------------------------

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> JSON:
        """Send an HTTP request and return parsed JSON.

        Returns:
            Parsed JSON body. If ``raise_on_error`` is ``False`` and an HTTP
            error occurs, a dict with keys ``error`` and ``status`` is
            returned instead.
        """
        if self.rate_limit > 0:
            await sleep(self.rate_limit)
        url = self.apiurl + endpoint
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
        except httpx.HTTPStatusError as http_err:
            status_code = http_err.response.status_code
            payload: Any | None = None
            try:
                payload = http_err.response.json()
            except Exception:  # pragma: no cover
                payload = None
            message = None
            if isinstance(payload, dict):
                message = payload.get("message") or payload.get("error")
            if not message:
                message = str(http_err)
            if self.raise_on_error:
                raise FiriHTTPError(status_code, message, payload) from http_err
            log.warning(
                "HTTP error (%s) for %s %s: %s",
                status_code,
                method,
                url,
                message,
            )
            return {"error": message, "status": status_code}
        except httpx.HTTPError as err:
            if self.raise_on_error:
                raise FiriAPIError(str(err)) from err
            log.error("Request error for %s %s: %s", method, url, err)
            return {"error": str(err), "status": None}
        else:
            try:
                return response.json()
            except ValueError:  # pragma: no cover
                return {
                    "error": "Invalid JSON in response",
                    "status": response.status_code,
                }

    async def get(self, endpoint: str, **kwargs: Any) -> JSON:
        """Send a GET request to the given endpoint."""
        return await self._request("GET", endpoint, **kwargs)

    async def delete(self, endpoint: str) -> JSON:
        """Send a DELETE request to the given endpoint."""
        return await self._request("DELETE", endpoint)

    async def post(self, endpoint: str, data: dict[str, Any] | None = None) -> JSON:
        """Send a POST request to the given endpoint."""
        return await self._request("POST", endpoint, json=data)

    # --- Internal helpers --------------------------------------------------

    def _validate_choice(
        self, name: str, value: str | None, choices: Iterable[str]
    ) -> str | None:
        if value is None:
            return None
        ordered_choices = sorted(choices)
        if value not in ordered_choices:
            raise ValueError(f"{name} must be one of {ordered_choices} (got {value!r})")
        return value

    def _validate_int(
        self,
        name: str,
        value: int | None,
        *,
        minimum: int = 1,
        maximum: int | None = None,
    ) -> int | None:
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

    # --- Time --------------------------------------------------------------

    async def time(self) -> JSON:
        """Get the current server time from the Firi API."""
        return await self.get("/time")

    # --- History -----------------------------------------------------------

    async def history_transactions(
        self, *, count: int | None = None, direction: str | None = None
    ) -> JSON:
        """Get history over all transactions.

        Args:
            count: Number of records to request. Defaults to
                ``DEFAULT_COUNT`` when omitted.
            direction: Pagination direction (``"start"`` or ``"end"``).
        """
        params: dict[str, Any] = {}
        count = self._validate_int(
            "count", count or self.DEFAULT_COUNT, maximum=self.MAX_COUNT
        )
        params["count"] = count
        validated_direction = self._validate_choice(
            "direction", direction, {"start", "end"}
        )
        if validated_direction is not None:
            params["direction"] = validated_direction
        return await self.get("/v2/history/transactions", params=params)

    async def history_transactions_year(
        self, year: str, *, direction: str | None = None
    ) -> JSON:
        """Get transaction history filtered by year.

        Args:
            year: The year to filter by (e.g. ``"2024"``).
            direction: Pagination direction (``"start"`` or ``"end"``).
        """
        params: dict[str, Any] = {}
        validated_direction = self._validate_choice(
            "direction", direction, {"start", "end"}
        )
        if validated_direction is not None:
            params["direction"] = validated_direction
        return await self.get(f"/v2/history/transactions/{year}", params=params or None)

    async def history_transactions_month_year(
        self, month: str, year: str, *, direction: str | None = None
    ) -> JSON:
        """Get transaction history filtered by month and year.

        Args:
            month: The month to filter by (e.g. ``"6"``).
            year: The year to filter by (e.g. ``"2024"``).
            direction: Pagination direction (``"start"`` or ``"end"``).
        """
        params: dict[str, Any] = {}
        validated_direction = self._validate_choice(
            "direction", direction, {"start", "end"}
        )
        if validated_direction is not None:
            params["direction"] = validated_direction
        return await self.get(
            f"/v2/history/transactions/{month}/{year}", params=params or None
        )

    async def history_orders(
        self,
        *,
        type: str | None = None,  # noqa: A002
        count: int | None = None,
    ) -> JSON:
        """Get history over all orders.

        Args:
            type: Order type filter as documented by the API.
            count: Number of records (defaults to ``DEFAULT_COUNT``).
        """
        params: dict[str, Any] = {}
        count = self._validate_int(
            "count", count or self.DEFAULT_COUNT, maximum=self.MAX_COUNT
        )
        params["count"] = count
        if type is not None:
            params["type"] = type
        return await self.get("/v2/history/orders", params=params)

    async def history_orders_market(
        self,
        market: str,
        *,
        type: str | None = None,  # noqa: A002
        count: int | None = None,
    ) -> JSON:
        """Get order history for a specific market.

        Args:
            market: Market identifier (e.g. ``"BTCNOK"``).
            type: Order type filter.
            count: Number of records (defaults to ``DEFAULT_COUNT``).
        """
        params: dict[str, Any] = {}
        count = self._validate_int(
            "count", count or self.DEFAULT_COUNT, maximum=self.MAX_COUNT
        )
        params["count"] = count
        if type is not None:
            params["type"] = type
        return await self.get(f"/v2/history/orders/{market}", params=params)

    # --- Markets -----------------------------------------------------------

    async def markets_market_history(
        self, market: str, *, count: int | None = None
    ) -> JSON:
        """Get trade history for a specific market.

        Args:
            market: Market identifier (e.g. ``"BTCNOK"``).
            count: Number of records to return.
        """
        params: dict[str, Any] = {}
        if count is not None:
            count = self._validate_int("count", count, maximum=self.MAX_COUNT)
            params["count"] = count
        return await self.get(f"/v2/markets/{market}/history", params=params or None)

    async def markets_market_depth(
        self,
        market: str,
        *,
        bids: int | None = None,
        asks: int | None = None,
    ) -> JSON:
        """Get the order book for a market.

        Args:
            market: Market identifier (e.g. ``"BTCNOK"``).
            bids: Maximum number of bid entries to return.
            asks: Maximum number of ask entries to return.
        """
        params: dict[str, Any] = {}
        if bids is not None:
            params["bids"] = self._validate_int("bids", bids)
        if asks is not None:
            params["asks"] = self._validate_int("asks", asks)
        return await self.get(f"/v2/markets/{market}/depth", params=params or None)

    async def markets_market(self, market: str) -> JSON:
        """Get info about a specific market.

        Args:
            market: Market identifier (e.g. ``"BTCNOK"``).
        """
        return await self.get(f"/v2/markets/{market}")

    async def markets(self) -> JSON:
        """Get all available markets."""
        return await self.get("/v2/markets")

    async def markets_market_ticker(self, market: str) -> JSON:
        """Get ticker for a specific market.

        Args:
            market: Market identifier (e.g. ``"BTCNOK"``).
        """
        return await self.get(f"/v2/markets/{market}/ticker")

    async def markets_tickers(self) -> JSON:
        """Get tickers for all available markets."""
        return await self.get("/v2/markets/tickers")

    # --- Per-coin convenience methods --------------------------------------
    # All methods below are deprecated. stacklevel=2 points the warning at
    # the direct caller of the deprecated method. If any of these are ever
    # called internally (from another method on this class), stacklevel must
    # be incremented accordingly — none are called internally today.

    async def xrp_withdraw_pending(self) -> JSON:
        """Get pending XRP withdrawals.

        .. deprecated::
            Use ``coin_withdraw_pending("XRP")`` instead.
        """
        warnings.warn(
            "xrp_withdraw_pending() is deprecated; "
            "use coin_withdraw_pending('XRP') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_withdraw_pending("XRP")

    async def xrp_withdraw_address(self) -> JSON:
        """Get the user's XRP deposit address.

        .. deprecated::
            Use ``coin_address("XRP")`` instead.
        """
        warnings.warn(
            "xrp_withdraw_address() is deprecated; use coin_address('XRP') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_address("XRP")

    async def ltc_withdraw_pending(self) -> JSON:
        """Get pending LTC withdrawals.

        .. deprecated::
            Use ``coin_withdraw_pending("LTC")`` instead.
        """
        warnings.warn(
            "ltc_withdraw_pending() is deprecated; "
            "use coin_withdraw_pending('LTC') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_withdraw_pending("LTC")

    async def ltc_withdraw_address(self) -> JSON:
        """Get the user's LTC deposit address.

        .. deprecated::
            Use ``coin_address("LTC")`` instead.
        """
        warnings.warn(
            "ltc_withdraw_address() is deprecated; use coin_address('LTC') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_address("LTC")

    async def eth_withdraw_pending(self) -> JSON:
        """Get pending ETH withdrawals.

        .. deprecated::
            Use ``coin_withdraw_pending("ETH")`` instead.
        """
        warnings.warn(
            "eth_withdraw_pending() is deprecated; "
            "use coin_withdraw_pending('ETH') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_withdraw_pending("ETH")

    async def eth_address(self) -> JSON:
        """Get the user's ETH deposit address.

        .. deprecated::
            Use ``coin_address("ETH")`` instead.
        """
        warnings.warn(
            "eth_address() is deprecated; use coin_address('ETH') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_address("ETH")

    async def dai_withdraw_pending(self) -> JSON:
        """Get pending DAI withdrawals.

        .. deprecated::
            Use ``coin_withdraw_pending("DAI")`` instead.
        """
        warnings.warn(
            "dai_withdraw_pending() is deprecated; "
            "use coin_withdraw_pending('DAI') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_withdraw_pending("DAI")

    async def dai_address(self) -> JSON:
        """Get the user's DAI deposit address.

        .. deprecated::
            Use ``coin_address("DAI")`` instead.
        """
        warnings.warn(
            "dai_address() is deprecated; use coin_address('DAI') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_address("DAI")

    async def dot_address(self) -> JSON:
        """Get the user's DOT deposit address.

        .. deprecated::
            Use ``coin_address("DOT")`` instead.
        """
        warnings.warn(
            "dot_address() is deprecated; use coin_address('DOT') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_address("DOT")

    async def dot_withdraw_pending(self) -> JSON:
        """Get pending DOT withdrawals.

        .. deprecated::
            Use ``coin_withdraw_pending("DOT")`` instead.
        """
        warnings.warn(
            "dot_withdraw_pending() is deprecated; "
            "use coin_withdraw_pending('DOT') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_withdraw_pending("DOT")

    async def btc_withdraw_pending(self) -> JSON:
        """Get pending BTC withdrawals.

        .. deprecated::
            Use ``coin_withdraw_pending("BTC")`` instead.
        """
        warnings.warn(
            "btc_withdraw_pending() is deprecated; "
            "use coin_withdraw_pending('BTC') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_withdraw_pending("BTC")

    async def btc_address(self) -> JSON:
        """Get the user's BTC deposit address.

        .. deprecated::
            Use ``coin_address("BTC")`` instead.
        """
        warnings.warn(
            "btc_address() is deprecated; use coin_address('BTC') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_address("BTC")

    async def ada_withdraw_pending(self) -> JSON:
        """Get pending ADA withdrawals.

        .. deprecated::
            Use ``coin_withdraw_pending("ADA")`` instead.
        """
        warnings.warn(
            "ada_withdraw_pending() is deprecated; "
            "use coin_withdraw_pending('ADA') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_withdraw_pending("ADA")

    async def ada_address(self) -> JSON:
        """Get the user's ADA deposit address.

        .. deprecated::
            Use ``coin_address("ADA")`` instead.
        """
        warnings.warn(
            "ada_address() is deprecated; use coin_address('ADA') instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.coin_address("ADA")

    # --- Deposits ----------------------------------------------------------

    async def deposit_history(
        self, *, count: int | None = None, before: int | None = None
    ) -> JSON:
        """Get deposit history for the authenticated user.

        Args:
            count: Number of records (defaults to ``DEFAULT_COUNT``).
            before: Fetch deposits before this cursor/timestamp.
        """
        params: dict[str, Any] = {}
        count = self._validate_int(
            "count", count or self.DEFAULT_COUNT, maximum=self.MAX_COUNT
        )
        params["count"] = count
        if before is not None:
            params["before"] = before
        return await self.get("/v2/deposit/history", params=params)

    async def deposit_address(self) -> JSON:
        """Get the user's multi-coin deposit address."""
        return await self.get("/v2/deposit/address")

    # --- Orders ------------------------------------------------------------

    async def orders(self) -> JSON:
        """Get all active orders."""
        return await self.get("/v2/orders")

    async def orders_market(self, market: str, *, count: int | None = None) -> JSON:
        """Get active orders for a specific market.

        Args:
            market: Market identifier (e.g. ``"BTCNOK"``).
            count: Maximum number of orders to return.
        """
        params: dict[str, Any] = {}
        if count is not None:
            params["count"] = self._validate_int("count", count, maximum=self.MAX_COUNT)
        return await self.get(f"/v2/orders/{market}", params=params or None)

    async def orders_market_history(
        self, market: str, *, count: int | None = None
    ) -> JSON:
        """Get filled and closed orders for a specific market.

        Args:
            market: Market identifier (e.g. ``"BTCNOK"``).
            count: Maximum number of orders to return.
        """
        params: dict[str, Any] = {}
        if count is not None:
            params["count"] = self._validate_int("count", count, maximum=self.MAX_COUNT)
        return await self.get(f"/v2/orders/{market}/history", params=params or None)

    async def orders_history(self, *, count: int | None = None) -> JSON:
        """Get all filled and closed orders.

        Args:
            count: Maximum number of orders to return.
        """
        params: dict[str, Any] = {}
        if count is not None:
            params["count"] = self._validate_int("count", count, maximum=self.MAX_COUNT)
        return await self.get("/v2/orders/history", params=params or None)

    async def order_orderid(self, order_id: str) -> JSON:
        """Get an order by its ID.

        Args:
            order_id: The order identifier.
        """
        return await self.get(f"/v2/order/{order_id}")

    async def order(self, order_id: str) -> JSON:
        """Get an order by its ID (concise alias for :meth:`order_orderid`).

        Args:
            order_id: The order identifier.
        """
        return await self.order_orderid(order_id)

    async def delete_orders(self) -> JSON:
        """Cancel all active orders."""
        return await self.delete("/v2/orders")

    async def delete_orders_for_market(self, market_or_market_id: str) -> JSON:
        """Cancel all active orders for a market.

        Args:
            market_or_market_id: Market identifier or ID.
        """
        return await self.delete(f"/v2/orders/{market_or_market_id}")

    async def delete_order_detailed(
        self, order_id: str, *, market: str | None = None
    ) -> JSON:
        """Cancel an order and return the matched amount if supported.

        Args:
            order_id: ID of the order to cancel.
            market: If provided, uses the market-specific detailed endpoint.
        """
        if market:
            return await self.delete(f"/v2/orders/{order_id}/{market}/detailed")
        return await self.delete(f"/v2/orders/{order_id}/detailed")

    # --- Balances ----------------------------------------------------------

    async def balances(self) -> JSON:
        """Get wallet balances for the authenticated user."""
        return await self.get("/v2/balances")

    # --- Post orders -------------------------------------------------------

    async def post_orders(
        self, market: str, ordertype: str, price: str, amount: str
    ) -> JSON:
        """Place a new order.

        Args:
            market: Market identifier (e.g. ``"BTCNOK"``).
            ordertype: Order type (e.g. ``"bid"`` or ``"ask"``).
            price: Order price as a string.
            amount: Order amount as a string.
        """
        data = {
            "market": market,
            "type": ordertype,
            "price": price,
            "amount": amount,
        }
        return await self.post("/v2/orders", data=data)

    # --- Generic coin helpers ----------------------------------------------

    async def coin_address(self, symbol: str) -> JSON:
        """Get the deposit address for a coin.

        Args:
            symbol: Upper-case asset symbol (e.g. ``"BTC"``, ``"ETH"``).
        """
        return await self.get(f"/v2/{symbol}/address")

    async def coin_withdraw_pending(self, symbol: str) -> JSON:
        """Get pending withdrawals for a coin.

        Args:
            symbol: Upper-case asset symbol (e.g. ``"BTC"``, ``"ETH"``).
        """
        return await self.get(f"/v2/{symbol}/withdraw/pending")
