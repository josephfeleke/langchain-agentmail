"""LangChain integration for AgentMail."""

from langchain_agentmail._version import __version__
from langchain_agentmail.client import AgentMailClient
from langchain_agentmail.toolkit import AgentMailToolkit
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

__all__ = [
    "AgentMailClient",
    "AgentMailCreateDraftTool",
    "AgentMailCreateInboxTool",
    "AgentMailDeleteDraftTool",
    "AgentMailGetMessageTool",
    "AgentMailGetThreadTool",
    "AgentMailListInboxesTool",
    "AgentMailListMessagesTool",
    "AgentMailListThreadsTool",
    "AgentMailReplyTool",
    "AgentMailSendDraftTool",
    "AgentMailSendTool",
    "AgentMailToolkit",
    "AgentMailUpdateDraftTool",
    "AgentMailUpdateMessageLabelsTool",
    "__version__",
]
