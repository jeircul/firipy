# Firi API wrapper

[![Upload Python Package](https://github.com/jeircul/firipy/actions/workflows/publish.yml/badge.svg)](https://github.com/jeircul/firipy/actions/workflows/publish.yml)
[![Run Tests](https://github.com/jeircul/firipy/actions/workflows/run_tests.yml/badge.svg)](https://github.com/jeircul/firipy/actions/workflows/run_tests.yml)
![PyPI - Version](https://img.shields.io/pypi/v/firipy)
![GitHub](https://img.shields.io/github/license/jeircul/firipy)

Python3 wrapper around the [Firi Trading API (1.0.0)](https://developers.firi.com/)<b></b>
>  I have **no** affiliation with Firi, use at your **own** risk.

## 📦 Installation
PyPI
```pip
pip install -U firipy
```

## 🚀 Usage

**API Key** from [Firi](https://platform.firi.com/) is required:
```python
from firipy import FiriAPI

fp = FiriAPI(token='YOUR_API_KEY')
print(fp.balances())
```

## 🔌 Endpoints included

> :book: [Firi Trading API (1.0.0)](https://developers.firi.com/) for more details


* **/time**

```python
# Get current timestamp in epoch
fp.time()
```

* **/v2/history/transactions?count=100000000000000000000**

```python
fp.history_transactions()
```

* **/v2/history/transactions/{year}**

```python
fp.history_transactions_year(year)
```

* **/v2/history/transactions/{month}/{year}**

```python
fp.history_transactions_month_year(month, year)
```

* **/v2/history/trades**

```python
fp.history_trades()
```

* **/v2/history/trades/{year}**

```python
fp.history_trades_year(year)
```

* **/v2/history/trades/{month}/{year}**

```python
fp.history_trades_month_year(month, year)
```

* **/v2/history/orders**

```python
fp.history_orders()
```

* **/v2/history/orders/{market}**

```python
fp.history_orders_market(market)
```

* **/v2/markets/{market}/history**

```python
fp.markets_market_history(market)
```

* **/v2/markets/{market}/depth**

```python
fp.markets_market_depth(market)
```

* **/v2/markets/{market}**

```python
fp.markets_market(market)
```

* **/v2/markets**

```python
fp.markets()
```

* **/v2/markets/{market}/ticker**

```python
fp.markets_market_ticker(market)
```

* **/v2/markets/tickers**

```python
fp.markets_tickers()
```

* **/v2/XRP/withdraw/pending**

```python
fp.xrp_withdraw_pending()
```

* **/v2/XRP/address**

```python
fp.xrp_withdraw_address()
```

* **/v2/LTC/withdraw/pending**

```python
fp.ltc_withdraw_pending()
```

* **/v2/LTC/address**

```python
fp.ltc_withdraw_address()
```

* **/v2/ETH/withdraw/pending**

```python
fp.eth_withdraw_pending()
```

* **/v2/ETH/address**

```python
fp.eth_Address()
```

* **/v2/DAI/withdraw/pending**

```python
fp.dai_withdraw_pending()
```

* **/v2/DAI/address**

```python
fp.dai_Address()
```

* **/v2/DOT/address**

```python
fp.dot_Address()
```

* **/v2/DOT/withdraw/pending**

```python
fp.dot_withdraw_pending()
```

* **/v2/BTC/withdraw/pending**

```python
fp.btc_withdraw_pending()
```

* **/v2/BTC/address**

```python
fp.btc_Address()
```

* **/v2/ADA/withdraw/pending**

```python
fp.ada_withdraw_pending()
```

* **/v2/ADA/address**

```python
fp.ada_Address()
```

* **/v2/deposit/history?count=1000000**

```python
fp.deposit_history()
```

* **/v2/deposit/address**

```python
fp.deposit_address()
```

* **/v2/orders**

```python
fp.orders()
```

* **/v2/orders/{market}**

```python
fp.orders_market(market)
```

* **/v2/orders/{market}/history**

```python
fp.orders_market_history(market)
```

* **/v2/orders/history**

```python
fp.orders_history()
```

* **/v2/order/{orderID}**

```python
fp.order_orderid(orderID)
```

* **/v2/balances**

```python
fp.balances()
```

* **/v2/orders**

```python
fp.delete_orders()
```

* **/v2/orders/{orderID}/{market}/detailed**

```python
fp.delete_oders_orderid_market_detailed(orderID, market)
```

* **/v2/orders/{orderID}/detailed**

```python
fp.delete_oders_orderid_detailed(orderID)
```

* **/v2/orders/{marketOrMarketID}**

```python
fp.delete_orders_marketormarketsid(marketOrMarketID)
```
