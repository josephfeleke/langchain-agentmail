"""Draft tool tests — mock the SDK and verify args pass through correctly."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from langchain_agentmail import (
    AgentMailClient,
    AgentMailCreateDraftTool,
    AgentMailDeleteDraftTool,
    AgentMailSendDraftTool,
    AgentMailToolkit,
    AgentMailUpdateDraftTool,
)


def _fake_client() -> AgentMailClient:
    sdk = SimpleNamespace(
        inboxes=SimpleNamespace(
            drafts=SimpleNamespace(
                create=MagicMock(return_value={"draft_id": "d_1"}),
                update=MagicMock(return_value={"draft_id": "d_1", "subject": "v2"}),
                send=MagicMock(return_value={"message_id": "m_9", "thread_id": "t_1"}),
                delete=MagicMock(return_value=None),
            ),
            messages=SimpleNamespace(),
        ),
        threads=SimpleNamespace(),
    )
    return AgentMailClient(client=sdk)


def test_create_draft_passes_only_provided_fields():
    client = _fake_client()
    tool = AgentMailCreateDraftTool(client=client)
    out = tool.invoke(
        {
            "inbox_id": "ib_1",
            "to": ["alice@example.com"],
            "subject": "Hello",
            "text": "Body",
        }
    )
    assert '"draft_id": "d_1"' in out
    call_kwargs = client.sdk.inboxes.drafts.create.call_args.kwargs
    assert call_kwargs["inbox_id"] == "ib_1"
    assert call_kwargs["to"] == ["alice@example.com"]
    assert "cc" not in call_kwargs


def test_update_draft_ignores_untouched_fields():
    client = _fake_client()
    tool = AgentMailUpdateDraftTool(client=client)
    tool.invoke({"inbox_id": "ib", "draft_id": "d_1", "subject": "v2"})
    call_kwargs = client.sdk.inboxes.drafts.update.call_args.kwargs
    assert call_kwargs == {"inbox_id": "ib", "draft_id": "d_1", "subject": "v2"}


def test_send_draft_returns_message_and_thread_ids():
    client = _fake_client()
    tool = AgentMailSendDraftTool(client=client)
    out = tool.invoke({"inbox_id": "ib", "draft_id": "d_1"})
    assert '"message_id": "m_9"' in out
    assert '"thread_id": "t_1"' in out


def test_delete_draft_handles_empty_response():
    client = _fake_client()
    tool = AgentMailDeleteDraftTool(client=client)
    out = tool.invoke({"inbox_id": "ib", "draft_id": "d_1"})
    assert '"deleted": true' in out


def test_toolkit_includes_draft_tools():
    client = _fake_client()
    names = {t.name for t in AgentMailToolkit(client=client).get_tools()}
    assert {
        "agentmail_create_draft",
        "agentmail_update_draft",
        "agentmail_send_draft",
        "agentmail_delete_draft",
    } <= names
