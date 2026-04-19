"""Tools for downloading AgentMail message attachments."""

from __future__ import annotations

from pydantic import BaseModel, Field

from langchain_agentmail.tools.base import AgentMailBaseTool, _format_error


class _GetAttachmentInput(BaseModel):
    inbox_id: str = Field(description="Inbox that owns the message.")
    message_id: str = Field(description="Message the attachment belongs to.")
    attachment_id: str = Field(description="Attachment to fetch.")


class AgentMailGetAttachmentTool(AgentMailBaseTool):
    name: str = "agentmail_get_attachment"
    description: str = (
        "Fetch a presigned download URL for a message attachment. The URL "
        "expires, so download promptly or pipe it into a file-storage step. "
        "Returns filename, size, content_type, download_url, and expires_at."
    )
    args_schema: type[BaseModel] = _GetAttachmentInput

    def _run(self, inbox_id: str, message_id: str, attachment_id: str) -> str:
        try:
            resp = self.sdk.inboxes.messages.get_attachment(
                inbox_id=inbox_id,
                message_id=message_id,
                attachment_id=attachment_id,
            )
            return self._format(resp)
        except Exception as e:
            return _format_error(e)
