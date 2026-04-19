"""Svix-compatible signature verification for AgentMail webhooks.

AgentMail signs webhook deliveries with svix headers:

    svix-id         a unique message ID
    svix-timestamp  unix seconds, rejected if ±5 min skew from now
    svix-signature  "v1,<base64 hmac-sha256(secret, f'{id}.{ts}.{body}')>"
                    (space-separated — one line may contain multiple sigs)

The secret is the webhook's signing key (starts with `whsec_`). We compute the
expected HMAC over `<svix_id>.<svix_timestamp>.<raw body>` and compare each
submitted signature against it.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import time

DEFAULT_MAX_SKEW_SECONDS = 5 * 60


class InvalidSignatureError(Exception):
    """Raised when webhook signature verification fails."""


def verify_signature(
    *,
    payload: bytes,
    secret: str,
    svix_id: str,
    svix_timestamp: str,
    svix_signature: str,
    max_skew_seconds: int = DEFAULT_MAX_SKEW_SECONDS,
    _now: float | None = None,
) -> None:
    """Verify a webhook request; raise `InvalidSignatureError` on failure.

    Returns `None` on success. `payload` must be the exact raw request body —
    re-serialized JSON will not match the signature.
    """
    if not secret:
        raise InvalidSignatureError("Missing signing secret")
    if not svix_id or not svix_timestamp or not svix_signature:
        raise InvalidSignatureError("Missing svix headers")

    try:
        ts = int(svix_timestamp)
    except ValueError as e:
        raise InvalidSignatureError("svix-timestamp is not an integer") from e

    now = time.time() if _now is None else _now
    if abs(now - ts) > max_skew_seconds:
        raise InvalidSignatureError("Webhook timestamp outside skew window")

    key = _decode_secret(secret)
    signed = f"{svix_id}.{svix_timestamp}.".encode() + payload
    expected = base64.b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode()

    # Header format: "v1,<sig> v1,<sig2> ..." — accept if any matches.
    for token in svix_signature.split(" "):
        if "," not in token:
            continue
        _version, provided = token.split(",", 1)
        if hmac.compare_digest(provided, expected):
            return

    raise InvalidSignatureError("No matching signature")


def _decode_secret(secret: str) -> bytes:
    """Strip the optional `whsec_` prefix and base64-decode the key."""
    if secret.startswith("whsec_"):
        secret = secret[len("whsec_") :]
    return base64.b64decode(secret)
