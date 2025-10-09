import os
from dotenv import load_dotenv
from loguru import logger
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from src.utils.rate_limiter import RateLimiter


"""
A simple chatbot implementation using LangGraph and LangChain with OpenAI's GPT model.
"""
load_dotenv()
SELECTED_MODEL = "gpt-5-nano"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TIMEOUT = 10  # seconds
llm = ChatOpenAI(model=SELECTED_MODEL, api_key=OPENAI_API_KEY)
rate_limiter = RateLimiter(max_calls=5, interval=10)  # max 5 calls per 10 seconds


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State) -> State:
    rate_limiter.check()
    return {"messages": [llm.invoke(state["messages"])]}


def answer(prompt: str) -> dict[str, str]:
    try:
        response = graph.invoke({"messages": [HumanMessage(content=prompt)]})
        response_text = response["messages"][-1].content
        return {"message": response_text}

    except KeyError:
        logger.error("Invalid response")
        return {"message": "Error: Could not generate response"}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()
try:
    print(graph.get_graph().draw_ascii())
except Exception:
    "Error in drawing graph"
