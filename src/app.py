import chainlit as cl
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable, RunnableConfig

from src.agent import agent_executor as notion_agent_executor


@cl.on_chat_start
async def on_chat_start() -> None:
    cl.user_session.set("agent", notion_agent_executor)
    cl.user_session.set("messages", [])


@cl.on_message
async def on_message(input: cl.Message) -> None:
    agent: Runnable = cl.user_session.get("agent")  # type: ignore
    messages: list = cl.user_session.get("messages")  # type: ignore
    messages.append(HumanMessage(content=input.content))

    response = cl.Message(content="")
    ai_message_str = ""

    async for event in agent.astream_events(
        {"messages": messages},
        version="v1",
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            await response.stream_token(content)
            ai_message_str += content

    await response.send()
    messages.append(AIMessage(content=ai_message_str))
