"""Tests for AgentMailLoader and AgentMailRetriever."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from langchain_agentmail import AgentMailClient, AgentMailLoader, AgentMailRetriever


def _messages_sdk(messages: list[dict], full_by_id: dict[str, dict]) -> AgentMailClient:
    sdk = SimpleNamespace(
        inboxes=SimpleNamespace(
            messages=SimpleNamespace(
                list=MagicMock(return_value={"messages": messages, "count": len(messages)}),
                get=MagicMock(side_effect=lambda inbox_id, message_id: full_by_id[message_id]),
            ),
        ),
    )
    return AgentMailClient(client=sdk)


def test_loader_yields_documents_with_metadata():
    client = _messages_sdk(
        messages=[
            {"message_id": "m_1", "subject": "hi", "from": "a@b.com"},
            {"message_id": "m_2", "subject": "bye", "from": "c@d.com"},
        ],
        full_by_id={
            "m_1": {
                "message_id": "m_1",
                "thread_id": "t_1",
                "subject": "hi",
                "from": "a@b.com",
                "to": ["me@x.io"],
                "labels": ["inbox"],
                "extracted_text": "hello world",
                "attachments": [],
            },
            "m_2": {
                "message_id": "m_2",
                "thread_id": "t_2",
                "subject": "bye",
                "from": "c@d.com",
                "to": ["me@x.io"],
                "labels": ["inbox"],
                "text": "goodbye world",
                "attachments": [
                    {
                        "attachment_id": "a_1",
                        "filename": "r.pdf",
                        "content_type": "application/pdf",
                        "size": 123,
                    }
                ],
            },
        },
    )
    docs = AgentMailLoader(inbox_id="ib_1", client=client).load()
    assert len(docs) == 2
    assert docs[0].page_content == "hello world"
    assert docs[0].metadata["message_id"] == "m_1"
    assert docs[0].metadata["from"] == "a@b.com"
    assert docs[0].metadata["has_attachments"] is False
    assert docs[1].metadata["has_attachments"] is True
    assert docs[1].metadata["attachments"][0]["filename"] == "r.pdf"


def test_loader_respects_limit():
    client = _messages_sdk(
        messages=[{"message_id": f"m_{i}"} for i in range(5)],
        full_by_id={f"m_{i}": {"message_id": f"m_{i}", "text": "x"} for i in range(5)},
    )
    docs = AgentMailLoader(inbox_id="ib", client=client, limit=2).load()
    assert len(docs) == 2


def test_retriever_ranks_subject_hits_highest():
    client = _messages_sdk(
        messages=[
            {"message_id": "m_1"},
            {"message_id": "m_2"},
            {"message_id": "m_3"},
        ],
        full_by_id={
            "m_1": {"message_id": "m_1", "subject": "invoice", "text": "see attached"},
            "m_2": {"message_id": "m_2", "subject": "hello", "text": "invoice inside"},
            "m_3": {"message_id": "m_3", "subject": "spam", "text": "no match"},
        },
    )
    retriever = AgentMailRetriever(inbox_id="ib", client=client, k=2)
    docs = retriever.invoke("invoice")
    assert len(docs) == 2
    assert docs[0].metadata["message_id"] == "m_1"  # subject hit outranks body hit
    assert docs[1].metadata["message_id"] == "m_2"


def test_retriever_drops_zero_score_results():
    client = _messages_sdk(
        messages=[{"message_id": "m_1"}],
        full_by_id={"m_1": {"message_id": "m_1", "subject": "irrelevant", "text": "nothing"}},
    )
    retriever = AgentMailRetriever(inbox_id="ib", client=client, k=5)
    docs = retriever.invoke("invoice")
    assert docs == []
