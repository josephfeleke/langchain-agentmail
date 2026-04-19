"""Attachment tests — cover outbound serialization and inbound download."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from langchain_agentmail import (
    AgentMailClient,
    AgentMailGetAttachmentTool,
    AgentMailSendTool,
    SendAttachmentSpec,
)


def _fake_client() -> AgentMailClient:
    sdk = SimpleNamespace(
        inboxes=SimpleNamespace(
            messages=SimpleNamespace(
                send=MagicMock(return_value={"message_id": "m_att", "thread_id": "t_1"}),
                get_attachment=MagicMock(
                    return_value={
                        "attachment_id": "a_1",
                        "filename": "report.pdf",
                        "size": 2048,
                        "content_type": "application/pdf",
                        "download_url": "https://example.com/signed",
                        "expires_at": "2026-05-01T00:00:00Z",
                    }
                ),
            ),
        ),
        threads=SimpleNamespace(),
    )
    return AgentMailClient(client=sdk)


def test_send_accepts_typed_attachment_spec():
    client = _fake_client()
    tool = AgentMailSendTool(client=client)
    tool.invoke(
        {
            "inbox_id": "ib",
            "to": "a@b.com",
            "subject": "hi",
            "text": "body",
            "attachments": [
                SendAttachmentSpec(
                    filename="r.pdf",
                    content_type="application/pdf",
                    content="dGVzdA==",
                )
            ],
        }
    )
    kwargs = client.sdk.inboxes.messages.send.call_args.kwargs
    assert kwargs["attachments"] == [
        {
            "filename": "r.pdf",
            "content_type": "application/pdf",
            "content": "dGVzdA==",
        }
    ]


def test_send_accepts_raw_dict_attachment():
    client = _fake_client()
    tool = AgentMailSendTool(client=client)
    tool.invoke(
        {
            "inbox_id": "ib",
            "to": "a@b.com",
            "subject": "hi",
            "text": "body",
            "attachments": [{"filename": "x.png", "url": "https://example.com/x.png"}],
        }
    )
    kwargs = client.sdk.inboxes.messages.send.call_args.kwargs
    assert kwargs["attachments"] == [{"filename": "x.png", "url": "https://example.com/x.png"}]


def test_get_attachment_returns_signed_url():
    client = _fake_client()
    tool = AgentMailGetAttachmentTool(client=client)
    out = tool.invoke({"inbox_id": "ib", "message_id": "m_1", "attachment_id": "a_1"})
    assert '"download_url": "https://example.com/signed"' in out
    client.sdk.inboxes.messages.get_attachment.assert_called_once_with(
        inbox_id="ib", message_id="m_1", attachment_id="a_1"
    )
