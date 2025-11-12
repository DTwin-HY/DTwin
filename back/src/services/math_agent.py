import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from langchain.agents.middleware import AgentState

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class CustomState(AgentState):
    testing_value: str



def add(a: float, b: float, runtime: ToolRuntime[CustomState]) -> float:
    """Add two numbers."""
    return a + b

def multiply(a: float, b: float):
    """Multiply two numbers."""
    return a * b

def divide(a: float, b: float):
    """Divide two numbers."""
    return a / b

@tool
def update_state(runtime: ToolRuntime) -> Command:
    """Tool to update the testing_value in the state."""
    return Command(update={
        "testing_value": "wtf is going on?",
        "messages": [
            ToolMessage(
                content="State succesfully updated.",
                tool_call_id=runtime.tool_call_id
            )
        ]
    })

math_agent = create_agent(
    model="openai:gpt-4.1",
    tools=[add, multiply, divide,update_state],
    system_prompt=(
        "You are a math agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with math-related tasks\n"
        "- Call the 'update_state' tool to update the testing_value in the state when you perform any operation."
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="math_agent",
    state_schema=CustomState,
)

@tool
def math_agent_tool(prompt: str, runtime: ToolRuntime[CustomState]) -> Command:
    """Wraps math_agent as a tool."""
    result = math_agent.invoke({"messages": [HumanMessage(content=prompt)], "testing_value": runtime.state.get("testing_value")})
    print(result)
    return Command(update={
        #"testing_value": result["testing_value"],
        "testing_value": result["testing_value"],
        "messages": [
            ToolMessage(
                content=result["messages"][-1].content,
                tool_call_id=runtime.tool_call_id
            )
        ]
    })