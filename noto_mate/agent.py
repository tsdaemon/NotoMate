from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_openai.chat_models import ChatOpenAI

from noto_mate.tools.notion import tools as notion_tools

tools: list = notion_tools
llm = ChatOpenAI(temperature=0.1, streaming=True, model="gpt-4-0125-preview")
assistant_system_message = """
You are a helpful agent which helps a user to manage his Notion API.

Greet the user in the first message. Answer in Ukrainian, informally.
"""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", assistant_system_message),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Create the agent chain
agent: Runnable = create_openai_tools_agent(llm, tools, prompt)
# Create the chain executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)  # type: ignore
