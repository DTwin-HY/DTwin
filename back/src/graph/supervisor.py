import json
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph_supervisor import create_supervisor

from ..services.math_agent import math_agent
from ..services.research_agent import research_agent
from ..services.sales_agent import sales_agent
from ..services.storage_agent import storage_react_agent
from ..utils.format import format_chunk
from ..utils.pretty_print import pretty_print_messages

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")


init_supervisor = create_supervisor(
    model=init_chat_model("openai:gpt-4.1"),
    agents=[research_agent, math_agent, storage_react_agent, sales_agent],
    prompt=(
        "You are a supervisor managing four agents:\n"
        "- a research agent. Assign research-related tasks to this agent\n"
        "- a math agent. Assign math-related tasks to this agent\n"
        "- a storage agent. Assign storage related tasks to this agent\n"
        "- a sales agent. Assign sales related tasks to this agent\n"
        "Assign work to one agent at a time, do not call agents in parallel.\n"
        "When an agent returns a result (especially image data), immediately pass that result to the user.\n"
        "Do NOT call additional agents after receiving a complete result.\n"
        "Do NOT modify or summarize agent responses - pass them through as-is.\n"
        "Do not do any work yourself."
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
    )

def stream_process(prompt: str, thread_id: str = "3"):
    """
    runs the supervisor with the given prompt and streams the interphases.
    saves the final prompt and reply to the database.
    conversations are saved in the database
    """
    config = {"configurable": {"thread_id": thread_id}}

    with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
        checkpointer.setup()
        supervisor = init_supervisor.compile(checkpointer=checkpointer)

        for chunk in supervisor.stream(
            {"messages": [{"role": "user", "content": prompt}]},
            config,
            subgraphs=True,
        ):
            output = format_chunk(chunk) # stream the output to the frontend
            yield f"data: {json.dumps(output)}\n\n"

if __name__ == "__main__":
    with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
        checkpointer.setup()

        supervisor = init_supervisor.compile(checkpointer=checkpointer)

        config = {"configurable": {"thread_id":"1"}}
        for chunk in supervisor.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Please take inventory of the warehouse.",
                    }
                ]
            },
            config,
            subgraphs=True,
        ):
            pretty_print_messages(chunk, last_message=True)

        for chunk in supervisor.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Which item was there least of in the previous query" +
                        ", also what was my name?",
                    }
                ]
            },
            config,
            subgraphs=True,
        ):
            pretty_print_messages(chunk, last_message=True)
