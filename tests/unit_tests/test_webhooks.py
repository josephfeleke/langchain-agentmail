"""Webhook tests — signature verification, event parsing, FastAPI router."""

from __future__ import annotations

import base64
import hashlib
import hmac
import time

import pytest

from langchain_agentmail.webhooks import (
    InvalidSignatureError,
    MessageReceivedEvent,
    parse_event,
    verify_signature,
)


def _sign(payload: bytes, secret_b64: str, msg_id: str, ts: int) -> str:
    key = base64.b64decode(secret_b64)
    signed = f"{msg_id}.{ts}.".encode() + payload
    return "v1," + base64.b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode()


def test_verify_signature_accepts_valid():
    secret_b64 = base64.b64encode(b"supersecret").decode()
    payload = b'{"event_type": "message.received"}'
    ts = int(time.time())
    sig = _sign(payload, secret_b64, "msg_1", ts)

    verify_signature(
        payload=payload,
        secret=f"whsec_{secret_b64}",
        svix_id="msg_1",
        svix_timestamp=str(ts),
        svix_signature=sig,
    )


def test_verify_signature_rejects_tampered_body():
    secret_b64 = base64.b64encode(b"supersecret").decode()
    ts = int(time.time())
    sig = _sign(b"original", secret_b64, "msg_1", ts)

    with pytest.raises(InvalidSignatureError):
        verify_signature(
            payload=b"tampered",
            secret=f"whsec_{secret_b64}",
            svix_id="msg_1",
            svix_timestamp=str(ts),
            svix_signature=sig,
        )


def test_verify_signature_rejects_stale_timestamp():
    secret_b64 = base64.b64encode(b"supersecret").decode()
    payload = b"{}"
    stale = int(time.time()) - 3600
    sig = _sign(payload, secret_b64, "msg_1", stale)

    with pytest.raises(InvalidSignatureError, match="skew"):
        verify_signature(
            payload=payload,
            secret=f"whsec_{secret_b64}",
            svix_id="msg_1",
            svix_timestamp=str(stale),
            svix_signature=sig,
        )


def test_parse_event_picks_right_union_member():
    event = parse_event(
        {
            "type": "event",
            "event_type": "message.received",
            "event_id": "evt_1",
            "message": {"message_id": "m_1", "subject": "hi"},
            "thread": {"thread_id": "t_1"},
        }
    )
    assert isinstance(event, MessageReceivedEvent)
    assert event.message["message_id"] == "m_1"


def test_parse_event_tolerates_extra_fields():
    event = parse_event(
        {
            "type": "event",
            "event_type": "message.sent",
            "event_id": "evt_2",
            "send": {"message_id": "m_2"},
            "future_field": "who knows",
        }
    )
    assert event.event_type == "message.sent"
    # Extra field stored on the model — preserved via `extra="allow"`.
    assert getattr(event, "future_field", None) == "who knows"


def test_parse_event_rejects_unknown_type():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        parse_event({"event_type": "nonsense", "event_id": "x", "type": "event"})
