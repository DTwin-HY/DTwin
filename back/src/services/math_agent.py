import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from langchain.agents.middleware import AgentState

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class MathState(AgentState):
    """A customized State for the math agent subgraph."""
    testing_value: str

def multiply(a: float, b: float):
    """Multiply two numbers."""
    return a * b

def divide(a: float, b: float):
    """Divide two numbers."""
    return a / b

@tool
def add(a: float, b: float, runtime: ToolRuntime[MathState]) -> Command:
    """Tool to add numbers and update testing_value in the state."""
    result = a + b

    # Command updates the math agent state (runtime is from the math agent)
    return Command(update={
        "testing_value": result,
        "messages": [
            ToolMessage(
                content="Result of addition added to state",
                tool_call_id=runtime.tool_call_id
            )
        ]
    })

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
    state_schema=MathState,
)


@tool
def math_agent_tool(prompt: str, runtime: ToolRuntime) -> Command:
    """Wraps math_agent as a tool."""
    #Runtime refers to the parent graph (caller) runtime.
    #Parent state value is passed down to the subgraph agent through runtime.state
    result = math_agent.invoke({"messages": [HumanMessage(content=prompt)], "testing_value": runtime.state.get("testing_value")})
    print(result)

    # Command used to update state fields in the parent graphs state. If state keys match, they will be updated.
    return Command(update={
        "testing_value": result["testing_value"],
        "messages": [
            ToolMessage(
                content=result["messages"][-1].content,
                tool_call_id=runtime.tool_call_id
            )
        ]
    })