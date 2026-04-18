"""Thin wrapper around the AgentMail SDK used by every tool in the package.

The real work happens in the `agentmail` SDK. This wrapper exists so that:

  1. Tools can accept a pre-built client (for tests / dependency injection).
  2. We centralize the `AGENTMAIL_API_KEY` env var lookup in one place.
  3. Callers don't have to care whether they pass an SDK instance or a key.
"""

from __future__ import annotations

import os
from typing import Any, Optional


class AgentMailClient:
    """Adapter that holds an `agentmail.AgentMail` SDK instance."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        client: Optional[Any] = None,
        base_url: Optional[str] = None,
    ) -> None:
        if client is not None:
            self._client = client
            return

        key = api_key or os.environ.get("AGENTMAIL_API_KEY")
        if not key:
            raise ValueError(
                "AgentMail API key not found. Pass `api_key=...` or set the "
                "AGENTMAIL_API_KEY environment variable. Get one at "
                "https://www.agentmail.to/"
            )

        try:
            from agentmail import AgentMail
        except ImportError as e:
            raise ImportError(
                "The `agentmail` package is required. Install with "
                "`pip install agentmail`."
            ) from e

        kwargs: dict[str, Any] = {"api_key": key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = AgentMail(**kwargs)

    @property
    def sdk(self) -> Any:
        """Return the underlying AgentMail SDK instance."""
        return self._client
