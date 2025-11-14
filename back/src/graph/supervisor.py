import json
import os

from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from langchain.agents import create_agent
from langchain.agents.middleware import AgentState
from langchain.tools import tool, ToolRuntime

from ..services.math_agent import math_agent_tool
from ..services.research_agent import research_agent_tool
from ..services.sales_agent import sales_agent_tool
from ..services.storage_agent import storage_agent_tool
from ..utils.format import format_chunk
from ..utils.pretty_print import pretty_print_messages
from .supervisor_prompt import supervisor_prompt
from ..services.simulation.sim_agent import simulation_agent_tool
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

class MainState(AgentState): #pragma: no cover
    """A customized state for the supervisor agent."""
    #temp placeholder for state testing with math agent
    
    testing_value: str #pragma: no cover

@tool
def state_testing_tool(runtime:ToolRuntime) -> str:
    """Tool to check the value of testing_value in the state. Used in development only."""
    value = runtime.state.get("testing_value", "not_set") #pragma: no cover

    return value #pragma: no cover


# pylint: disable=contextmanager-generator-missing-cleanup
def stream_process(prompt: str, thread_id: str = "3"):
    """
    runs the supervisor with the given prompt and streams the interphases.
    saves the final prompt and reply to the database.
    conversations are saved in the database
    """
    config = {"configurable": {"thread_id": thread_id}}

    with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer: # pragma: no cover
        checkpointer.setup() # pragma: no cover

        supervisor = create_agent(
            model="openai:gpt-4.1",
            tools=[research_agent_tool, math_agent_tool, storage_agent_tool, sales_agent_tool, state_testing_tool, simulation_agent_tool],
            system_prompt=supervisor_prompt,
            state_schema=MainState,
            checkpointer=checkpointer)

        for chunk in supervisor.stream(
            {"messages": [{"role": "user", "content": prompt}]},
            stream_mode="updates",
            config=config,
        ):
            output = format_chunk(chunk)  # stream the output to the frontend
            yield f"data: {json.dumps(output)}\n\n"


if __name__ == "__main__": # pragma: no cover
    with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
        checkpointer.setup()

        supervisor = init_supervisor.compile(checkpointer=checkpointer)

        config = {"configurable": {"thread_id": "1"}}
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
                        "content": "What is the value of testing_value?",
                    }
                ]
            },
            config,
            subgraphs=True,
        ):
            pretty_print_messages(chunk, last_message=True)
