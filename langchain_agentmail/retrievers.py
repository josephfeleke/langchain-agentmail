"""LangChain retriever that searches an AgentMail inbox by keyword.

AgentMail does not ship a server-side search endpoint yet. This retriever
hits `sdk.inboxes.messages.list`, pulls each message's full body via
`sdk.inboxes.messages.get`, and then scores results in-process with a simple
case-insensitive substring match.

For semantic search, combine `AgentMailLoader` with a vector store — this
retriever is the "just give me recent messages matching X" escape hatch.
"""

from __future__ import annotations

from typing import Any

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict, Field

from langchain_agentmail.client import AgentMailClient
from langchain_agentmail.loaders import AgentMailLoader


class AgentMailRetriever(BaseRetriever):
    """Keyword retriever over an AgentMail inbox.

    Not semantic — consumers who need embeddings should pipe
    `AgentMailLoader().load()` into their own vector store.
    """

    client: AgentMailClient = Field(default_factory=AgentMailClient)
    inbox_id: str
    k: int = 5
    labels: list[str] | None = None
    scan_limit: int = 50

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        loader = AgentMailLoader(
            inbox_id=self.inbox_id,
            client=self.client,
            labels=self.labels,
            limit=self.scan_limit,
        )
        candidates = loader.load()
        scored = [(_score(doc, query), doc) for doc in candidates]
        scored.sort(key=lambda s: s[0], reverse=True)
        return [doc for score, doc in scored[: self.k] if score > 0]


def _score(doc: Document, query: str) -> int:
    """Count case-insensitive substring hits across body + subject + senders.

    Coarse — good enough for "did the agent get an email about X?" queries."""
    if not query:
        return 0
    q = query.lower()
    body = (doc.page_content or "").lower()
    subject = str(doc.metadata.get("subject") or "").lower()
    senders = str(doc.metadata.get("from") or "").lower()

    return _count(body, q) + (2 * _count(subject, q)) + _count(senders, q)


def _count(haystack: str, needle: str) -> int:
    if not needle:
        return 0
    count = 0
    start = 0
    while True:
        idx = haystack.find(needle, start)
        if idx == -1:
            return count
        count += 1
        start = idx + len(needle)


__all__ = ["AgentMailRetriever", "_score"]


# Silence mypy about the unused arg type.
_ = Any
