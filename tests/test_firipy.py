import os
import unittest
from unittest.mock import patch
from firipy import FiriAPI

token = os.environ['API_KEY_FIRI']

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
        mock_request.assert_called_once_with("GET", "/v2/history/transactions", params={"count": 100000000000000000000})

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

if __name__ == '__main__':
    unittest.main()
