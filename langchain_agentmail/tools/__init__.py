"""LangChain tools backed by the AgentMail API."""

from langchain_agentmail.tools.attachments import AgentMailGetAttachmentTool
from langchain_agentmail.tools.drafts import (
    AgentMailCreateDraftTool,
    AgentMailDeleteDraftTool,
    AgentMailSendDraftTool,
    AgentMailUpdateDraftTool,
)
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
    "AgentMailUpdateDraftTool",
    "AgentMailUpdateMessageLabelsTool",
]
