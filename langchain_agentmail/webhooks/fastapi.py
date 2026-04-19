"""FastAPI router factory for AgentMail webhooks.

Keep the FastAPI import here so users who don't install the `webhooks` extra
can still import the rest of the package without failure.
"""

from __future__ import annotations

import os
from collections.abc import Awaitable, Callable
from typing import Any

from langchain_agentmail.webhooks.events import AgentMailEvent, parse_event
from langchain_agentmail.webhooks.verify import (
    InvalidSignatureError,
    verify_signature,
)

EventHandler = Callable[[AgentMailEvent], None | Awaitable[None]]


def create_fastapi_router(
    on_event: EventHandler,
    *,
    secret: str | None = None,
    path: str = "/",
) -> Any:
    """Build a FastAPI router that verifies + parses webhook deliveries.

    Example:

        from fastapi import FastAPI
        from langchain_agentmail.webhooks import create_fastapi_router

        async def handle(event):
            if event.event_type == "message.received":
                ...

        app = FastAPI()
        app.include_router(create_fastapi_router(handle), prefix="/agentmail")
    """
    try:
        from fastapi import APIRouter, HTTPException, Request
    except ImportError as e:  # pragma: no cover - clear upgrade hint
        raise ImportError(
            "FastAPI is required for create_fastapi_router. Install with "
            "`pip install 'langchain-agentmail[webhooks]'`."
        ) from e

    signing_secret = secret or os.environ.get("AGENTMAIL_WEBHOOK_SECRET")
    if not signing_secret:
        raise ValueError(
            "A signing secret is required. Pass `secret=` or set AGENTMAIL_WEBHOOK_SECRET."
        )

    router = APIRouter()

    import inspect

    @router.post(path)
    async def handle_webhook(request: Request) -> dict:
        body = await request.body()
        try:
            verify_signature(
                payload=body,
                secret=signing_secret,
                svix_id=request.headers.get("svix-id", ""),
                svix_timestamp=request.headers.get("svix-timestamp", ""),
                svix_signature=request.headers.get("svix-signature", ""),
            )
        except InvalidSignatureError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e

        try:
            event = parse_event(await request.json())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid payload: {e}") from e

        result = on_event(event)
        if inspect.isawaitable(result):
            await result
        return {"ok": True}

    return router


__all__ = ["EventHandler", "create_fastapi_router"]
