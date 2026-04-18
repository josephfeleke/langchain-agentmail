"""Minimal triage agent: reads unread mail and replies when asked.

Usage:
    export OPENAI_API_KEY=...
    export AGENTMAIL_API_KEY=...
    python examples/triage_agent.py
"""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from langchain_agentmail import AgentMailToolkit


def main() -> None:
    toolkit = AgentMailToolkit.from_api_key()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    agent = create_react_agent(
        llm,
        tools=toolkit.get_tools(),
        prompt=(
            "You are an email assistant with an AgentMail inbox. "
            "When asked to check mail, list recent threads, read the newest "
            "one, and summarize it. When asked to reply, draft a short, "
            "professional response and send it with agentmail_reply_to_message."
        ),
    )

    result = agent.invoke(
        {
            "messages": [
                (
                    "user",
                    "Check my inbox for anything new. Summarize the most "
                    "recent thread in 2 sentences.",
                )
            ]
        }
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
