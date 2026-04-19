"""Shared pydantic input types used by multiple tool modules.

Centralized so `messages.py`, `drafts.py`, and future tool files can reuse the
same `Addresses` union without redeclaring it — keeps the schema identical
across send, reply, draft-create, and draft-update surfaces.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

Addresses = str | list[str]


class SendAttachmentSpec(BaseModel):
    """One outbound attachment.

    Exactly one of `content` (base64-encoded bytes) or `url` (a fetchable URL)
    must be set. `content_disposition` defaults to "attachment"; use "inline"
    with a matching `content_id` to embed the file in HTML (e.g. `<img
    src="cid:logo">`).
    """

    filename: str | None = Field(
        default=None,
        description="Filename shown to the recipient (e.g. 'report.pdf').",
    )
    content_type: str | None = Field(
        default=None,
        description="MIME type (e.g. 'application/pdf'). Inferred from filename if omitted.",
    )
    content: str | None = Field(
        default=None,
        description="Base64-encoded file bytes. Mutually exclusive with `url`.",
    )
    url: str | None = Field(
        default=None,
        description="Public URL the mail server should fetch. Mutually exclusive with `content`.",
    )
    content_disposition: str | None = Field(
        default=None,
        description="'attachment' (default) or 'inline' for embedded images.",
    )
    content_id: str | None = Field(
        default=None,
        description="Referenced as `cid:<content_id>` in HTML when inline.",
    )
