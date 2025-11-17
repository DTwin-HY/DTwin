import json
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import AgentState
from langgraph.checkpoint.postgres import PostgresSaver

from ..services.mcp_client import mcp_agent_tool
from ..services.dataframe_creation import create_dataframe_tool, csv_dataframe_test_tool
from ..services.math_agent import math_agent_tool
from ..services.research_agent import research_agent_tool
from ..services.sales_agent import sales_agent_tool
from ..services.storage_agent import storage_agent_tool
from ..utils.format import format_chunk
from .supervisor_prompt import supervisor_prompt
from ..services.simulation.sim_agent import simulation_agent_tool
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")


class MainState(AgentState):  # pragma: no cover
    """A customized state for the supervisor agent."""

    test_value: str


# pylint: disable=contextmanager-generator-missing-cleanup
def stream_process(prompt: str, thread_id: str = "3"):
    """
    runs the supervisor with the given prompt and streams the interphases.
    saves the final prompt and reply to the database.
    conversations are saved in the database
    """
    config = {"configurable": {"thread_id": thread_id}}

    with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:  # pragma: no cover
        checkpointer.setup()  # pragma: no cover

        supervisor = create_agent(
            model="openai:gpt-4.1",
            tools=[
                research_agent_tool,
                math_agent_tool,
                mcp_agent_tool,
                storage_agent_tool,
                sales_agent_tool,
                create_dataframe_tool,
                csv_dataframe_test_tool,
                simulation_agent_tool,
            ],
            system_prompt=supervisor_prompt,
            state_schema=MainState,
            checkpointer=checkpointer,
        )

        for chunk in supervisor.stream(
            {"messages": [{"role": "user", "content": prompt}]},
            stream_mode="updates",
            config=config,
        ):
            output = format_chunk(chunk)  # stream the output to the frontend
            yield f"data: {json.dumps(output)}\n\n"
