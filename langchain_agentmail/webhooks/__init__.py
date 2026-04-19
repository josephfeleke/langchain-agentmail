"""Optional subpackage for handling AgentMail webhooks.

Install with:

    pip install 'langchain-agentmail[webhooks]'

Key pieces:

- `verify_signature` — checks svix-signed webhook requests.
- `parse_event` — turns a raw payload dict into a typed event model.
- `AgentMailEvent` — tagged union of every supported event.
- `create_fastapi_router` — opinionated FastAPI router that handles
  verification + parsing and hands a typed event to your callback.
"""

from __future__ import annotations

from langchain_agentmail.webhooks.events import (
    AgentMailEvent,
    DomainVerifiedEvent,
    MessageBouncedEvent,
    MessageComplainedEvent,
    MessageDeliveredEvent,
    MessageReceivedEvent,
    MessageRejectedEvent,
    MessageSentEvent,
    parse_event,
)
from langchain_agentmail.webhooks.verify import (
    InvalidSignatureError,
    verify_signature,
)

__all__ = [
    "AgentMailEvent",
    "DomainVerifiedEvent",
    "InvalidSignatureError",
    "MessageBouncedEvent",
    "MessageComplainedEvent",
    "MessageDeliveredEvent",
    "MessageReceivedEvent",
    "MessageRejectedEvent",
    "MessageSentEvent",
    "parse_event",
    "verify_signature",
]


def create_fastapi_router(*args, **kwargs):  # pragma: no cover - lazy import shim
    """Re-export `create_fastapi_router` with a deferred fastapi import.

    Importing `fastapi` at module load breaks users who install the core
    package without the `webhooks` extra. We import inside the shim so a
    missing dependency only errors when the router is actually requested.
    """
    from langchain_agentmail.webhooks.fastapi import create_fastapi_router as _impl

    return _impl(*args, **kwargs)
