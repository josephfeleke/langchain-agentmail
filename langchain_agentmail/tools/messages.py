"""Tools for reading, sending, and replying to AgentMail messages."""

from __future__ import annotations

import json

from pydantic import BaseModel, Field

from langchain_agentmail.tools.base import (
    AgentMailBaseTool,
    _format_error,
    _model_dump,
    _truncate,
)
from langchain_agentmail.tools.schemas import Addresses, SendAttachmentSpec


def _serialize_attachments(
    attachments: list[SendAttachmentSpec] | list[dict] | None,
) -> list[dict] | None:
    """Normalize attachments into plain dicts the SDK accepts.

    Agents can pass `SendAttachmentSpec` instances (typed) or raw dicts
    (untyped); both paths end up as a list of dicts with `None` fields
    dropped."""
    if not attachments:
        return None
    out: list[dict] = []
    for item in attachments:
        if isinstance(item, SendAttachmentSpec):
            out.append(item.model_dump(exclude_none=True))
        else:
            out.append({k: v for k, v in item.items() if v is not None})
    return out


class _ListMessagesInput(BaseModel):
    inbox_id: str = Field(description="Inbox to list messages from.")
    limit: int | None = Field(default=None, description="Max messages to return.")
    page_token: str | None = Field(default=None, description="Pagination token.")
    labels: list[str] | None = Field(
        default=None, description="Filter by labels (e.g. ['inbox', 'unread'])."
    )
    before: str | None = Field(default=None, description="ISO-8601 upper bound.")
    after: str | None = Field(default=None, description="ISO-8601 lower bound.")
    ascending: bool | None = Field(default=None, description="Oldest-first ordering.")


class AgentMailListMessagesTool(AgentMailBaseTool):
    name: str = "agentmail_list_messages"
    description: str = (
        "List messages within a specific inbox. Returns lightweight message "
        "items (message_id, from, to, subject, preview) — fetch the full body "
        "with agentmail_get_message."
    )
    args_schema: type[BaseModel] = _ListMessagesInput

    def _run(
        self,
        inbox_id: str,
        limit: int | None = None,
        page_token: str | None = None,
        labels: list[str] | None = None,
        before: str | None = None,
        after: str | None = None,
        ascending: bool | None = None,
    ) -> str:
        try:
            kwargs = {
                k: v
                for k, v in {
                    "limit": limit,
                    "page_token": page_token,
                    "labels": labels,
                    "before": before,
                    "after": after,
                    "ascending": ascending,
                }.items()
                if v is not None
            }
            resp = self.sdk.inboxes.messages.list(inbox_id=inbox_id, **kwargs)
            return self._format(resp)
        except Exception as e:
            return _format_error(e)


class _GetMessageInput(BaseModel):
    inbox_id: str = Field(description="Inbox that owns the message.")
    message_id: str = Field(description="Message to fetch.")


class AgentMailGetMessageTool(AgentMailBaseTool):
    name: str = "agentmail_get_message"
    description: str = (
        "Fetch a single message with its full plain-text body, sender, "
        "recipients, and metadata. HTML content is stripped to save tokens."
    )
    args_schema: type[BaseModel] = _GetMessageInput

    def _run(self, inbox_id: str, message_id: str) -> str:
        try:
            resp = self.sdk.inboxes.messages.get(inbox_id=inbox_id, message_id=message_id)
            dumped = _model_dump(resp)
            if isinstance(dumped, dict):
                dumped.pop("html", None)
                dumped.pop("extracted_html", None)
                if "text" in dumped:
                    dumped["text"] = _truncate(dumped["text"], 6000)
                if "extracted_text" in dumped:
                    dumped["extracted_text"] = _truncate(dumped["extracted_text"], 6000)
            return json.dumps(dumped, default=str)
        except Exception as e:
            return _format_error(e)


class _SendMessageInput(BaseModel):
    inbox_id: str = Field(description="Inbox to send the message from.")
    to: Addresses = Field(description="Recipient email(s).")
    subject: str | None = Field(default=None, description="Message subject.")
    text: str | None = Field(default=None, description="Plain-text body.")
    html: str | None = Field(default=None, description="HTML body.")
    cc: Addresses | None = Field(default=None, description="CC recipient(s).")
    bcc: Addresses | None = Field(default=None, description="BCC recipient(s).")
    reply_to: Addresses | None = Field(default=None, description="Reply-To header value.")
    labels: list[str] | None = Field(
        default=None, description="Labels to attach to the sent message."
    )
    attachments: list[SendAttachmentSpec] | None = Field(
        default=None,
        description="Files to attach. Each must set `content` (base64) OR `url`.",
    )


