# Firi API wrapper

[![Upload Python Package](https://github.com/jeircul/firipy/actions/workflows/publish.yml/badge.svg)](https://github.com/jeircul/firipy/actions/workflows/publish.yml)
[![Ruff](https://github.com/jeircul/firipy/actions/workflows/ruff.yml/badge.svg)](https://github.com/jeircul/firipy/actions/workflows/ruff.yml)
![PyPI - Version](https://img.shields.io/pypi/v/firipy)
![GitHub](https://img.shields.io/github/license/jeircul/firipy)

Python3 wrapper around the [Firi Trading API (1.0.0)](https://developers.firi.com/)<b></b>
> :warning: I have **no** affiliation with Firi. Use it at your **own** risk.

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

<details><summary>time</summary>
<p>

* **/time** Get current timestamp in epoch

  ```python
  fp.time()
  ```
</details>


<details><summary>history_transactions</summary>
<p>

* **/v2/history/transactions?count=100000000000000000000**

```python
fp.history_transactions()
```
</details>


<details><summary>history_transactions_year</summary>
<p>

* **/v2/history/transactions/{year}**

```python
fp.history_transactions_year(year):
```
</details>


<details><summary>history_transactions_month_year</summary>
<p>

* **/v2/history/transactions/{month}/{year}**

```python
fp.history_transactions_month_year(month, year):
```
</details>


<details><summary>history_trades</summary>
<p>

* **/v2/history/trades**

```python
fp.history_trades()
```
</details>


<details><summary>history_trades_year</summary>
<p>

* **/v2/history/trades/{year}**

```python
fp.history_trades_year(year):
```
</details>


<details><summary>history_trades_month_year</summary>
<p>

* **/v2/history/trades/{month}/{year}**

```python
fp.history_trades_month_year(month, year):
```
</details>


<details><summary>history_orders</summary>
<p>

* **/v2/history/orders**

```python
fp.history_orders()
```
</details>


<details><summary>history_orders_market</summary>
<p>

* **/v2/history/orders/{market}**

```python
fp.history_orders_market(market):
```
</details>


<details><summary>markets_market_history</summary>
<p>

* **/v2/markets/{market}/history**

```python
fp.markets_market_history(market):
```
</details>


<details><summary>markets_market_depth</summary>
<p>

* **/v2/markets/{market}/depth**

```python
fp.markets_market_depth(market):
```
</details>


<details><summary>markets_market</summary>
<p>

* **/v2/markets/{market}**

```python
fp.markets_market(market):
```
</details>


<details><summary>markets</summary>
<p>

* **/v2/markets**

```python
fp.markets()
```
</details>


<details><summary>markets_market_ticker</summary>
<p>

* **/v2/markets/{market}/ticker**

```python
fp.markets_market_ticker(market):
```
</details>


<details><summary>markets_tickers</summary>
<p>

* **/v2/markets/tickers**

```python
fp.markets_tickers()
```
</details>


<details><summary>xrp_withdraw_pending</summary>
<p>

* **/v2/XRP/withdraw/pending**

```python
fp.xrp_withdraw_pending()
```
</details>


<details><summary>xrp_withdraw_address</summary>
<p>

* **/v2/XRP/address**

```python
fp.xrp_withdraw_address()
```
</details>


<details><summary>ltc_withdraw_pending</summary>
<p>

* **/v2/LTC/withdraw/pending**

```python
fp.ltc_withdraw_pending()
```
</details>


<details><summary>ltc_withdraw_address</summary>
<p>

* **/v2/LTC/address**

```python
fp.ltc_withdraw_address()
```
</details>


<details><summary>eth_withdraw_pending</summary>
<p>

* **/v2/ETH/withdraw/pending**

```python
fp.eth_withdraw_pending()
```
</details>


<details><summary>eth_Address</summary>
<p>

* **/v2/ETH/address**

```python
fp.eth_Address()
```
</details>


<details><summary>dai_withdraw_pending</summary>
<p>

* **/v2/DAI/withdraw/pending**

```python
fp.dai_withdraw_pending()
```
</details>


<details><summary>dai_Address</summary>
<p>

* **/v2/DAI/address**

```python
fp.dai_Address()
```
</details>


<details><summary>dot_Address</summary>
<p>

* **/v2/DOT/address**

```python
fp.dot_Address()
```
</details>


<details><summary>dot_withdraw_pending</summary>
<p>

* **/v2/DOT/withdraw/pending**

```python
fp.dot_withdraw_pending()
```
</details>


<details><summary>btc_withdraw_pending</summary>
<p>

* **/v2/BTC/withdraw/pending**

```python
fp.btc_withdraw_pending()
```
</details>


<details><summary>btc_Address</summary>
<p>

* **/v2/BTC/address**

```python
fp.btc_Address()
```
</details>


<details><summary>ada_withdraw_pending</summary>
<p>

* **/v2/ADA/withdraw/pending**

```python
fp.ada_withdraw_pending()
```
</details>


<details><summary>ada_Address</summary>
<p>

* **/v2/ADA/address**

```python
fp.ada_Address()
```
</details>


<details><summary>deposit_history</summary>
<p>

* **/v2/deposit/history?count=1000000**

```python
fp.deposit_history()
```
</details>


<details><summary>deposit_address</summary>
<p>

* **/v2/deposit/address**

```python
fp.deposit_address()
```
</details>


<details><summary>orders</summary>
<p>

* **/v2/orders**

```python
fp.orders()
```
</details>


<details><summary>orders_market</summary>
<p>

* **/v2/orders/{market}**

```python
fp.orders_market(market):
```
</details>


<details><summary>orders_market_history</summary>
<p>

* **/v2/orders/{market}/history**

```python
fp.orders_market_history(market):
```
</details>


<details><summary>orders_history</summary>
<p>

* **/v2/orders/history**

```python
fp.orders_history()
```
</details>


<details><summary>order_orderid</summary>
<p>

* **/v2/order/{orderID}**

```python
fp.order_orderid(orderID):
```
</details>


<details><summary>balances</summary>
<p>

* **/v2/balances**

```python
fp.balances()
```
</details>


<details><summary>delete_orders</summary>
<p>

* **/v2/orders**

```python
fp.delete_orders()
```
</details>


<details><summary>delete_oders_orderid_market_detailed</summary>
<p>

* **/v2/orders/{orderID}/{market}/detailed**

```python
fp.delete_oders_orderid_market_detailed(orderID, market):
```
</details>


<details><summary>delete_oders_orderid_detailed</summary>
<p>

* **/v2/orders/{orderID}/detailed**

```python
fp.delete_oders_orderid_detailed(orderID):
```
</details>

<details><summary>delete_orders_marketormarketsid</summary>
<p>

* **/v2/orders/{marketOrMarketID}**

```python
fp.delete_orders_marketormarketsid(marketOrMarketID):
```
</details>
