import os
from typing import Annotated
from langgraph.types import Command
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.prebuilt import create_react_agent
from .seller import build_seller_agent
from langchain_core.messages import convert_to_messages
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import convert_to_messages
from langgraph.graph import StateGraph, START, MessagesState, END
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[MessagesState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            goto=agent_name,  
            update={**state, "messages": state["messages"] + [tool_message]},  
            graph=Command.PARENT,  
        )

    return handoff_tool


# Handoffs
assign_to_seller_agent = create_handoff_tool(
    agent_name="seller_agent",
    description="Assign task to a seller agent.",
)

seller_agent = build_seller_agent()
supervisor_agent = create_react_agent(
    model="openai:gpt-5-nano",
    tools=[assign_to_seller_agent],
    prompt=(
        "You are a supervisor managing a seller agent:\n"
        # "- fetch weather tool is where you get weather. If there is instruction to get weather for a location call it.\n"
        "- a seller agent. Assign transaction based tasks to this agent \n"
        # "Assign work to one agent at a time, do not call agents in parallel.\n"
        "Do not do any work yourself."
    ),
    name="supervisor",
)

def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)


def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")

supervisor = (
    StateGraph(MessagesState)
    .add_node(supervisor_agent, destinations=("seller_agent", END))
    .add_node(seller_agent)
    .add_edge(START, "supervisor")
    .add_edge("seller_agent", "supervisor")
    .add_edge("supervisor", END)
    .compile()
)

for chunk in supervisor.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "Then assign the task to the seller agent and have it run `simulate_sales` once. Return only the result.",
            }
        ]
    },
):
    pretty_print_messages(chunk, last_message=True)

final_message_history = chunk["supervisor"]["messages"]