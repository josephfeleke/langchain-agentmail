"""LangChain integration for AgentMail."""

from langchain_agentmail._version import __version__
from langchain_agentmail.client import AgentMailClient
from langchain_agentmail.toolkit import AgentMailToolkit
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

__all__ = [
    "AgentMailClient",
    "AgentMailCreateInboxTool",
    "AgentMailGetMessageTool",
    "AgentMailGetThreadTool",
    "AgentMailListInboxesTool",
    "AgentMailListMessagesTool",
    "AgentMailListThreadsTool",
    "AgentMailReplyTool",
    "AgentMailSendTool",
    "AgentMailToolkit",
    "AgentMailUpdateMessageLabelsTool",
    "__version__",
]
