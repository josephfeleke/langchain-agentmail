"""Tools for reading, sending, and replying to AgentMail messages."""

from __future__ import annotations

import json
from typing import List, Optional, Type

from pydantic import BaseModel, Field

from langchain_agentmail.tools.base import (
    AgentMailBaseTool,
    _format_error,
    _model_dump,
    _truncate,
)
from langchain_agentmail.tools.schemas import Addresses


class _ListMessagesInput(BaseModel):
    inbox_id: str = Field(description="Inbox to list messages from.")
    limit: Optional[int] = Field(default=None, description="Max messages to return.")
    page_token: Optional[str] = Field(default=None, description="Pagination token.")
    labels: Optional[List[str]] = Field(
        default=None, description="Filter by labels (e.g. ['inbox', 'unread'])."
    )
    before: Optional[str] = Field(default=None, description="ISO-8601 upper bound.")
    after: Optional[str] = Field(default=None, description="ISO-8601 lower bound.")
    ascending: Optional[bool] = Field(default=None, description="Oldest-first ordering.")


class AgentMailListMessagesTool(AgentMailBaseTool):
    name: str = "agentmail_list_messages"
    description: str = (
        "List messages within a specific inbox. Returns lightweight message "
        "items (message_id, from, to, subject, preview) — fetch the full body "
        "with agentmail_get_message."
    )
    args_schema: Type[BaseModel] = _ListMessagesInput

    def _run(
        self,
        inbox_id: str,
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
        labels: Optional[List[str]] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        ascending: Optional[bool] = None,
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
    args_schema: Type[BaseModel] = _GetMessageInput

    def _run(self, inbox_id: str, message_id: str) -> str:
        try:
            resp = self.sdk.inboxes.messages.get(
                inbox_id=inbox_id, message_id=message_id
            )
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
    subject: Optional[str] = Field(default=None, description="Message subject.")
    text: Optional[str] = Field(default=None, description="Plain-text body.")
    html: Optional[str] = Field(default=None, description="HTML body.")
    cc: Optional[Addresses] = Field(default=None, description="CC recipient(s).")
    bcc: Optional[Addresses] = Field(default=None, description="BCC recipient(s).")
    reply_to: Optional[Addresses] = Field(
        default=None, description="Reply-To header value."
    )
    labels: Optional[List[str]] = Field(
        default=None, description="Labels to attach to the sent message."
    )


class AgentMailSendTool(AgentMailBaseTool):
    name: str = "agentmail_send_message"
    description: str = (
        "Send a new email from the given AgentMail inbox. Provide at least one "
        "of text or html; subject is strongly recommended. Returns the "
        "message_id and thread_id of the sent message."
    )
    args_schema: Type[BaseModel] = _SendMessageInput

    def _run(
        self,
        inbox_id: str,
        to: Addresses,
        subject: Optional[str] = None,
        text: Optional[str] = None,
        html: Optional[str] = None,
        cc: Optional[Addresses] = None,
        bcc: Optional[Addresses] = None,
        reply_to: Optional[Addresses] = None,
        labels: Optional[List[str]] = None,
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
    text: Optional[str] = Field(default=None, description="Plain-text reply body.")
    html: Optional[str] = Field(default=None, description="HTML reply body.")
    reply_all: Optional[bool] = Field(
        default=None, description="Reply to everyone on the original thread."
    )
    to: Optional[Addresses] = Field(
        default=None,
        description="Override the reply recipients. Omit to reply to the sender.",
    )
    cc: Optional[Addresses] = Field(default=None, description="CC override.")
    bcc: Optional[Addresses] = Field(default=None, description="BCC override.")
    labels: Optional[List[str]] = Field(
        default=None, description="Labels for the reply."
    )


class AgentMailReplyTool(AgentMailBaseTool):
    name: str = "agentmail_reply_to_message"
    description: str = (
        "Reply to an existing email inside the same thread. Keeps the thread "
        "intact by sending with the right In-Reply-To headers. Use after "
        "agentmail_get_message to read what you're replying to."
    )
    args_schema: Type[BaseModel] = _ReplyInput

    def _run(
        self,
        inbox_id: str,
        message_id: str,
        text: Optional[str] = None,
        html: Optional[str] = None,
        reply_all: Optional[bool] = None,
        to: Optional[Addresses] = None,
        cc: Optional[Addresses] = None,
        bcc: Optional[Addresses] = None,
        labels: Optional[List[str]] = None,
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
    add_labels: Optional[List[str]] = Field(
        default=None, description="Labels to add."
    )
    remove_labels: Optional[List[str]] = Field(
        default=None, description="Labels to remove."
    )


class AgentMailUpdateMessageLabelsTool(AgentMailBaseTool):
    name: str = "agentmail_update_message_labels"
    description: str = (
        "Add or remove labels on a message. Useful for marking messages "
        "handled, archived, or flagging follow-ups. System labels (sent, "
        "received, trash, etc.) cannot be modified."
    )
    args_schema: Type[BaseModel] = _UpdateLabelsInput

    def _run(
        self,
        inbox_id: str,
        message_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
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
