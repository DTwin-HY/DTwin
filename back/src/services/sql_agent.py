# pylint: disable=E1101
import os
from functools import lru_cache
from typing import Any, Dict, Literal

from dotenv import load_dotenv
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from ..utils.logger import logger

load_dotenv()

SELECTED_MODEL = "gpt-4o-mini"


def _get_env_or_raise(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise EnvironmentError(f"Environment variable '{name}' is required but not set")
    return val


_schema_cache: Dict[str, str] = {}


def get_cached_schema(state: MessagesState) -> Dict[str, Any]:
    """Get schema from cache or fetch if not cached."""
    toolkit = _make_toolkit()

    cache_key = _get_env_or_raise("DATABASE_URL")

    if cache_key in _schema_cache:
        return {"messages": [AIMessage(_schema_cache[cache_key])]}

    list_tables_tool = _get_tool(toolkit.get_tools(), "sql_db_list_tables")
    get_schema_tool = _get_tool(toolkit.get_tools(), "sql_db_schema")

    tables = list_tables_tool.invoke({})
    schema = get_schema_tool.invoke({"table_names": tables})

    combined = f"Available tables: {tables}\n\nSchema:\n{schema}"
    _schema_cache[cache_key] = combined

    return {"messages": [AIMessage(combined)]}


@lru_cache(maxsize=1)
def _make_llm() -> ChatOpenAI:
    return ChatOpenAI(model=SELECTED_MODEL, api_key=_get_env_or_raise("OPENAI_API_KEY"))


@lru_cache(maxsize=1)
def _make_toolkit() -> SQLDatabaseToolkit:
    db = SQLDatabase.from_uri(_get_env_or_raise("DATABASE_URL"))
    return SQLDatabaseToolkit(db=db, llm=_make_llm())


def _get_tool(tools, name: str):
    try:
        return next(tool for tool in tools if tool.name == name)
    except StopIteration as exc:
        raise ValueError(f"Tool with name '{name}' not found in SQL toolkit") from exc


def list_tables(_state: MessagesState) -> Dict[str, Any]:
    toolkit = _make_toolkit()
    list_tables_tool = _get_tool(toolkit.get_tools(), "sql_db_list_tables")
    result = list_tables_tool.invoke({})
    return {"messages": [AIMessage(f"Available tables: {result}")]}


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
    then look at the results of the query and return the answer.

    You can order the results by a relevant column to return the most interesting
    examples in the database. Never query for all the columns from a specific table,
    only ask for the relevant columns given the question.

    If you are asked about aggregate metrics, use {sql_db.dialect} appropriate aggregate queries
    to answer to create the metric. E.g. when asked about total sales, aggregate sales numbers to daily sums.
    
    ALWAYS include a date column in your queries.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
    DO NOT come up with any data, only return real data present in the database.

    IMPORTANT: After receiving query results, do NOT call the tool again. Instead,
    analyze the results and provide the final answer.
    """.strip()

    system_message = {"role": "system", "content": generate_query_system_prompt}
    llm_with_tools = _make_llm().bind_tools([run_query_tool])
    response = llm_with_tools.invoke([system_message] + state["messages"])
    logger.debug("sql response:", response)
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

    response.id = state["messages"][-1].id
    return {"messages": [response]}


def analyze_results(state: MessagesState) -> Dict[str, Any]:
    """Analysoi query-tulokset ja muodosta lopullinen vastaus."""
    llm = _make_llm()

    system_prompt = """
    You are a helpful assistant analyzing SQL query results.
    Based on the query results in the conversation history, provide a clear,
    concise answer to the user's original question. Format the results in a
    readable way.

    CRITICAL: Do NOT call any tools. Simply analyze the data you already have
    and provide the final answer.
    """

    response = llm.invoke([{"role": "system", "content": system_prompt}] + state["messages"])
    return {"messages": [response]}


def should_continue_after_generate(
    state: MessagesState,
) -> Literal["check_query", "analyze_results"]:
    """Decide if the query should be executed or if there are results to be analyzed."""
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "check_query"

    return "analyze_results"


def should_retry_query(state: MessagesState) -> Literal["generate_query", "analyze_results"]:
    """Decide if the query should be retried or if we should continue to analysis."""
    query_count = sum(
        1
        for msg in state["messages"]
        if hasattr(msg, "type") and msg.type == "tool" and "sql_db_query" in str(msg)
    )

    if query_count >= 2:
        return "analyze_results"

    last_tool_message = None
    for msg in reversed(state["messages"]):
        if hasattr(msg, "type") and msg.type == "tool":
            last_tool_message = msg
            break

    if last_tool_message and "error" in str(last_tool_message.content).lower():
        return "generate_query"

    return "analyze_results"


@lru_cache(maxsize=1)
def build_sql_agent_graph():
    """Build and compile graph once per process."""
    toolkit = _make_toolkit()
    tools = toolkit.get_tools()

    get_schema_node = ToolNode([_get_tool(tools, "sql_db_schema")])
    run_query_node = ToolNode([_get_tool(tools, "sql_db_query")])

    builder = StateGraph(MessagesState)
    builder.add_node("get_cached_schema", get_cached_schema)
    builder.add_node("generate_query", generate_query)
    builder.add_node("check_query", check_query)
    builder.add_node("run_query", run_query_node)
    builder.add_node("analyze_results", analyze_results)

    builder.add_edge(START, "get_cached_schema")
    builder.add_edge("get_cached_schema", "generate_query")

    builder.add_conditional_edges(
        "generate_query",
        should_continue_after_generate,
        {"check_query": "check_query", "analyze_results": "analyze_results"},
    )

    builder.add_edge("check_query", "run_query")

    builder.add_conditional_edges(
        "run_query",
        should_retry_query,
        {"generate_query": "generate_query", "analyze_results": "analyze_results"},
    )

    builder.add_edge("analyze_results", END)

    return builder.compile()


def get_sql_agent_graph():
    return build_sql_agent_graph()


def run_sql_agent(query: str) -> str:
    logger.debug("Running SQL agent with query:", query)
    result = get_sql_agent_graph().invoke({"messages": [HumanMessage(content=query)]})
    logger.debug("SQL agent response:", result)
    return result["messages"][-1].content


sql_agent_tool = StructuredTool.from_function(
    func=run_sql_agent,
    name="sql_agent_tool",
    description=(
        "Executes SQL queries on the storage and sales databases and returns structured results. "
        "Call this tool ONCE with a comprehensive query written in natural language - "
        "it returns ALL needed data in one execution."
    ),
)


if __name__ == "__main__":
    graph = get_sql_agent_graph()
    question = "What's the most expensive product in the inventory?"
    for step in graph.stream(
        {"messages": [{"role": "user", "content": question}]}, stream_mode="values"
    ):
        step["messages"][-1].pretty_print()
