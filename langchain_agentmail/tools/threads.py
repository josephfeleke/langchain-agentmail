"""Tools for browsing AgentMail threads."""

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


class _ListThreadsInput(BaseModel):
    limit: Optional[int] = Field(default=None, description="Max threads to return.")
    page_token: Optional[str] = Field(default=None, description="Pagination token.")
    labels: Optional[List[str]] = Field(
        default=None,
        description="Filter to threads having any of these labels (e.g. ['inbox', 'unread']).",
    )
    before: Optional[str] = Field(
        default=None,
        description="ISO-8601 timestamp; only threads before this are returned.",
    )
    after: Optional[str] = Field(
        default=None,
        description="ISO-8601 timestamp; only threads after this are returned.",
    )
    ascending: Optional[bool] = Field(
        default=None, description="Sort oldest-first when true."
    )


class AgentMailListThreadsTool(AgentMailBaseTool):
    name: str = "agentmail_list_threads"
    description: str = (
        "List email threads across all inboxes the agent has access to. Each "
        "item includes thread_id, subject, preview, senders, recipients, and "
        "last-message timestamp. Use this to triage unread mail — then call "
        "agentmail_get_thread with a specific thread_id to read the full "
        "conversation."
    )
    args_schema: Type[BaseModel] = _ListThreadsInput

    def _run(
        self,
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
            resp = self.sdk.threads.list(**kwargs)
            return json.dumps(_model_dump(resp), default=str)
        except Exception as e:
            return _format_error(e)


class _GetThreadInput(BaseModel):
    thread_id: str = Field(description="ID of the thread to fetch.")


class AgentMailGetThreadTool(AgentMailBaseTool):
    name: str = "agentmail_get_thread"
    description: str = (
        "Fetch the full contents of a single email thread, including every "
        "message's text body. Use after agentmail_list_threads narrows down "
        "which conversation you care about."
    )
    args_schema: Type[BaseModel] = _GetThreadInput

    def _run(self, thread_id: str) -> str:
        try:
            resp = self.sdk.threads.get(thread_id=thread_id)
            dumped = _model_dump(resp)
            # Protect the agent's context window: trim giant message bodies.
            for msg in dumped.get("messages", []) if isinstance(dumped, dict) else []:
                if "text" in msg:
                    msg["text"] = _truncate(msg.get("text"), 4000)
                if "html" in msg:
                    # HTML bloats context with very little signal — drop it.
                    msg.pop("html", None)
            return json.dumps(dumped, default=str)
        except Exception as e:
            return _format_error(e)
