"""CLI helper to fetch live balances via the Firi API."""

from __future__ import annotations

import json
import os
import sys

from firipy import FiriAPI, FiriAPIError, FiriHTTPError


def main() -> None:
    """Print the authenticated user's balances in JSON form."""
    api_key = os.environ.get("API_KEY_FIRI")
    if not api_key:
        sys.exit("Set API_KEY_FIRI with your Firi API key before running this script.")

    client = FiriAPI(api_key, rate_limit=0.3, raise_on_error=True)
    try:
        balances = client.balances()
    except (FiriHTTPError, FiriAPIError) as exc:
        sys.exit(f"Unable to fetch balances: {exc}")

    print(json.dumps(balances, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
