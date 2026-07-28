"""HMAC request signing for Firi's ``HMAC_encrypted_secretKey`` auth scheme.

Firi authenticates private endpoints by having the client sign a JSON payload
(timestamp, validity window, and the request body) with the user's secret
key using HMAC-SHA256, then send the hex digest and the payload fields as
headers/params alongside the request.
"""

import hashlib
import hmac
import json
import time
from typing import Any

SIGNATURE_HEADER = "firi-user-signature"
CLIENT_ID_HEADER = "firi-user-clientid"


def sign_request(
    secret_key: str,
    *,
    validity_ms: int = 2000,
    body: dict[str, Any] | None = None,
    timestamp: int | None = None,
    compact: bool = True,
) -> tuple[dict[str, str], dict[str, str]]:
    """Sign a Firi request payload and return (headers, params).

    ``compact`` controls JSON separator whitespace. Firi's own Node and
    Kotlin reference samples disagree on this (compact vs spaced), so it is
    exposed here in case a given endpoint requires the non-compact form.
    """
    ts = str(timestamp if timestamp is not None else int(time.time()))
    validity = str(validity_ms)

    payload: dict[str, str] = {"timestamp": ts, "validity": validity}
    if body:
        payload.update({key: str(value) for key, value in body.items()})

    separators = (",", ":") if compact else (", ", ":")
    encoded = json.dumps(payload, separators=separators)

    signature = hmac.new(
        secret_key.encode(), encoded.encode(), hashlib.sha256
    ).hexdigest()

    return {SIGNATURE_HEADER: signature}, {"timestamp": ts, "validity": validity}
