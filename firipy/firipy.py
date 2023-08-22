from requests import Session


class Firi:
    # https://developers.firi.com/
    def __init__(self, token):
        headers = {"miraiex-access-key": token}
        self.apiurl = "https://api.firi.com"
        self.session = Session()
        self.session.headers.update(headers)

    def get(self, endpoint):
        url = self.apiurl + endpoint
        r = self.session.get(url, timeout=30)
        r.raise_for_status()
        return r.json()

    def delete(self, endpoint):
        url = self.apiurl + endpoint
        r = self.session.delete(url)
        r.raise_for_status()
        return r.json()

    def post_orders(self, market, ordertype, price, amount):
        param = {
            "market": market,
            "type": ordertype,
            "price": price,
            "amount": amount
        }
        url = self.apiurl + "/v2/orders"
        r = self.session.post(url, params=param)
        r.raise_for_status()
        return r.json()

    def time(self):
        return self.get("/time")

    def history_transactions(self):
        return self.get("/v2/history/transactions?count=100000000000000000000")

    def history_transactions_year(self, year):
        return self.get(f"/v2/history/transactions/{year}")

    def history_transactions_month_year(self, month, year):
        return self.get(f"/v2/history/transactions/{month}/{year}")

    def history_trades(self):
        return self.get("/v2/history/trades")

    def history_trades_year(self, year):
        return self.get(f"/v2/history/trades/{year}")

    def history_trades_month_year(self, month, year):
        return self.get(f"/v2/history/trades/{month}/{year}")

    def history_orders(self):
        return self.get("/v2/history/orders")

    def history_orders_market(self, market):
        return self.get(f"/v2/history/orders/{market}")

    def markets_market_history(self, market):
        return self.get(f"/v2/markets/{market}/history")

    def markets_market_depth(self, market):
        return self.get(f"/v2/markets/{market}/depth")

    def markets_market(self, market):
        return self.get(f"/v2/markets/{market}")

    def markets(self):
        return self.get("/v2/markets")

    def markets_market_ticker(self, market):
        return self.get(f"/v2/markets/{market}/ticker")

    def markets_tickers(self):
        return self.get("/v2/markets/tickers")

    def xrp_withdraw_pending(self):
        return self.get("/v2/XRP/withdraw/pending")

    def xrp_withdraw_address(self):
        return self.get("/v2/XRP/address")

    def ltc_withdraw_pending(self):
        return self.get("/v2/LTC/withdraw/pending")

    def ltc_withdraw_address(self):
        return self.get("/v2/LTC/address")

    def eth_withdraw_pending(self):
        return self.get("/v2/ETH/withdraw/pending")

    def eth_Address(self):
        return self.get("/v2/ETH/address")

    def dai_withdraw_pending(self):
        return self.get("/v2/DAI/withdraw/pending")

    def dai_Address(self):
        return self.get("/v2/DAI/address")

    def dot_Address(self):
        return self.get("/v2/DOT/address")

    def dot_withdraw_pending(self):
        return self.get("/v2/DOT/withdraw/pending")

    def btc_withdraw_pending(self):
        return self.get("/v2/BTC/withdraw/pending")

    def btc_Address(self):
        return self.get("/v2/BTC/address")

    def ada_withdraw_pending(self):
        return self.get("/v2/ADA/withdraw/pending")

    def ada_Address(self):
        return self.get("/v2/ADA/address")

    def deposit_history(self):
        return self.get("/v2/deposit/history?count=1000000")

    def deposit_address(self):
        return self.get("/v2/deposit/address")

    def orders(self):
        return self.get("/v2/orders")

    def orders_market(self, market):
        return self.get(f"/v2/orders/{market}")

    def orders_market_history(self, market):
        return self.get(f"/v2/orders/{market}/history")

    def orders_history(self):
        return self.get("/v2/orders/history")

    def order_orderid(self, orderID):
        return self.get(f"/v2/order/{orderID}")

    def balances(self):
        return self.get("/v2/balances")

    def delete_orders(self):
        return self.delete("/v2/orders")

    def delete_oders_orderid_market_detailed(self, orderID, market):
        return self.delete(f"/v2/orders/{orderID}/{market}/detailed")

    def delete_oders_orderid_detailed(self, orderID):
        return self.delete(f"/v2/orders/{orderID}/detailed")

    def delete_orders_marketormarketsid(self, marketOrMarketID):
        return self.delete(f"/v2/orders/{marketOrMarketID}")
