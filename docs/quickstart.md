# Quickstart

End-to-end walkthrough: create an inbox, send a message, triage inbound email
with a LangGraph agent, and close the loop via webhooks.

## 1. Install

```bash
pip install 'langchain-agentmail[webhooks]' langchain-openai langgraph
```

Set your keys:

```bash
export AGENTMAIL_API_KEY=am_live_...
export OPENAI_API_KEY=sk-...
```

## 2. Create an inbox, send an email

```python
from langchain_agentmail import AgentMailClient

client = AgentMailClient()  # reads AGENTMAIL_API_KEY

inbox = client.sdk.inboxes.create(display_name="Support Bot")
print("Inbox:", inbox.email, inbox.inbox_id)

client.sdk.inboxes.messages.send(
    inbox_id=inbox.inbox_id,
    to="your-personal-email@gmail.com",
    subject="Hello from a LangChain agent",
    text="Reply to this message to trigger the demo.",
)
```

## 3. Build a triage agent

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_agentmail import AgentMailToolkit

toolkit = AgentMailToolkit.from_api_key()
agent = create_react_agent(
    ChatOpenAI(model="gpt-4o-mini"),
    tools=toolkit.get_tools(),
    prompt=(
        "You are a support triage assistant with an AgentMail inbox. "
        "When asked to check mail, list recent threads, summarize them, and "
        "reply to anything that looks actionable."
    ),
)

result = agent.invoke(
    {"messages": [("user", "Summarize my three newest threads.")]}
)
print(result["messages"][-1].content)
```

## 4. Retrieve email by keyword

```python
from langchain_agentmail import AgentMailRetriever

hits = AgentMailRetriever(inbox_id=inbox.inbox_id, k=5).invoke("invoice")
for doc in hits:
    print(doc.metadata["subject"], "—", doc.page_content[:80])
```

For semantic search, feed `AgentMailLoader(...).load()` into your vector
store; this retriever is a keyword-only escape hatch.

## 5. React to inbound email via webhooks

In `app.py`:

```python
from fastapi import FastAPI
from langchain_agentmail.webhooks import AgentMailEvent, create_fastapi_router

async def on_event(event: AgentMailEvent) -> None:
    if event.event_type != "message.received":
        return
    msg = event.message
    # Kick off your agent with the new message here.
    print(f"New mail: {msg.get('subject')!r} from {msg.get('from')}")

app = FastAPI()
app.include_router(create_fastapi_router(on_event), prefix="/agentmail")
```

Run:

```bash
export AGENTMAIL_WEBHOOK_SECRET=whsec_...
uvicorn app:app --port 8000
```

Expose the port to the public internet (ngrok works locally), register the
URL as an AgentMail webhook, and your handler will fire on every inbound
message — signature-verified automatically.

## Next steps

- **Drafts** — `agentmail_create_draft` + `agentmail_send_draft` for
  compose-review-send flows, including scheduled delivery via `send_at`.
- **Attachments** — `AgentMailSendTool` accepts
  `attachments=[SendAttachmentSpec(...)]`; `AgentMailGetAttachmentTool`
  downloads inbound files via presigned URL.
- **Labels** — `agentmail_update_message_labels` for custom workflow
  states (e.g. `needs_review`, `archived`).
