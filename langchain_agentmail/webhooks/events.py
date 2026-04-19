"""Typed pydantic models for AgentMail webhook events.

Each event type is a separate model with a literal `event_type` discriminator
so pydantic can resolve the right class from a raw payload. All models set
`extra = "allow"` so newly added AgentMail fields don't break parsing.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class _EventBase(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: Literal["event"] = "event"
    event_id: str


class MessageReceivedEvent(_EventBase):
    event_type: Literal["message.received"]
    message: dict[str, Any]
    thread: dict[str, Any]


class MessageSentEvent(_EventBase):
    event_type: Literal["message.sent"]
    send: dict[str, Any]


class MessageDeliveredEvent(_EventBase):
    event_type: Literal["message.delivered"]
    delivery: dict[str, Any]


class MessageBouncedEvent(_EventBase):
    event_type: Literal["message.bounced"]
    bounce: dict[str, Any]


class MessageComplainedEvent(_EventBase):
    event_type: Literal["message.complained"]
    complaint: dict[str, Any]


class MessageRejectedEvent(_EventBase):
    event_type: Literal["message.rejected"]
    reject: dict[str, Any]


class DomainVerifiedEvent(_EventBase):
    event_type: Literal["domain.verified"]
    domain: dict[str, Any]


AgentMailEvent = Annotated[
    MessageReceivedEvent
    | MessageSentEvent
    | MessageDeliveredEvent
    | MessageBouncedEvent
    | MessageComplainedEvent
    | MessageRejectedEvent
    | DomainVerifiedEvent,
    Field(discriminator="event_type"),
]


_ADAPTER: TypeAdapter[AgentMailEvent] = TypeAdapter(AgentMailEvent)


def parse_event(payload: dict[str, Any]) -> AgentMailEvent:
    """Turn a raw JSON payload into a typed `AgentMailEvent` union member.

    Unknown fields are preserved (stored on the model instance) so webhook
    handlers never throw on a future AgentMail schema change."""
    return _ADAPTER.validate_python(payload)
