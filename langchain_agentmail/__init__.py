"""LangChain integration for AgentMail."""

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
    "AgentMailToolkit",
    "AgentMailCreateInboxTool",
    "AgentMailGetMessageTool",
    "AgentMailGetThreadTool",
    "AgentMailListInboxesTool",
    "AgentMailListMessagesTool",
    "AgentMailListThreadsTool",
    "AgentMailReplyTool",
    "AgentMailSendTool",
    "AgentMailUpdateMessageLabelsTool",
]

__version__ = "0.1.0"
