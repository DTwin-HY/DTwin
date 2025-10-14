import os
from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from loguru import logger
from src.services.research_agent import research_agent
from src.services.math_agent import math_agent
from src.services.storage_agent import storage_react_agent
from src.utils.pretty_print import pretty_print_messages
from dotenv import load_dotenv

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

def answer(prompt: str) -> dict[str, str]:
    try:
        response = supervisor.invoke({"messages": [HumanMessage(content=prompt)]})
        response_text = response["messages"][-1].content
        return {"message": response_text}

    except KeyError:
        logger.error("Invalid response")
        return {"message": "Error: Could not generate response"}
    

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
