# FiriAPI

FiriAPI is a Python client for the Firi API.

## Installation

You can install FiriAPI using pip:

```bash
pip install firipy
```

## Usage

First, import the `FiriAPI` class from the `firipy` module:

```python
from firipy import FiriAPI
```

Then, initialize the client with your API token:

```python
client = FiriAPI("your-token")
```

Now you can use the client to interact with the Firi API. For example, to get the current time:

```python
time = client.time()
print(time)
```

To get history over all transactions:

```python
history = client.history_transactions()
print(history)
```

To create an order:

```python
order = client.post_orders("market", "type", "price", "amount")
print(order)
```

To get balances:

```python
balances = client.balances()
print(balances)
```

## Rate Limiting

FiriAPI includes a rate limit, which is the number of seconds to wait between requests. By default, this is set to 1 second. You can change this when you initialize the client:

```python
client = FiriAPI("your-token", rate_limit=2)  # wait 2 seconds between requests
```

## Error Handling

FiriAPI handles HTTP errors using the `requests.Response.raise_for_status` method. If a request fails, this method raises a `requests.HTTPError` exception. The client catches this exception and prints an error message.

The client also handles other exceptions that might occur during the execution of a request, and prints an error message in these cases.

## Contributing

Contributions to FiriAPI are welcome! Please submit a pull request or create an issue on the [GitHub page](https://github.com/jeircul/firipy).

## Disclaimer

This client was developed by Ove Aursland and is not officially associated with Firi.
