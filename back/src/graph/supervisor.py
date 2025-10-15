import os
import json
from dotenv import load_dotenv
from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from sqlalchemy.sql import text

from ..index import db
from src.services.research_agent import research_agent
from src.services.math_agent import math_agent
from src.services.storage_agent import storage_react_agent
from src.utils.pretty_print import pretty_print_messages
from src.utils.format import format_chunk
from langchain_core.messages import convert_to_messages
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supervisor = create_supervisor(
    model=init_chat_model("openai:gpt-4.1"),
    # TODO vaihda nämä sales ja storage agenteiksi
    agents=[research_agent, math_agent, storage_react_agent],
    # TODO vaihda promptit agenteille sopiviksi
    prompt=(
        "You are a supervisor managing three agents:\n"
        "- a research agent. Assign research-related tasks to this agent\n"
        "- a math agent. Assign math-related tasks to this agent\n"
        "- a storage agent. Assign storage related tasks to this agent."
        "Assign work to one agent at a time, do not call agents in parallel.\n"
        # "If you find the result DON'T call other agents and return the result immediately\n"
        "Do not do any work yourself."
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
).compile()
    
def stream_process(prompt):
    """
    runs the supervisor with the given prompt and streams the interphases.
    saves the final prompt and reply to the database.
    """
    last_message = None
    for chunk in supervisor.stream(
        {"messages": [{"role": "user", "content": prompt}]},
        subgraphs=True,
    ):
        output = format_chunk(chunk)
        # stream the output to the frontend
        yield f"data: {json.dumps(output)}\n\n"
        last_message = chunk

    #save to db
    if last_message and "messages" in last_message:
        final_reply = last_message["messages"][-1].get("content", "")
        sql = text("INSERT INTO logs (prompt, reply) VALUES (:prompt, :reply);")
        db.session.execute(sql, {"prompt": prompt, "reply": final_reply})
        db.session.commit()

        # notify frontend that the process is done
        yield f"data: {json.dumps({'done': True, 'reply': final_reply})}\n\n"

if __name__ == "__main__":
    for chunk in supervisor.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "How much products for product id A100 is in the storage?",
                }
            ]
        },
        subgraphs=True,
    ):
        pretty_print_messages(chunk, last_message=True)
