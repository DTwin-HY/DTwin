import os
from langgraph.prebuilt import create_react_agent
# from .helper_nodes import update_cash_register, update_inventory, add_log
from main.http_requests.req_weather import fetch_weather
from langchain_core.messages import convert_to_messages
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import convert_to_messages
from langgraph.graph import StateGraph, START, MessagesState, END
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supervisor_agent = create_react_agent(
    model="openai:gpt-5-nano",
    tools=[fetch_weather],
    prompt=(
        "You are a supervisor managing a weather fetcher function:\n"
        "-Assign weahter-related tasks to this function\n"
        "-GIve location to the function by lat and lon thats provided to you\n"
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
    .add_node("supervisor", supervisor_agent)
    .add_edge(START, "supervisor")
    .add_edge("supervisor", END)
    .compile()
)

for chunk in supervisor.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "Get the weather for Guangzhou",
            }
        ],
    },
    subgraphs=True,
):
    pretty_print_messages(chunk, last_message=True)