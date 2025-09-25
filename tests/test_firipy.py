import os
import unittest
import warnings
from unittest.mock import patch
from firipy import FiriAPI

token = os.environ.get('API_KEY_FIRI', 'dummy-token')

class TestFiriAPI(unittest.TestCase):
    @patch('firipy.FiriAPI._request')
    def test_get_time(self, mock_request):
        # Setup
        mock_request.return_value = {"serverTime": "2022-01-01T00:00:00Z"}
        fp = FiriAPI(token)

        # Exercise
        time = fp.time()

        # Verify
        self.assertEqual(time, {"serverTime": "2022-01-01T00:00:00Z"})
        mock_request.assert_called_once_with("GET", "/time")

    @patch('firipy.FiriAPI._request')
    def test_history_transactions(self, mock_request):
        # Setup
        mock_request.return_value = [{"id": "1", "amount": "0.1"}]
        fp = FiriAPI(token)

        # Exercise
        transactions = fp.history_transactions()

        # Verify
        self.assertEqual(transactions, [{"id": "1", "amount": "0.1"}])
        mock_request.assert_called_once_with("GET", "/v2/history/transactions", params={"count": 500})

    @patch('firipy.FiriAPI._request')
    def test_history_transactions_year(self, mock_request):
        # Setup
        mock_request.return_value = [{"id": "1", "amount": "0.1"}]
        fp = FiriAPI(token)

        # Exercise
        transactions = fp.history_transactions_year("2023")

        # Verify
        self.assertEqual(transactions, [{"id": "1", "amount": "0.1"}])
        mock_request.assert_called_once_with("GET", "/v2/history/transactions/2023", params=None)

    @patch('firipy.FiriAPI._request')
    def test_history_transactions_month_year(self, mock_request):
        # Setup
        mock_request.return_value = [{"id": "1", "amount": "0.1"}]
        fp = FiriAPI(token)

        # Exercise
        transactions = fp.history_transactions_month_year("6", "2023")

        # Verify
        self.assertEqual(transactions, [{"id": "1", "amount": "0.1"}])
        mock_request.assert_called_once_with("GET", "/v2/history/transactions/6/2023", params=None)

    @patch('firipy.FiriAPI._request')
    def test_deprecated_eth_Address(self, mock_request):
        mock_request.return_value = {"address": "0xabc"}
        fp = FiriAPI(token)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            addr = fp.eth_Address()
            self.assertEqual(addr, {"address": "0xabc"})
            self.assertTrue(any(issubclass(wi.category, DeprecationWarning) for wi in w))
        mock_request.assert_called_once_with("GET", "/v2/ETH/address")

    @patch('firipy.FiriAPI._request')
    def test_post_orders(self, mock_request):
        mock_request.return_value = {"orderId": "123", "status": "placed"}
        fp = FiriAPI(token)
        result = fp.post_orders("BTCNOK", "limit", "500000", "0.01")
        self.assertEqual(result["orderId"], "123")
        mock_request.assert_called_once()

    @patch('firipy.FiriAPI._request')
    def test_history_transactions_with_params(self, mock_request):
        mock_request.return_value = []
        fp = FiriAPI(token)
        fp.history_transactions(count=250, direction='start')
        mock_request.assert_called_once_with("GET", "/v2/history/transactions", params={'count': 250, 'direction': 'start'})

    @patch('firipy.FiriAPI._request')
    def test_markets_market_depth_with_params(self, mock_request):
        mock_request.return_value = {"bids": [], "asks": []}
        fp = FiriAPI(token)
        fp.markets_market_depth('BTCNOK', bids=5, asks=10)
        mock_request.assert_called_once_with("GET", "/v2/markets/BTCNOK/depth", params={'bids': 5, 'asks': 10})

    @patch('firipy.FiriAPI._request')
    def test_deposit_history_before(self, mock_request):
        mock_request.return_value = {"transactions": []}
        fp = FiriAPI(token)
        fp.deposit_history(count=100, before=123456)
        mock_request.assert_called_once_with("GET", "/v2/deposit/history", params={'count': 100, 'before': 123456})

    @patch('firipy.FiriAPI._request')
    def test_orders_market_count(self, mock_request):
        mock_request.return_value = []
        fp = FiriAPI(token)
        fp.orders_market('BTCNOK', count=50)
        mock_request.assert_called_once_with("GET", "/v2/orders/BTCNOK", params={'count': 50})

    @patch('firipy.FiriAPI._request')
    def test_coin_generic_helpers(self, mock_request):
        mock_request.return_value = {"address": "xyz"}
        fp = FiriAPI(token)
        fp.coin_address('BTC')
        mock_request.assert_called_once_with("GET", "/v2/BTC/address")

    @patch('firipy.FiriAPI._request')
    def test_deprecated_history_trades(self, mock_request):
        mock_request.return_value = []
        fp = FiriAPI(token)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            fp.history_trades()
            self.assertTrue(any(issubclass(wi.category, DeprecationWarning) for wi in w))
        mock_request.assert_called_once_with("GET", "/v2/history/trades")

    @patch('firipy.FiriAPI._request')
    def test_deprecated_delete_orders_orderid_detailed(self, mock_request):
        mock_request.return_value = {"matched": "0.0"}
        fp = FiriAPI(token)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            fp.delete_orders_orderid_detailed('123')
            self.assertTrue(any(issubclass(wi.category, DeprecationWarning) for wi in w))
        mock_request.assert_called_once_with("DELETE", "/v2/orders/123/detailed")

    @patch('firipy.FiriAPI._request')
    def test_new_delete_order_detailed_market(self, mock_request):
        mock_request.return_value = {"matched": "0.0"}
        fp = FiriAPI(token)
        fp.delete_order_detailed('345', market='BTCNOK')
        mock_request.assert_called_once_with("DELETE", "/v2/orders/345/BTCNOK/detailed")

    def test_raise_on_error_false_returns_error_dict(self):
        # simulate by patching session.request at lower level could be more complex; patch _request for shape
        with patch('firipy.FiriAPI._request', return_value={"error": "Bad Request", "status": 400}):
            fp = FiriAPI(token, raise_on_error=False)
            data = fp.get('/v2/markets')
            self.assertIn('error', data)
            self.assertEqual(data['status'], 400)

    def test_context_manager(self):
        fp = FiriAPI(token)
        with patch.object(fp.session, 'close') as mock_close:
            with fp:
                pass
            mock_close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
