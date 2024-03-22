from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

additional_agents = [
    "NotionAPI",
    # "NotionGraphDatabase"
]
system_prompt = """
Ти є асистентом-супервізором, задача якого допомогти користувачеві користуватися Notion.
Для виконання задачі ти можеш використовувати додаткових агентів {additional_agents}.

Звертайся до користвeча неформально, але з повагою. У першому повідомленні привітай користувача по імені: Анатолій.
"""

tool_def = {
    "type": "function",
    "function": {
        "name": "get_info_from_agent",
        "description": "Provides info from specialized agent",
        "parameters": {
            "type": "object",
            "properties": {"agent_name": {"type": "string", "enum": additional_agents}},
            "required": ["agent_name"],
        },
    },
}
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]
).partial(additional_agents=", ".join(additional_agents))

llm = ChatOpenAI(temperature=0, streaming=True)

agent = prompt | llm.bind(tools=[tool_def]) | OpenAIToolsAgentOutputParser()
