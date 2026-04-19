# Changelog

All notable changes to `langchain-agentmail` are documented in this file. The
format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this project adheres to [Semantic Versioning](https://semver.org/).

## 0.2.0

### Added

- **Async support** — every tool now has an `_arun` implementation backed by
  `asyncio.to_thread`, so LangGraph and other async agents can run tools
  concurrently without blocking the event loop.
- **Draft tools** — four new tools covering the full compose-and-ship lifecycle:
  `agentmail_create_draft`, `agentmail_update_draft`, `agentmail_send_draft`,
  `agentmail_delete_draft`. Supports scheduled delivery via `send_at`.
- **Attachments** — `SendAttachmentSpec` model plus attachment fields on
  send / reply / draft-create tools (base64 or URL). New
  `AgentMailGetAttachmentTool` fetches presigned download URLs.
- **`AgentMailLoader`** — a `BaseLoader` that streams inbox messages as
  `Document`s, with standard email metadata keys.
- **`AgentMailRetriever`** — a keyword `BaseRetriever` over the loader;
  substring scoring weighted 2× for subject hits. For semantic search, combine
  the loader with your own vector store.
- **Webhooks subpackage** (`langchain_agentmail.webhooks`) — pydantic event
  models, pure-stdlib svix signature verification, and an optional FastAPI
  router factory. Install with `pip install 'langchain-agentmail[webhooks]'`.
- **Packaging & CI** — switched build backend to hatchling, added `uv` dev
  flow, ruff + mypy configs, and a GitHub Actions matrix (py3.10–3.13)
  running lint + type-check + unit tests on every PR.
- **Release automation** — `release.yml` publishes to PyPI via Trusted
  Publisher OIDC on a manual `workflow_dispatch`.

### Changed

- Dropped Python 3.9 support; floor is now 3.10.
- `_format` helper and `Addresses` union extracted into shared modules so
  tool files stay focused on SDK calls.
- `model_config` fields switched from dict literals to `ConfigDict(...)` for
  pydantic v2 correctness.
- `_version.py` is now the actual single source of truth — `pyproject.toml`
  reads it via `[tool.hatch.version]`.

### Added (dev)

- `langchain_agentmail/py.typed` marker ships in the wheel for PEP 561
  downstream type checking.

## 0.1.0

Initial release. Nine tools + `AgentMailToolkit` wrapping the AgentMail SDK.
