"""Shared base class and helpers for AgentMail-backed LangChain tools."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Optional

from langchain_core.tools import BaseTool
from pydantic import Field

from langchain_agentmail.client import AgentMailClient


class AgentMailBaseTool(BaseTool):
    """Holds the shared AgentMail client that every tool in this package uses."""

    client: AgentMailClient = Field(default_factory=AgentMailClient)

    # BaseTool uses pydantic v2 under the hood; this allows the non-pydantic
    # AgentMailClient to be stored as a field.
    model_config = {"arbitrary_types_allowed": True}

    @property
    def sdk(self) -> Any:
        return self.client.sdk

    def _format(self, resp: Any) -> str:
        """Dump an SDK response into a JSON string an LLM can consume."""
        return json.dumps(_model_dump(resp), default=str)

    async def _arun(self, *args: Any, **kwargs: Any) -> str:
        """Run the tool on a worker thread so async agents don't stall.

        BaseTool's default `_arun` uses `run_in_executor`; we override with
        `asyncio.to_thread` because it propagates contextvars correctly — a
        requirement for LangGraph's callback manager and tracing. Strips the
        async-only `run_manager` kwarg before dispatching to the sync `_run`.
        """
        kwargs.pop("run_manager", None)
        return await asyncio.to_thread(self._run, *args, **kwargs)


def _format_error(e: Exception) -> str:
    """Render errors as strings the LLM can read without blowing up the agent loop."""
    return f"{type(e).__name__}: {e}"


def _model_dump(obj: Any) -> Any:
    """Best-effort conversion of SDK response objects into plain dicts/lists.

    The AgentMail SDK returns pydantic models; older versions may return dicts.
    We prefer `model_dump(mode='json')` so datetimes are stringified."""
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump(mode="json", exclude_none=True)
        except TypeError:
            return obj.model_dump(exclude_none=True)
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, list):
        return [_model_dump(i) for i in obj]
    return obj


def _truncate(value: Optional[str], limit: int = 2000) -> Optional[str]:
    if value is None:
        return None
    if len(value) <= limit:
        return value
    return value[:limit] + f"... [truncated, {len(value) - limit} chars omitted]"