class AgentMailSendTool(AgentMailBaseTool):
    name: str = "agentmail_send_message"
    description: str = (
        "Send a new email from the given AgentMail inbox. Provide at least one "
        "of text or html; subject is strongly recommended. Returns the "
        "message_id and thread_id of the sent message."
    )
    args_schema: type[BaseModel] = _SendMessageInput

    def _run(
        self,
        inbox_id: str,
        to: Addresses,
        subject: str | None = None,
        text: str | None = None,
        html: str | None = None,
        cc: Addresses | None = None,
        bcc: Addresses | None = None,
        reply_to: Addresses | None = None,
        labels: list[str] | None = None,
        attachments: list[SendAttachmentSpec] | list[dict] | None = None,
    ) -> str:
        if text is None and html is None:
            return "Error: must provide at least one of `text` or `html`."
        try:
            kwargs = {
                k: v
                for k, v in {
                    "to": to,
                    "subject": subject,
                    "text": text,
                    "html": html,
                    "cc": cc,
                    "bcc": bcc,
                    "reply_to": reply_to,
                    "labels": labels,
                    "attachments": _serialize_attachments(attachments),
                }.items()
                if v is not None
            }
            resp = self.sdk.inboxes.messages.send(inbox_id=inbox_id, **kwargs)
            return self._format(resp)
        except Exception as e:
            return _format_error(e)


class _ReplyInput(BaseModel):
    inbox_id: str = Field(description="Inbox that owns the message being replied to.")
    message_id: str = Field(description="Message to reply to.")
    text: str | None = Field(default=None, description="Plain-text reply body.")
    html: str | None = Field(default=None, description="HTML reply body.")
    reply_all: bool | None = Field(
        default=None, description="Reply to everyone on the original thread."
    )
    to: Addresses | None = Field(
        default=None,
        description="Override the reply recipients. Omit to reply to the sender.",
    )
    cc: Addresses | None = Field(default=None, description="CC override.")
    bcc: Addresses | None = Field(default=None, description="BCC override.")
    labels: list[str] | None = Field(default=None, description="Labels for the reply.")
    attachments: list[SendAttachmentSpec] | None = Field(
        default=None,
        description="Files to attach. Each must set `content` (base64) OR `url`.",
    )


class AgentMailReplyTool(AgentMailBaseTool):
    name: str = "agentmail_reply_to_message"
    description: str = (
        "Reply to an existing email inside the same thread. Keeps the thread "
        "intact by sending with the right In-Reply-To headers. Use after "
        "agentmail_get_message to read what you're replying to."
    )
    args_schema: type[BaseModel] = _ReplyInput

    def _run(
        self,
        inbox_id: str,
        message_id: str,
        text: str | None = None,
        html: str | None = None,
        reply_all: bool | None = None,
        to: Addresses | None = None,
        cc: Addresses | None = None,
        bcc: Addresses | None = None,
        labels: list[str] | None = None,
        attachments: list[SendAttachmentSpec] | list[dict] | None = None,
    ) -> str:
        if text is None and html is None:
            return "Error: must provide at least one of `text` or `html`."
        try:
            kwargs = {
                k: v
                for k, v in {
                    "text": text,
                    "html": html,
                    "reply_all": reply_all,
                    "to": to,
                    "cc": cc,
                    "bcc": bcc,
                    "labels": labels,
                    "attachments": _serialize_attachments(attachments),
                }.items()
                if v is not None
            }
            resp = self.sdk.inboxes.messages.reply(
                inbox_id=inbox_id, message_id=message_id, **kwargs
            )
            return self._format(resp)
        except Exception as e:
            return _format_error(e)


class _UpdateLabelsInput(BaseModel):
    inbox_id: str = Field(description="Inbox containing the message.")
    message_id: str = Field(description="Message to relabel.")
    add_labels: list[str] | None = Field(default=None, description="Labels to add.")
    remove_labels: list[str] | None = Field(default=None, description="Labels to remove.")


class AgentMailUpdateMessageLabelsTool(AgentMailBaseTool):
    name: str = "agentmail_update_message_labels"
    description: str = (
        "Add or remove labels on a message. Useful for marking messages "
        "handled, archived, or flagging follow-ups. System labels (sent, "
        "received, trash, etc.) cannot be modified."
    )
    args_schema: type[BaseModel] = _UpdateLabelsInput

    def _run(
        self,
        inbox_id: str,
        message_id: str,
        add_labels: list[str] | None = None,
        remove_labels: list[str] | None = None,
    ) -> str:
        if not add_labels and not remove_labels:
            return "Error: provide at least one of add_labels or remove_labels."
        try:
            kwargs = {
                k: v
                for k, v in {
                    "add_labels": add_labels,
                    "remove_labels": remove_labels,
                }.items()
                if v is not None
            }
            resp = self.sdk.inboxes.messages.update(
                inbox_id=inbox_id, message_id=message_id, **kwargs
            )
            return self._format(resp)
        except Exception as e:
            return _format_error(e)
