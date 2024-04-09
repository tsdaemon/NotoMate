import os

import chainlit as cl
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable, RunnableConfig

from noto_mate.agent import agent_executor as notion_agent_executor

ALLOWED_USERNAME = os.environ.get("CHAINLIT_ALLOWED_USERNAME")
if ALLOWED_USERNAME:
    print(f"Allowed username: {ALLOWED_USERNAME}")

    @cl.oauth_callback
    def auth_callback(
        provider_id: str, token: str, raw_user_data: dict[str, str], default_app_user: cl.User
    ) -> cl.User | None:
        if provider_id == "github" and default_app_user.identifier == ALLOWED_USERNAME:
            return default_app_user
        return None


@cl.on_chat_start
async def on_chat_start() -> None:
    cl.user_session.set("agent", notion_agent_executor)
    cl.user_session.set("messages", [])

    await cl.Avatar(
        name="NotoMate",
        url="public/avatar.png",
    ).send()


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
