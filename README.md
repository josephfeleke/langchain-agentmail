# langchain-agentmail

LangChain tools for [AgentMail](https://www.agentmail.to/) — give any LangChain
agent its own real email inbox. The agent can create inboxes, triage unread
threads, read messages, and send or reply to email, all through the standard
LangChain tool interface.

## Install

```bash
pip install langchain-agentmail
```

Set your API key:

```bash
export AGENTMAIL_API_KEY=am_live_...
```

Grab a key at [agentmail.to](https://www.agentmail.to/).

## Quick start

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from langchain_agentmail import AgentMailToolkit

toolkit = AgentMailToolkit.from_api_key()
agent = create_react_agent(
    ChatOpenAI(model="gpt-4o-mini"),
    tools=toolkit.get_tools(),
)

result = agent.invoke(
    {"messages": [("user", "Summarize my most recent email thread.")]}
)
print(result["messages"][-1].content)
```

## What the agent can do

| Tool | What it does |
| --- | --- |
| `agentmail_list_inboxes` | Enumerate inboxes the agent owns. |
| `agentmail_create_inbox` | Create a fresh inbox (random or custom username). |
| `agentmail_list_threads` | List threads across inboxes with label / time filters. |
| `agentmail_get_thread` | Pull every message in a thread, text only. |
| `agentmail_list_messages` | List messages in a specific inbox. |
| `agentmail_get_message` | Fetch one message with its full body. |
| `agentmail_send_message` | Send a new email. |
| `agentmail_reply_to_message` | Reply inside the same thread (with optional reply-all). |
| `agentmail_update_message_labels` | Add or remove labels (e.g. archive a message). |

HTML bodies are stripped and long text is truncated before returning to the
model, so a single thread won't eat your whole context window.

## Using individual tools

Every tool works on its own if you don't want the whole toolkit:

```python
from langchain_agentmail import AgentMailClient, AgentMailSendTool

client = AgentMailClient()  # reads AGENTMAIL_API_KEY
send = AgentMailSendTool(client=client)

send.invoke({
    "inbox_id": "ib_...",
    "to": "alice@example.com",
    "subject": "Ping",
    "text": "Hello from my agent.",
})
```

## Examples

- [`examples/triage_agent.py`](examples/triage_agent.py) — a ReAct agent that
  summarizes your newest thread.
- [`examples/send_one_email.py`](examples/send_one_email.py) — the shortest
  possible "send one email" script.

## Development

This repo uses [`uv`](https://docs.astral.sh/uv/) + hatchling.

```bash
uv sync --all-extras --dev
uv run ruff check .
uv run mypy langchain_agentmail
uv run pytest tests/unit_tests -v
```

Unit tests mock the AgentMail SDK, so they don't need a live API key. The CI
matrix runs lint + mypy + pytest on Python 3.10–3.13 for every PR.

## License

MIT.
