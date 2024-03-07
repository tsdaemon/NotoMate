import chainlit as cl
from langchain.agents import AgentExecutor
from langchain_core.runnables.config import RunnableConfig

from app.chains.notion.api import agent_executor as notion_agent


@cl.on_chat_start
async def on_chat_start() -> None:
    cl.user_session.set("agent", notion_agent)
    cl.user_session.set("history", [])


@cl.on_message
async def main(message: cl.Message) -> None:
    agent: AgentExecutor | None = cl.user_session.get("agent")
    history = cl.user_session.get("history")
    if agent is None:
        raise ValueError("Agent is not set")
    if history is None:
        raise ValueError("History is not set")

    res = await agent.ainvoke(
        input={"input": message.content, "chat_history": history},
        config=RunnableConfig(callbacks=[cl.AsyncLangchainCallbackHandler()]),
    )

    history.append((message.content, res["output"]))

    await cl.Message(content=res["output"]).send()
