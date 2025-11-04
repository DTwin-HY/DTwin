# pylint: disable=E1101
import os
from functools import lru_cache
from typing import Any, Dict, Literal

from dotenv import load_dotenv
from langchain.tools import StructuredTool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

load_dotenv()

SELECTED_MODEL = "gpt-4o-mini"


def _get_env_or_raise(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise EnvironmentError(f"Environment variable '{name}' is required but not set")
    return val


def _make_llm() -> ChatOpenAI:
    return ChatOpenAI(model=SELECTED_MODEL, api_key=_get_env_or_raise("OPENAI_API_KEY"))


def _make_toolkit() -> SQLDatabaseToolkit:
    db = SQLDatabase.from_uri(_get_env_or_raise("DATABASE_URL"))
    return SQLDatabaseToolkit(db=db, llm=_make_llm())


def _get_tool(tools, name: str):
    try:
        return next(tool for tool in tools if tool.name == name)
    except StopIteration as exc:
        raise ValueError(f"Tool with name '{name}' not found in SQL toolkit") from exc


def list_tables(_state: MessagesState) -> Dict[str, Any]:
    """Simuloi tool-kutsun viestivirtaa ja palauttaa MessagesState-muotoisen dictin."""
    toolkit = _make_toolkit()
    list_tables_tool = _get_tool(toolkit.get_tools(), "sql_db_list_tables")

    tool_call = {"name": "sql_db_list_tables", "args": {}, "id": "1", "type": "tool_call"}
    tool_call_message = AIMessage(content="", tool_calls=[tool_call])

    tool_message = list_tables_tool.invoke(tool_call)
    response = AIMessage(f"Available tables: {tool_message.content}")
    return {"messages": [tool_call_message, tool_message, response]}


def call_get_schema(state: MessagesState) -> Dict[str, Any]:
    toolkit = _make_toolkit()
    get_schema_tool = _get_tool(toolkit.get_tools(), "sql_db_schema")
    llm_with_tools = _make_llm().bind_tools([get_schema_tool], tool_choice="any")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def generate_query(state: MessagesState) -> Dict[str, Any]:
    toolkit = _make_toolkit()
    run_query_tool = _get_tool(toolkit.get_tools(), "sql_db_query")

    sql_db = toolkit.db
    generate_query_system_prompt = f"""
    You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct {sql_db.dialect} query to run,
    then look at the results of the query and return the answer. Unless the user
    specifies a specific number of examples they wish to obtain, always limit your
    query to at most 5 results.

    You can order the results by a relevant column to return the most interesting
    examples in the database. Never query for all the columns from a specific table,
    only ask for the relevant columns given the question.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
    """.strip()

    system_message = {"role": "system", "content": generate_query_system_prompt}
    llm_with_tools = _make_llm().bind_tools([run_query_tool])
    response = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [response]}


def check_query(state: MessagesState) -> Dict[str, Any]:
    toolkit = _make_toolkit()
    run_query_tool = _get_tool(toolkit.get_tools(), "sql_db_query")

    sql_db = toolkit.db
    check_query_system_prompt = f"""
    You are a SQL expert with a strong attention to detail.
    Double check the {sql_db.dialect} query for common mistakes, including:
    - Output ONLY a SQL code block and nothing else
    - Using NOT IN with NULL values
    - Using UNION when UNION ALL should have been used
    - Using BETWEEN for exclusive ranges
    - Data type mismatch in predicates
    - Properly quoting identifiers
    - Using the correct number of arguments for functions
    - Casting to the correct data type
    - Using the proper columns for joins

    If there are any of the above mistakes, rewrite the query. If there are no mistakes,
    just reproduce the original query.

    You will call the appropriate tool to execute the query after running this check.
    """.strip()

    tool_call = state["messages"][-1].tool_calls[0]
    user_message = {"role": "user", "content": tool_call["args"]["query"]}
    llm_with_tools = _make_llm().bind_tools([run_query_tool], tool_choice="any")
    response = llm_with_tools.invoke(
        [{"role": "system", "content": check_query_system_prompt}, user_message]
    )

    # varmista, että tool-call id linjassa
    response.id = state["messages"][-1].id
    return {"messages": [response]}


def should_continue(state: MessagesState) -> Literal[END, "check_query"]:
    last_message = state["messages"][-1]
    return END if not getattr(last_message, "tool_calls", None) else "check_query"


# Rakenna SQL-agentin graafi funktiossa
# Graafi rakennetaan vain kerran per prosessi: @lru_cache(maxsize=1) palauttaa saman
# instanssin myöhemmissä kutsuissa, kunnes cache tyhjennetään (cache_clear).
@lru_cache(maxsize=1)
def build_sql_agent_graph():
    """Rakenna ja käännä graafi täsmälleen kerran per prosessi."""
    toolkit = _make_toolkit()
    tools = toolkit.get_tools()

    get_schema_node = ToolNode([_get_tool(tools, "sql_db_schema")])
    run_query_node = ToolNode([_get_tool(tools, "sql_db_query")])

    builder = StateGraph(MessagesState)
    builder.add_node("list_tables", list_tables)
    builder.add_node("call_get_schema", call_get_schema)
    builder.add_node("get_schema", get_schema_node)
    builder.add_node("generate_query", generate_query)
    builder.add_node("check_query", check_query)
    builder.add_node("run_query", run_query_node)

    builder.add_edge(START, "list_tables")
    builder.add_edge("list_tables", "call_get_schema")
    builder.add_edge("call_get_schema", "get_schema")
    builder.add_edge("get_schema", "generate_query")
    builder.add_conditional_edges("generate_query", should_continue)
    builder.add_edge("check_query", "run_query")
    builder.add_edge("run_query", "generate_query")

    return builder.compile()


def get_sql_agent_graph():
    return build_sql_agent_graph()


def run_sql_agent(query: str) -> str:
    result = get_sql_agent_graph().invoke({"messages": [HumanMessage(content=query)]})
    return result["messages"][-1].content


sql_agent_tool = StructuredTool.from_function(
    func=run_sql_agent,
    name="sql_agent_tool",
    description=(
        "Executes SQL queries on the storage and sales databases " "and returns structured results."
    ),
)


if __name__ == "__main__":
    graph = get_sql_agent_graph()
    question = "What's the most expensive product in the inventory?"
    for step in graph.stream(
        {"messages": [{"role": "user", "content": question}]}, stream_mode="values"
    ):
        step["messages"][-1].pretty_print()
