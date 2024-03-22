import functools
import operator
from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain.agents import AgentExecutor
from langchain.agents.output_parsers.openai_tools import OpenAIToolAgentAction
from langchain_core.agents import AgentFinish
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, ToolMessage
from langchain_core.runnables import Runnable
from langgraph.graph import END, StateGraph

from app.chains.notion.api import agent_executor as notion_api_agent_executor
from app.chains.notion.supervisor import agent as supervisor_agent


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # list of calls to agents which needs to be executed required
    calls_to_agent_required: Annotated[Sequence[OpenAIToolAgentAction], operator.setitem]


def tool_agent_node(state: dict, agent: AgentExecutor, name: str) -> dict:
    # Transform state to tool state: convert tool messages to scratchpad
    tool_state = {
        "messages": [],
    }  # type: ignore
    for message in state["messages"]:
        # Convert previous tool messages to system messages
        if isinstance(message, ToolMessage):
            message = SystemMessage(content=f"Prior answer from an agent {message.name}: {message.content}")
        # Ignore AI messages which are tool call requests
        if isinstance(message, AIMessage) and "tool_calls" in message.additional_kwargs:
            continue
        tool_state["messages"].append(message)
    result = agent.invoke(tool_state)
    # Get from state the last agent action to create a tool message
    agent_action: OpenAIToolAgentAction = state["calls_to_agent_required"][-1]

    return {
        "messages": (
            # Append the original tool call message to the message log otherwise OpenAI won't accept the answer
            list(agent_action.message_log)
            +
            # Set the same tool answer for all tool calls: sometimes OpenAI requests multiple tool calls but they are
            # all the same
            [
                ToolMessage(content=result["output"], name=name, tool_call_id=action.tool_call_id)
                for action in state["calls_to_agent_required"]
            ]
        ),
        "calls_to_agent_required": [],
    }


def supervisor_node(state: dict, agent: Runnable, name: str) -> dict:
    result = agent.invoke(state)
    if isinstance(result, AgentFinish):
        return {"messages": result.messages}
    if isinstance(result, list) and all(isinstance(m, OpenAIToolAgentAction) for m in result):
        return {
            "calls_to_agent_required": result,
        }
    raise ValueError(f"Unexpected result type from supervisor agent: {type(result)}")


def router(state: AgentState) -> str:
    """Cycle between agents until supervisor is ready to answer"""
    # When the last message is a non empty AIMessage, this means that the question is answered: exit from the graph
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.content != "":
        return "end"

    # When all calls to agents are done: go back to the supervisor
    if "calls_to_agent_required" not in state or len(state["calls_to_agent_required"]) == 0:
        return "Supervisor"

    # Otherwise, get the last agent action to route to the right agent
    agent_action: OpenAIToolAgentAction = state["calls_to_agent_required"][-1]
    if not agent_action.tool == "get_info_from_agent":
        raise ValueError(f"Unexpected agent action: {agent_action}")
    return agent_action.tool_input["agent_name"]  # type: ignore


workflow = StateGraph(AgentState)

notion_api_node = functools.partial(tool_agent_node, agent=notion_api_agent_executor, name="NotionAPI")
workflow.add_node("NotionAPI", notion_api_node)

supervisor_node = functools.partial(supervisor_node, agent=supervisor_agent, name="Supervisor")
workflow.add_node("Supervisor", supervisor_node)

# The supervisor populates the "next" field in the graph state
# which routes to a node or finishes
conditional_map = {
    "NotionAPI": "NotionAPI",
    "Supervisor": "Supervisor",
    "end": END,
}
workflow.add_conditional_edges("Supervisor", router, conditional_map)
workflow.add_conditional_edges("NotionAPI", router, conditional_map)
# Finally, add entrypoint
workflow.set_entry_point("Supervisor")

graph = workflow.compile()
