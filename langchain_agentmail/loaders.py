"""LangChain document loaders for AgentMail inboxes."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from langchain_agentmail.client import AgentMailClient


class AgentMailLoader(BaseLoader):
    """Load messages from an AgentMail inbox as LangChain `Document`s.

    Each message becomes one `Document`. `page_content` is the plain-text body
    (preferring the SDK's `extracted_text`, which strips quoted history).
    Attachment metadata (filename / size / id) is placed in
    `metadata["attachments"]` — use `AgentMailGetAttachmentTool` to download
    the bytes when you need them.
    """

    def __init__(
        self,
        inbox_id: str,
        *,
        client: AgentMailClient | None = None,
        labels: list[str] | None = None,
        limit: int | None = None,
        include_attachments: bool = True,
    ) -> None:
        self.client = client or AgentMailClient()
        self.inbox_id = inbox_id
        self.labels = labels
        self.limit = limit
        self.include_attachments = include_attachments

    def lazy_load(self) -> Iterator[Document]:
        sdk = self.client.sdk
        fetched = 0
        page_token: str | None = None

        while True:
            kwargs: dict[str, Any] = {}
            if self.labels is not None:
                kwargs["labels"] = self.labels
            if page_token is not None:
                kwargs["page_token"] = page_token

            resp = sdk.inboxes.messages.list(inbox_id=self.inbox_id, **kwargs)
            items = _attr(resp, "messages", []) or []
            if not items:
                return

            for item in items:
                if self.limit is not None and fetched >= self.limit:
                    return
                full = sdk.inboxes.messages.get(
                    inbox_id=self.inbox_id,
                    message_id=_attr(item, "message_id"),
                )
                yield _to_document(full, self.inbox_id, self.include_attachments)
                fetched += 1

            page_token = _attr(resp, "next_page_token")
            if not page_token:
                return

    def load(self) -> list[Document]:
        return list(self.lazy_load())


def _attr(obj: Any, name: str, default: Any = None) -> Any:
    """Read a field off a pydantic model or a dict; return default if absent."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _to_document(msg: Any, inbox_id: str, include_attachments: bool) -> Document:
    text = _attr(msg, "extracted_text") or _attr(msg, "text") or ""
    attachments = _attr(msg, "attachments") or []
    attachment_meta = (
        [
            {
                "attachment_id": _attr(a, "attachment_id"),
                "filename": _attr(a, "filename"),
                "content_type": _attr(a, "content_type"),
                "size": _attr(a, "size"),
            }
            for a in attachments
        ]
        if include_attachments
        else []
    )

    metadata: dict[str, Any] = {
        "inbox_id": inbox_id,
        "message_id": _attr(msg, "message_id"),
        "thread_id": _attr(msg, "thread_id"),
        "from": _attr(msg, "from") or _attr(msg, "from_"),
        "to": _attr(msg, "to"),
        "cc": _attr(msg, "cc"),
        "subject": _attr(msg, "subject"),
        "labels": _attr(msg, "labels"),
        "timestamp": _attr(msg, "timestamp"),
        "has_attachments": bool(attachments),
        "attachments": attachment_meta,
    }
    # Drop None values so downstream filters don't blow up.
    metadata = {k: v for k, v in metadata.items() if v is not None}
    return Document(page_content=text, metadata=metadata)
