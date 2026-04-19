"""Minimal FastAPI server that logs each inbound AgentMail event.

Run with:

    export AGENTMAIL_WEBHOOK_SECRET=whsec_...
    uvicorn examples.webhook_server:app --port 8000

Then point an AgentMail webhook at http://<your-host>:8000/agentmail
(ngrok works during local testing).
"""

from __future__ import annotations

from fastapi import FastAPI

from langchain_agentmail.webhooks import AgentMailEvent, create_fastapi_router

app = FastAPI()


async def handle_event(event: AgentMailEvent) -> None:
    if event.event_type == "message.received":
        msg = event.message
        print(
            f"[received] {msg.get('subject', '(no subject)')} "
            f"from {msg.get('from')} → {msg.get('to')}"
        )
    else:
        print(f"[{event.event_type}] event_id={event.event_id}")


app.include_router(create_fastapi_router(handle_event), prefix="/agentmail")
