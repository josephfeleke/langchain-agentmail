"""LangChain integration for AgentMail."""

from langchain_agentmail._version import __version__
from langchain_agentmail.client import AgentMailClient
from langchain_agentmail.toolkit import AgentMailToolkit
from langchain_agentmail.tools import (
    AgentMailCreateDraftTool,
    AgentMailCreateInboxTool,
    AgentMailDeleteDraftTool,
    AgentMailGetAttachmentTool,
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
from langchain_agentmail.tools.schemas import SendAttachmentSpec

__all__ = [
    "AgentMailClient",
    "AgentMailCreateDraftTool",
    "AgentMailCreateInboxTool",
    "AgentMailDeleteDraftTool",
    "AgentMailGetAttachmentTool",
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
    "SendAttachmentSpec",
    "__version__",
]
