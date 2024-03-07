import os
from typing import Any

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai.chat_models import ChatOpenAI
from notion_client import Client

from app.tools.notion import GetNotionPageContent, SearchMyNotion

# Create tools
notion_client = Client(auth=os.environ["NOTION_API_KEY"])
search_tool = SearchMyNotion(client=notion_client)
page_content_tool = GetNotionPageContent(client=notion_client)
tools = [search_tool, page_content_tool]

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
