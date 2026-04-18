"""LangChain tools backed by the AgentMail API."""

from langchain_agentmail.tools.inboxes import (
    AgentMailCreateInboxTool,
    AgentMailListInboxesTool,
)
from langchain_agentmail.tools.messages import (
    AgentMailGetMessageTool,
    AgentMailListMessagesTool,
    AgentMailReplyTool,
    AgentMailSendTool,
    AgentMailUpdateMessageLabelsTool,
)
from langchain_agentmail.tools.threads import (
    AgentMailGetThreadTool,
    AgentMailListThreadsTool,
)

__all__ = [
    "AgentMailCreateInboxTool",
    "AgentMailListInboxesTool",
    "AgentMailGetMessageTool",
    "AgentMailListMessagesTool",
    "AgentMailReplyTool",
    "AgentMailSendTool",
    "AgentMailUpdateMessageLabelsTool",
    "AgentMailGetThreadTool",
    "AgentMailListThreadsTool",
]
