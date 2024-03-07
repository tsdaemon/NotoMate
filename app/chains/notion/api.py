import os
from typing import Any

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai.chat_models import ChatOpenAI
from notion_client import Client

notion_client = Client(auth=os.environ["NOTION_API_KEY"])


class SearchMyNotionInput(BaseModel):
    """Input for the Notion search tool."""

    query: str = Field(description="Search query to look up")
    sort_last_editing_time: bool = Field(description="Show the most recently edited documents first.", default=True)
    start_cursor: str | None = Field(
        description="A cursor value returned in a previous response that If supplied, limits the response to results "
        "starting after the cursor. If not supplied, then the first page of results is returned. "
    )
    page_size: int = Field(description="The number of documents to return", max=100, default=10)


@tool(args_schema=SearchMyNotionInput)
def search_my_notion(
    query: str, sort_last_editing_time: bool = True, page_size: int = 10, start_cursor: str | None = None
) -> dict:
    """Search over documents in Notion workspace.
    If the user is asking to search something in his notes, you can use this tool.
    If an error occurs, show to user all debug information.
    """
    return notion_client.search(
        query=query,
        sort={
            "direction": "descending" if sort_last_editing_time else "ascending",
            "timestamp": "last_edited_time",
        },
        start_cursor=start_cursor,
        page_size=page_size,
    )  # type: ignore


class GetNotionPageContentInput(BaseModel):
    """Notion page id input."""

    page_id: str = Field(description="Page id to get content from.")
    start_cursor: str | None = Field(
        description="If supplied, this endpoint will return a page of results starting after the cursor provided. "
        "If not supplied, this endpoint will return the first page of results."
    )


@tool(args_schema=GetNotionPageContentInput)
def get_notion_page_content(page_id: str, start_cursor: str | None = None) -> dict:
    """Get a page content in Notion workspace.
    If the user is asking to get some content from his notes, you can use this tool.
    If an error occurs, show to user all debug information."""
    return notion_client.blocks.children.list(page_id, start_cursor=start_cursor, page_size=10)  # type: ignore


# Create tools
tools = [search_my_notion, get_notion_page_content]

# Create LLM
llm = ChatOpenAI(temperature=0, streaming=True)
assistant_system_message = """Ти помічник і можеш використовувати інструменти, щоб найкраще
відповісти на питання користувача."""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", assistant_system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
llm_with_tools = llm.bind(functions=[convert_to_openai_function(t) for t in tools])


# Create the chain
def _format_chat_history(chat_history: list[tuple[str, str]]) -> list[BaseMessage]:
    buffer: list[BaseMessage] = []
    for human, ai in chat_history:
        buffer.append(HumanMessage(content=human))
        buffer.append(AIMessage(content=ai))
    return buffer


agent: Any = (
    {
        "input": lambda x: x["input"],
        "chat_history": lambda x: _format_chat_history(x["chat_history"]),
        "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
    }
    | prompt
    | llm_with_tools
    | OpenAIFunctionsAgentOutputParser()
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
