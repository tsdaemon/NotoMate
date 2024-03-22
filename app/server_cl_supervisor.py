import chainlit as cl
from langchain.agents import AgentExecutor
from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig

from app.graph import graph


@cl.on_chat_start
async def on_chat_start() -> None:
    cl.user_session.set("agent", graph)
    cl.user_session.set("history", [])


@cl.on_message
async def main(message: cl.Message) -> None:
    agent: AgentExecutor | None = cl.user_session.get("agent")
    history = cl.user_session.get("history")
    if agent is None:
        raise ValueError("Agent is not set")
    if history is None:
        raise ValueError("History is not set")

    history.append(HumanMessage(content=message.content))

    res = await agent.ainvoke(
        input={"messages": history},
        config=RunnableConfig(callbacks=[cl.AsyncLangchainCallbackHandler()]),
    )

    await cl.Message(content=res["messages"][-1].content).send()
    cl.user_session.set("history", res["messages"])
