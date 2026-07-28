"""Unit tests for :mod:`firipy._hmac`."""

import hashlib
import hmac
import json

from firipy._hmac import CLIENT_ID_HEADER, SIGNATURE_HEADER, sign_request

SECRET = "test-secret"
TIMESTAMP = 1700000000


def _expected_signature(payload: dict[str, str], *, compact: bool) -> str:
    separators = (",", ":") if compact else (", ", ":")
    encoded = json.dumps(payload, separators=separators)
    return hmac.new(SECRET.encode(), encoded.encode(), hashlib.sha256).hexdigest()


def test_sign_request_get_style_no_body() -> None:
    headers, params = sign_request(SECRET, timestamp=TIMESTAMP)

    expected_payload = {"timestamp": str(TIMESTAMP), "validity": "2000"}
    expected_signature = _expected_signature(expected_payload, compact=True)

    assert headers[SIGNATURE_HEADER] == expected_signature
    assert params == expected_payload
    assert all(isinstance(v, str) for v in headers.values())
    assert all(isinstance(v, str) for v in params.values())
    assert params["validity"] == "2000"


def test_sign_request_post_orders_with_body() -> None:
    body = {"market": "BTCNOK", "price": "1000", "amount": "1", "type": "ask"}
    headers, params = sign_request(SECRET, body=body, timestamp=TIMESTAMP)

    expected_payload = {"timestamp": str(TIMESTAMP), "validity": "2000", **body}
    expected_signature = _expected_signature(expected_payload, compact=True)

    assert headers[SIGNATURE_HEADER] == expected_signature
    assert params == {"timestamp": str(TIMESTAMP), "validity": "2000"}
    assert all(isinstance(v, str) for v in headers.values())
    assert all(isinstance(v, str) for v in params.values())


def test_sign_request_compact_vs_spaced_differ() -> None:
    body = {"market": "BTCNOK", "price": "1000", "amount": "1", "type": "ask"}

    compact_headers, compact_params = sign_request(
        SECRET, body=body, timestamp=TIMESTAMP, compact=True
    )
    spaced_headers, spaced_params = sign_request(
        SECRET, body=body, timestamp=TIMESTAMP, compact=False
    )

    expected_payload = {"timestamp": str(TIMESTAMP), "validity": "2000", **body}
    expected_compact = _expected_signature(expected_payload, compact=True)
    expected_spaced = _expected_signature(expected_payload, compact=False)

    assert compact_headers[SIGNATURE_HEADER] == expected_compact
    assert spaced_headers[SIGNATURE_HEADER] == expected_spaced
    assert compact_headers[SIGNATURE_HEADER] != spaced_headers[SIGNATURE_HEADER]
    assert compact_params == spaced_params


def test_client_id_header_constant_exists() -> None:
    assert CLIENT_ID_HEADER == "firi-user-clientid"
