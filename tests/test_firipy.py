"""Unit tests for :mod:`firipy` using ``unittest.mock`` to stub HTTP calls."""

import os
import unittest
from unittest.mock import MagicMock, patch

from firipy import FiriAPI

token: str = os.environ.get("API_KEY_FIRI", "dummy-token")


class TestFiriAPI(unittest.TestCase):
    """Validate the core client by patching the network layer."""

    @patch("firipy.FiriAPI._request")
    def test_get_time(self, mock_request: MagicMock) -> None:
        """Ensure the time endpoint response is forwarded unchanged."""
        mock_request.return_value = {"serverTime": "2022-01-01T00:00:00Z"}
        fp = FiriAPI(token)

        time_response = fp.time()

        self.assertEqual(time_response, {"serverTime": "2022-01-01T00:00:00Z"})
        mock_request.assert_called_once_with("GET", "/time")

    @patch("firipy.FiriAPI._request")
    def test_history_transactions(self, mock_request: MagicMock) -> None:
        """Verify defaults when pulling transaction history."""
        mock_request.return_value = [{"id": "1", "amount": "0.1"}]
        fp = FiriAPI(token)

        transactions = fp.history_transactions()

        self.assertEqual(transactions, [{"id": "1", "amount": "0.1"}])
        mock_request.assert_called_once_with(
            "GET",
            "/v2/history/transactions",
            params={"count": 500},
        )

    @patch("firipy.FiriAPI._request")
    def test_history_transactions_year(self, mock_request: MagicMock) -> None:
        """Ensure yearly transaction helper relays parameters correctly."""
        mock_request.return_value = [{"id": "1", "amount": "0.1"}]
        fp = FiriAPI(token)

        transactions = fp.history_transactions_year("2023")

        self.assertEqual(transactions, [{"id": "1", "amount": "0.1"}])
        mock_request.assert_called_once_with(
            "GET",
            "/v2/history/transactions/2023",
            params=None,
        )

    @patch("firipy.FiriAPI._request")
    def test_history_transactions_month_year(
        self, mock_request: MagicMock
    ) -> None:
        """Confirm month/year helper feeds path parameters as expected."""
        mock_request.return_value = [{"id": "1", "amount": "0.1"}]
        fp = FiriAPI(token)

        transactions = fp.history_transactions_month_year("6", "2023")

        self.assertEqual(transactions, [{"id": "1", "amount": "0.1"}])
        mock_request.assert_called_once_with(
            "GET",
            "/v2/history/transactions/6/2023",
            params=None,
        )

    @patch("firipy.FiriAPI._request")
    def test_post_orders(self, mock_request: MagicMock) -> None:
        """Verify payloads are forwarded when placing orders."""
        mock_request.return_value = {"orderId": "123", "status": "placed"}
        fp = FiriAPI(token)

        result = fp.post_orders("BTCNOK", "limit", "500000", "0.01")

        self.assertEqual(result["orderId"], "123")
        mock_request.assert_called_once()

    @patch("firipy.FiriAPI._request")
    def test_history_transactions_with_params(
        self, mock_request: MagicMock
    ) -> None:
        """Pass optional filters through to the request layer."""
        mock_request.return_value = []
        fp = FiriAPI(token)

        fp.history_transactions(count=250, direction="start")

        mock_request.assert_called_once_with(
            "GET",
            "/v2/history/transactions",
            params={"count": 250, "direction": "start"},
        )

    @patch("firipy.FiriAPI._request")
    def test_markets_market_depth_with_params(
        self, mock_request: MagicMock
    ) -> None:
        """Check optional depth arguments propagate to the request payload."""
        mock_request.return_value = {"bids": [], "asks": []}
        fp = FiriAPI(token)

        fp.markets_market_depth("BTCNOK", bids=5, asks=10)

        mock_request.assert_called_once_with(
            "GET",
            "/v2/markets/BTCNOK/depth",
            params={"bids": 5, "asks": 10},
        )

    @patch("firipy.FiriAPI._request")
    def test_deposit_history_before(self, mock_request: MagicMock) -> None:
        """Ensure both count and before arguments are honored for deposits."""
        mock_request.return_value = {"transactions": []}
        fp = FiriAPI(token)

        fp.deposit_history(count=100, before=123456)

        mock_request.assert_called_once_with(
            "GET",
            "/v2/deposit/history",
            params={"count": 100, "before": 123456},
        )

    @patch("firipy.FiriAPI._request")
    def test_orders_market_count(self, mock_request: MagicMock) -> None:
        """Honor the count filter when fetching orders for a market."""
        mock_request.return_value = []
        fp = FiriAPI(token)

        fp.orders_market("BTCNOK", count=50)

        mock_request.assert_called_once_with(
            "GET",
            "/v2/orders/BTCNOK",
            params={"count": 50},
        )

    @patch("firipy.FiriAPI._request")
    def test_coin_generic_helpers(self, mock_request: MagicMock) -> None:
        """Ensure the generic coin helper builds the proper endpoint."""
        mock_request.return_value = {"address": "xyz"}
        fp = FiriAPI(token)

        fp.coin_address("BTC")

        mock_request.assert_called_once_with("GET", "/v2/BTC/address")

    @patch("firipy.FiriAPI._request")
    def test_delete_order_detailed_market(
        self, mock_request: MagicMock
    ) -> None:
        """Preferred delete helper should include the market when provided."""
        mock_request.return_value = {"matched": "0.0"}
        fp = FiriAPI(token)

        fp.delete_order_detailed("345", market="BTCNOK")

        mock_request.assert_called_once_with(
            "DELETE", "/v2/orders/345/BTCNOK/detailed"
        )

    def test_raise_on_error_false_returns_error_dict(self) -> None:
        """Return an error payload when raise_on_error is disabled."""
        with patch(
            "firipy.FiriAPI._request",
            return_value={"error": "Bad Request", "status": 400},
        ):
            fp = FiriAPI(token, raise_on_error=False)
            data = fp.get("/v2/markets")
            self.assertIn("error", data)
            self.assertEqual(data["status"], 400)

    def test_context_manager(self) -> None:
        """Ensure the context manager closes the underlying session."""
        fp = FiriAPI(token)
        with patch.object(fp.session, "close") as mock_close:
            with fp:
                pass
            mock_close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
