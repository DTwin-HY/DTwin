import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool, ToolRuntime

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def add(a: float, b: float):
    """Add two numbers."""
#    runtime.state["testing_value"] = "math_used"
    return a + b


def multiply(a: float, b: float):
    """Multiply two numbers."""
    return a * b


def divide(a: float, b: float):
    """Divide two numbers."""
    return a / b # pragma: no cover


math_agent = create_agent(
    model="openai:gpt-4.1",
    tools=[add, multiply, divide],
    system_prompt=(
        "You are a math agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with math-related tasks\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="math_agent",
)

@tool
def math_agent_tool(prompt: str) -> str:
    """Wraps math_agent as a tool."""
    result = math_agent.invoke({"messages": [HumanMessage(content=prompt)]})
    return result["messages"][-1].content # pragma: no cover
