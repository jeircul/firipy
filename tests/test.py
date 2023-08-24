import os
import unittest
from firipy import FiriAPI

token = os.environ['API_KEY_FIRI']


class TestFiriAPI(unittest.TestCase):
    def test_get_time(self):
        fg = FiriAPI(token)
        time = fg.time()
        self.assertIsNotNone(time)
        self.assertIsInstance(time, dict)

    def test_history_transactions(self):
        fg = FiriAPI(token)
        transactions = fg.history_transactions()
        self.assertIsNotNone(transactions)
        self.assertIsInstance(transactions, list)
        self.assertGreater(len(transactions), 0)

    def test_history_transactions_year(self):
        fg = FiriAPI(token)
        transactions = fg.history_transactions_year(2023)
        self.assertIsNotNone(transactions)
        self.assertIsInstance(transactions, list)
        self.assertGreater(len(transactions), 0)

    def test_history_transactions_month_year(self):
        fg = FiriAPI(token)
        transactions = fg.history_transactions_month_year(6, 2023)
        self.assertIsNotNone(transactions)
        self.assertIsInstance(transactions, list)
        self.assertGreater(len(transactions), 0)

if __name__ == '__main__':
    unittest.main()
