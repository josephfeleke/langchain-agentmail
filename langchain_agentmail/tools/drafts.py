"""Tools for composing and sending AgentMail drafts.

Drafts let an agent stage a message, revise it, and send later (or on a
schedule). The SDK exposes these under `sdk.inboxes.drafts.{create,update,
send,delete}` — one tool per verb so agents can reason about each step.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from langchain_agentmail.tools.base import AgentMailBaseTool, _format_error
from langchain_agentmail.tools.schemas import Addresses


class _CreateDraftInput(BaseModel):
    inbox_id: str = Field(description="Inbox the draft will be created in.")
    to: Addresses | None = Field(default=None, description="Recipient(s).")
    cc: Addresses | None = Field(default=None, description="CC recipient(s).")
    bcc: Addresses | None = Field(default=None, description="BCC recipient(s).")
    reply_to: Addresses | None = Field(default=None, description="Reply-To address(es).")
    subject: str | None = Field(default=None, description="Draft subject.")
    text: str | None = Field(default=None, description="Plain-text body.")
    html: str | None = Field(default=None, description="HTML body.")
    labels: list[str] | None = Field(default=None, description="Labels to tag.")
    in_reply_to: str | None = Field(
        default=None,
        description="Message ID this draft replies to (thread continuation).",
    )
    send_at: str | None = Field(
        default=None,
        description="ISO-8601 timestamp to schedule the draft for.",
    )


class AgentMailCreateDraftTool(AgentMailBaseTool):
    name: str = "agentmail_create_draft"
    description: str = (
        "Create a new draft in the given inbox. Returns the draft_id so the "
        "agent can later revise it with agentmail_update_draft or ship it "
        "with agentmail_send_draft. Use `send_at` to schedule delivery."
    )
    args_schema: type[BaseModel] = _CreateDraftInput

    def _run(self, inbox_id: str, **fields: Any) -> str:
        try:
            kwargs = {k: v for k, v in fields.items() if v is not None}
            resp = self.sdk.inboxes.drafts.create(inbox_id=inbox_id, **kwargs)
            return self._format(resp)
        except Exception as e:
            return _format_error(e)


class _UpdateDraftInput(BaseModel):
    inbox_id: str = Field(description="Inbox that owns the draft.")
    draft_id: str = Field(description="Draft to update.")
    to: Addresses | None = Field(default=None, description="New recipient(s).")
    cc: Addresses | None = Field(default=None, description="New CC(s).")
    bcc: Addresses | None = Field(default=None, description="New BCC(s).")
    reply_to: Addresses | None = Field(default=None, description="New Reply-To.")
    subject: str | None = Field(default=None, description="New subject.")
    text: str | None = Field(default=None, description="New plain-text body.")
    html: str | None = Field(default=None, description="New HTML body.")
    send_at: str | None = Field(
        default=None,
        description="ISO-8601 reschedule timestamp.",
    )


class AgentMailUpdateDraftTool(AgentMailBaseTool):
    name: str = "agentmail_update_draft"
    description: str = (
        "Revise an existing draft. Only the fields you pass are modified; "
        "omitted fields keep their current values."
    )
    args_schema: type[BaseModel] = _UpdateDraftInput

    def _run(self, inbox_id: str, draft_id: str, **fields: Any) -> str:
        try:
            kwargs = {k: v for k, v in fields.items() if v is not None}
            resp = self.sdk.inboxes.drafts.update(inbox_id=inbox_id, draft_id=draft_id, **kwargs)
            return self._format(resp)
        except Exception as e:
            return _format_error(e)


class _SendDraftInput(BaseModel):
    inbox_id: str = Field(description="Inbox that owns the draft.")
    draft_id: str = Field(description="Draft to send.")
    add_labels: list[str] | None = Field(
        default=None, description="Labels to apply to the resulting message."
    )
    remove_labels: list[str] | None = Field(
        default=None, description="Labels to strip before send."
    )


class AgentMailSendDraftTool(AgentMailBaseTool):
    name: str = "agentmail_send_draft"
    description: str = (
        "Send a previously created draft as a real message. Returns the "
        "resulting message_id and thread_id."
    )
    args_schema: type[BaseModel] = _SendDraftInput

    def _run(
        self,
        inbox_id: str,
        draft_id: str,
        add_labels: list[str] | None = None,
        remove_labels: list[str] | None = None,
    ) -> str:
        try:
            kwargs: dict[str, Any] = {}
            if add_labels is not None:
                kwargs["add_labels"] = add_labels
            if remove_labels is not None:
                kwargs["remove_labels"] = remove_labels
            resp = self.sdk.inboxes.drafts.send(inbox_id=inbox_id, draft_id=draft_id, **kwargs)
            return self._format(resp)
        except Exception as e:
            return _format_error(e)


class _DeleteDraftInput(BaseModel):
    inbox_id: str = Field(description="Inbox that owns the draft.")
    draft_id: str = Field(description="Draft to delete.")


class AgentMailDeleteDraftTool(AgentMailBaseTool):
    name: str = "agentmail_delete_draft"
    description: str = (
        "Permanently delete a draft. Use when the agent decides not to send "
        "a staged message. Returns an empty payload on success."
    )
    args_schema: type[BaseModel] = _DeleteDraftInput

    def _run(self, inbox_id: str, draft_id: str) -> str:
        try:
            resp = self.sdk.inboxes.drafts.delete(inbox_id=inbox_id, draft_id=draft_id)
            return self._format(resp) if resp is not None else '{"deleted": true}'
        except Exception as e:
            return _format_error(e)
