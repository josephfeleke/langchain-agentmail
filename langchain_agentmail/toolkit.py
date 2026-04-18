"""AgentMailToolkit — hands an agent every AgentMail tool at once."""

from __future__ import annotations

from typing import List, Optional

from langchain_core.tools import BaseTool, BaseToolkit
from pydantic import Field

from langchain_agentmail.client import AgentMailClient
from langchain_agentmail.tools import (
    AgentMailCreateInboxTool,
    AgentMailGetMessageTool,
    AgentMailGetThreadTool,
    AgentMailListInboxesTool,
    AgentMailListMessagesTool,
    AgentMailListThreadsTool,
    AgentMailReplyTool,
    AgentMailSendTool,
    AgentMailUpdateMessageLabelsTool,
)

_ALL_TOOL_CLASSES = [
    AgentMailListInboxesTool,
    AgentMailCreateInboxTool,
    AgentMailListThreadsTool,
    AgentMailGetThreadTool,
    AgentMailListMessagesTool,
    AgentMailGetMessageTool,
    AgentMailSendTool,
    AgentMailReplyTool,
    AgentMailUpdateMessageLabelsTool,
]


class AgentMailToolkit(BaseToolkit):
    """Bundle of AgentMail tools wired to a single shared client."""

    client: AgentMailClient = Field(default_factory=AgentMailClient)
    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def from_api_key(
        cls,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> "AgentMailToolkit":
        return cls(client=AgentMailClient(api_key=api_key, base_url=base_url))

    def get_tools(self) -> List[BaseTool]:
        return [cls(client=self.client) for cls in _ALL_TOOL_CLASSES]
