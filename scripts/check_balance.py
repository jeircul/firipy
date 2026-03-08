"""CLI helper to fetch and display live account data via the Firi API."""

import asyncio
import json
import os
import sys

from firipy import FiriAPI, FiriAPIError, FiriHTTPError


async def main() -> None:
    """Print balances, deposit addresses, and active orders."""
    api_key = os.environ.get("API_KEY_FIRI")
    if not api_key:
        sys.exit("Set API_KEY_FIRI with your Firi API key before running this script.")

    async with FiriAPI(api_key, rate_limit=0.3, raise_on_error=True) as client:
        try:
            balances = await client.balances()
            deposit_addr = await client.deposit_address()
            active_orders = await client.orders()
            markets = await client.markets()
        except (FiriHTTPError, FiriAPIError) as exc:
            sys.exit(f"API error: {exc}")

    print("=== Balances ===")
    print(json.dumps(balances, indent=2))

    print("\n=== Deposit Addresses ===")
    print(json.dumps(deposit_addr, indent=2))

    print("\n=== Active Orders ===")
    print(json.dumps(active_orders, indent=2))

    print("\n=== Available Markets ===")
    print(json.dumps(markets, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
