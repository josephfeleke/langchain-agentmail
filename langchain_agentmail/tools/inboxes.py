"""Tools for managing AgentMail inboxes."""

from __future__ import annotations

import json
from typing import Optional, Type

from pydantic import BaseModel, Field

from langchain_agentmail.tools.base import (
    AgentMailBaseTool,
    _format_error,
    _model_dump,
)


class _ListInboxesInput(BaseModel):
    limit: Optional[int] = Field(
        default=None,
        description="Maximum number of inboxes to return.",
    )
    page_token: Optional[str] = Field(
        default=None, description="Opaque pagination token from a previous response."
    )


class AgentMailListInboxesTool(AgentMailBaseTool):
    name: str = "agentmail_list_inboxes"
    description: str = (
        "List the AgentMail inboxes owned by the agent. Returns a JSON payload "
        "with inbox_id, email, and display_name for each inbox. Use this first "
        "when you don't know which inbox_id to operate on."
    )
    args_schema: Type[BaseModel] = _ListInboxesInput

    def _run(
        self,
        limit: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> str:
        try:
            kwargs = {}
            if limit is not None:
                kwargs["limit"] = limit
            if page_token is not None:
                kwargs["page_token"] = page_token
            resp = self.sdk.inboxes.list(**kwargs)
            return json.dumps(_model_dump(resp), default=str)
        except Exception as e:
            return _format_error(e)


class _CreateInboxInput(BaseModel):
    username: Optional[str] = Field(
        default=None,
        description="Local part of the email address. Random if omitted.",
    )
    domain: Optional[str] = Field(
        default=None,
        description="Verified domain to use. Defaults to agentmail.to.",
    )
    display_name: Optional[str] = Field(
        default=None, description="Human-readable sender name shown to recipients."
    )
    client_id: Optional[str] = Field(
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
    args_schema: Type[BaseModel] = _CreateInboxInput

    def _run(
        self,
        username: Optional[str] = None,
        domain: Optional[str] = None,
        display_name: Optional[str] = None,
        client_id: Optional[str] = None,
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
            return json.dumps(_model_dump(resp), default=str)
        except Exception as e:
            return _format_error(e)
