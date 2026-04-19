"""Unit tests — mock the AgentMail SDK, verify tools pass args through correctly."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from langchain_agentmail import (
    AgentMailClient,
    AgentMailListInboxesTool,
    AgentMailReplyTool,
    AgentMailSendTool,
    AgentMailToolkit,
)


def _fake_client() -> AgentMailClient:
    sdk = SimpleNamespace(
        inboxes=SimpleNamespace(
            list=MagicMock(return_value={"inboxes": [], "count": 0}),
            create=MagicMock(return_value={"inbox_id": "ib_123"}),
            messages=SimpleNamespace(
                list=MagicMock(return_value={"messages": [], "count": 0}),
                get=MagicMock(return_value={"message_id": "m_1", "text": "hi"}),
                send=MagicMock(return_value={"message_id": "m_2", "thread_id": "t_1"}),
                reply=MagicMock(return_value={"message_id": "m_3", "thread_id": "t_1"}),
                update=MagicMock(return_value={"message_id": "m_1", "labels": ["done"]}),
            ),
        ),
        threads=SimpleNamespace(
            list=MagicMock(return_value={"threads": [], "count": 0}),
            get=MagicMock(return_value={"thread_id": "t_1", "messages": []}),
        ),
    )
    return AgentMailClient(client=sdk)


def test_list_inboxes_returns_json():
    tool = AgentMailListInboxesTool(client=_fake_client())
    out = tool.invoke({"limit": 5})
    assert '"count": 0' in out
    tool.sdk.inboxes.list.assert_called_once_with(limit=5)


def test_send_requires_body():
    tool = AgentMailSendTool(client=_fake_client())
    out = tool.invoke({"inbox_id": "ib", "to": "a@b.com", "subject": "hi"})
    assert out.startswith("Error:")
    tool.sdk.inboxes.messages.send.assert_not_called()


def test_send_happy_path():
    client = _fake_client()
    tool = AgentMailSendTool(client=client)
    out = tool.invoke(
        {
            "inbox_id": "ib",
            "to": ["a@b.com"],
            "subject": "hi",
            "text": "body",
        }
    )
    assert '"message_id": "m_2"' in out
    client.sdk.inboxes.messages.send.assert_called_once()
    call_kwargs = client.sdk.inboxes.messages.send.call_args.kwargs
    assert call_kwargs["inbox_id"] == "ib"
    assert call_kwargs["to"] == ["a@b.com"]
    assert call_kwargs["text"] == "body"


def test_reply_passes_message_id():
    client = _fake_client()
    tool = AgentMailReplyTool(client=client)
    out = tool.invoke({"inbox_id": "ib", "message_id": "m_1", "text": "thanks", "reply_all": True})
    assert '"thread_id": "t_1"' in out
    call_kwargs = client.sdk.inboxes.messages.reply.call_args.kwargs
    assert call_kwargs["reply_all"] is True


def test_toolkit_wires_shared_client():
    client = _fake_client()
    tools = AgentMailToolkit(client=client).get_tools()
    assert len(tools) >= 9
    assert all(t.client is client for t in tools)
    names = {t.name for t in tools}
    assert {
        "agentmail_list_inboxes",
        "agentmail_send_message",
        "agentmail_reply_to_message",
    } <= names


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("AGENTMAIL_API_KEY", raising=False)
    with pytest.raises(ValueError, match="AGENTMAIL_API_KEY"):
        AgentMailClient()
