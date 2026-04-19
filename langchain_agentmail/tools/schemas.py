"""Shared pydantic input types used by multiple tool modules.

Centralized so `messages.py`, `drafts.py`, and future tool files can reuse the
same `Addresses` union without redeclaring it — keeps the schema identical
across send, reply, draft-create, and draft-update surfaces.
"""

from __future__ import annotations

Addresses = str | list[str]
