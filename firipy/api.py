from typing import Dict, Optional
from requests import Session, Response
from time import sleep
from requests.exceptions import HTTPError

class FiriAPI:
    """Client for the Firi API."""

    def __init__(self, token: str, rate_limit: int = 1):
        """Initialize the client with the given token and rate limit."""
        headers = {"miraiex-access-key": token}
        self.apiurl = "https://api.firi.com"
        self.session = Session()
        self.session.headers.update(headers)
        self.rate_limit = rate_limit

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Send a request to the given endpoint and return the response as JSON."""
        sleep(self.rate_limit)  # simple rate limiting
        url = self.apiurl + endpoint
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            return response.json()

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

    def history_transactions(self, count: int = 100000000000000000000) -> Dict:
        """Get history over all transactions."""
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

    def eth_Address(self) -> Dict:
        """Get a user's ETH address."""
        return self.get("/v2/ETH/address")

    def dai_withdraw_pending(self) -> Dict:
        """Get a user's pending DAI withdraws."""
        return self.get("/v2/DAI/withdraw/pending")

    def dai_Address(self) -> Dict:
        """Get a user's DAI address."""
        return self.get("/v2/DAI/address")

    def dot_Address(self) -> Dict:
        """Get a user's DOT address."""
        return self.get("/v2/DOT/address")

    def dot_withdraw_pending(self) -> Dict:
        """Get a user's pending DOT withdraws."""
        return self.get("/v2/DOT/withdraw/pending")

    def btc_withdraw_pending(self) -> Dict:
        """Get a user's pending BTC withdraws."""
        return self.get("/v2/BTC/withdraw/pending")

    def btc_Address(self) -> Dict:
        """Get a user's BTC address."""
        return self.get("/v2/BTC/address")

    def ada_withdraw_pending(self) -> Dict:
        """Get a user's pending ADA withdraws."""
        return self.get("/v2/ADA/withdraw/pending")

    def ada_Address(self) -> Dict:
        """Get a user's ADA address."""
        return self.get("/v2/ADA/address")

    def deposit_history(self, count: int = 1000000) -> Dict:
        """Get a user's history over deposits."""
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
        """Delete your orders by market."""
        return self.delete(f"/v2/orders/{marketOrMarketID}")

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
