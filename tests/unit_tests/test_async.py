"""Async path tests — every tool inherits `_arun` from base, so proving
`ainvoke` works on a representative tool per SDK surface covers all 9."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from langchain_agentmail import (
    AgentMailClient,
    AgentMailListInboxesTool,
    AgentMailListThreadsTool,
    AgentMailSendTool,
)


def _fake_client() -> AgentMailClient:
    sdk = SimpleNamespace(
        inboxes=SimpleNamespace(
            list=MagicMock(return_value={"inboxes": [], "count": 0}),
            messages=SimpleNamespace(
                send=MagicMock(return_value={"message_id": "m_async", "thread_id": "t_1"}),
            ),
        ),
        threads=SimpleNamespace(
            list=MagicMock(return_value={"threads": [], "count": 0}),
        ),
    )
    return AgentMailClient(client=sdk)


@pytest.mark.asyncio
async def test_ainvoke_list_inboxes():
    client = _fake_client()
    tool = AgentMailListInboxesTool(client=client)
    out = await tool.ainvoke({"limit": 3})
    assert '"count": 0' in out
    client.sdk.inboxes.list.assert_called_once_with(limit=3)


@pytest.mark.asyncio
async def test_ainvoke_send_message():
    client = _fake_client()
    tool = AgentMailSendTool(client=client)
    out = await tool.ainvoke(
        {
            "inbox_id": "ib_1",
            "to": "alice@example.com",
            "subject": "hi",
            "text": "async body",
        }
    )
    assert '"message_id": "m_async"' in out
    client.sdk.inboxes.messages.send.assert_called_once()


@pytest.mark.asyncio
async def test_ainvoke_list_threads():
    client = _fake_client()
    tool = AgentMailListThreadsTool(client=client)
    out = await tool.ainvoke({"limit": 1})
    assert '"count": 0' in out
    client.sdk.threads.list.assert_called_once_with(limit=1)


@pytest.mark.asyncio
async def test_ainvoke_error_formats_not_raises():
    """A failing SDK call inside `_run` must come back as a string, not crash."""
    client = _fake_client()
    client.sdk.inboxes.list = MagicMock(side_effect=RuntimeError("boom"))
    tool = AgentMailListInboxesTool(client=client)
    out = await tool.ainvoke({})
    assert out.startswith("RuntimeError:")
