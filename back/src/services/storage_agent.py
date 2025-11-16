from dotenv import load_dotenv
from langchain.messages import AIMessage, HumanMessage
from langchain.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph

from .sql_agent import sql_agent_tool

load_dotenv()


def call_sql_agent(state: MessagesState):
    """Kutsu SQL-agenttia kerran ilman LLM:n päätöksentekoa."""
    # Ota käyttäjän viesti
    user_message = state["messages"][0].content

    # Kutsu sql agenttia suoraan
    result = sql_agent_tool.invoke(user_message)

    # Palauta tulos AI Messagena
    return {"messages": [AIMessage(content=result)]}


def build_storage_agent():
    """Yksinkertainen graafi: kutsu SQL-agenttia kerran ja lopeta."""
    workflow = StateGraph(MessagesState)

    # Vain yksi node eli kutsu SQL agenttia
    workflow.add_node("call_sql", call_sql_agent)

    # Suora polku: START -> call_sql -> END
    workflow.add_edge(START, "call_sql")
    workflow.add_edge("call_sql", END)

    compiled = workflow.compile()
    compiled.name = "storage_agent"
    return compiled


# Luo react agentti
storage_react_agent = build_storage_agent()


@tool
def storage_agent_tool(prompt: str) -> str:
    """
    Wraps the storage_react_agent as a tool.
    Takes a user prompt string and returns the agent's response as a string.
    """
    result = storage_react_agent.invoke({"messages": [HumanMessage(content=prompt)]})
    return result["messages"][-1].content  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    result = storage_react_agent.invoke({"messages": [HumanMessage(content="Hae varaston saldot")]})
    print(result["messages"][-1].content)
