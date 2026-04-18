"""Smallest possible example: send one email through an AgentMail inbox."""

import os

from langchain_agentmail import AgentMailClient, AgentMailSendTool


def main() -> None:
    client = AgentMailClient()
    inbox_id = os.environ["AGENTMAIL_INBOX_ID"]
    to_addr = os.environ["TO_EMAIL"]

    tool = AgentMailSendTool(client=client)
    result = tool.invoke(
        {
            "inbox_id": inbox_id,
            "to": to_addr,
            "subject": "Hello from LangChain",
            "text": "This message was sent through langchain-agentmail.",
        }
    )
    print(result)


if __name__ == "__main__":
    main()
