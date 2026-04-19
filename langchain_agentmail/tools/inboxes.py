"""Tools for managing AgentMail inboxes."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from langchain_agentmail.tools.base import AgentMailBaseTool, _format_error


class _ListInboxesInput(BaseModel):
    limit: int | None = Field(
        default=None,
        description="Maximum number of inboxes to return.",
    )
    page_token: str | None = Field(
        default=None, description="Opaque pagination token from a previous response."
    )


class AgentMailListInboxesTool(AgentMailBaseTool):
    name: str = "agentmail_list_inboxes"
    description: str = (
        "List the AgentMail inboxes owned by the agent. Returns a JSON payload "
        "with inbox_id, email, and display_name for each inbox. Use this first "
        "when you don't know which inbox_id to operate on."
    )
    args_schema: type[BaseModel] = _ListInboxesInput

    def _run(
        self,
        limit: int | None = None,
        page_token: str | None = None,
    ) -> str:
        try:
            kwargs: dict[str, Any] = {}
            if limit is not None:
                kwargs["limit"] = limit
            if page_token is not None:
                kwargs["page_token"] = page_token
            resp = self.sdk.inboxes.list(**kwargs)
            return self._format(resp)
        except Exception as e:
            return _format_error(e)


class _CreateInboxInput(BaseModel):
    username: str | None = Field(
        default=None,
        description="Local part of the email address. Random if omitted.",
    )
    domain: str | None = Field(
        default=None,
        description="Verified domain to use. Defaults to agentmail.to.",
    )
    display_name: str | None = Field(
        default=None, description="Human-readable sender name shown to recipients."
    )
    client_id: str | None = Field(
        default=None,
        description="Your own identifier to tag this inbox with. Useful for "
        "mapping AgentMail inboxes to records in your system.",
    )


class AgentMailCreateInboxTool(AgentMailBaseTool):
    name: str = "agentmail_create_inbox"
    description: str = (
        "Create a new AgentMail inbox that the agent can send and receive "
        "email from. Returns the new inbox's id and email address."
    )
    args_schema: type[BaseModel] = _CreateInboxInput

    def _run(
        self,
        username: str | None = None,
        domain: str | None = None,
        display_name: str | None = None,
        client_id: str | None = None,
    ) -> str:
        try:
            kwargs = {
                k: v
                for k, v in {
                    "username": username,
                    "domain": domain,
                    "display_name": display_name,
                    "client_id": client_id,
                }.items()
                if v is not None
            }
            resp = self.sdk.inboxes.create(**kwargs) if kwargs else self.sdk.inboxes.create()
            return self._format(resp)
        except Exception as e:
            return _format_error(e)
