"""AgentMailToolkit — hands an agent every AgentMail tool at once."""

from __future__ import annotations

from langchain_core.tools import BaseTool, BaseToolkit
from pydantic import ConfigDict, Field

from langchain_agentmail.client import AgentMailClient
from langchain_agentmail.tools import (
    AgentMailCreateDraftTool,
    AgentMailCreateInboxTool,
    AgentMailDeleteDraftTool,
    AgentMailGetMessageTool,
    AgentMailGetThreadTool,
    AgentMailListInboxesTool,
    AgentMailListMessagesTool,
    AgentMailListThreadsTool,
    AgentMailReplyTool,
    AgentMailSendDraftTool,
    AgentMailSendTool,
    AgentMailUpdateDraftTool,
    AgentMailUpdateMessageLabelsTool,
)

_ALL_TOOL_CLASSES: list[type[BaseTool]] = [
    AgentMailListInboxesTool,
    AgentMailCreateInboxTool,
    AgentMailListThreadsTool,
    AgentMailGetThreadTool,
    AgentMailListMessagesTool,
    AgentMailGetMessageTool,
    AgentMailSendTool,
    AgentMailReplyTool,
    AgentMailUpdateMessageLabelsTool,
    AgentMailCreateDraftTool,
    AgentMailUpdateDraftTool,
    AgentMailSendDraftTool,
    AgentMailDeleteDraftTool,
]


class AgentMailToolkit(BaseToolkit):
    """Bundle of AgentMail tools wired to a single shared client."""

    client: AgentMailClient = Field(default_factory=AgentMailClient)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_api_key(
        cls,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> AgentMailToolkit:
        return cls(client=AgentMailClient(api_key=api_key, base_url=base_url))

    def get_tools(self) -> list[BaseTool]:
        return [cls(client=self.client) for cls in _ALL_TOOL_CLASSES]
