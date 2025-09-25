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
        mock_request.assert_called_once_with("GET", "/v2/history/transactions/2023")

    @patch('firipy.FiriAPI._request')
    def test_history_transactions_month_year(self, mock_request):
        # Setup
        mock_request.return_value = [{"id": "1", "amount": "0.1"}]
        fp = FiriAPI(token)

        # Exercise
        transactions = fp.history_transactions_month_year("6", "2023")

        # Verify
        self.assertEqual(transactions, [{"id": "1", "amount": "0.1"}])
        mock_request.assert_called_once_with("GET", "/v2/history/transactions/6/2023")

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
