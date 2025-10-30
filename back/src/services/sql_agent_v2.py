import os
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

OPENAI_API_KEY = _get_env_or_raise("OPENAI_API_KEY")
DATABASE_URL = _get_env_or_raise("DATABASE_URL")

llm = ChatOpenAI(model=SELECTED_MODEL, api_key=OPENAI_API_KEY)

sql_db = SQLDatabase.from_uri(DATABASE_URL)
toolkit = SQLDatabaseToolkit(db=sql_db, llm=llm)
tools = toolkit.get_tools()


def _get_tool(name: str):
    """return the first tool with a matching name or raise a ValueError"""
    try:
        return next(tool for tool in tools if tool.name == name)
    except StopIteration as exc:
        #chain the original StopIteration for better exception context
        raise ValueError(f"Tool with name '{name}' not found in SQL toolkit") from exc


get_schema_tool = _get_tool("sql_db_schema")
get_schema_node = ToolNode([get_schema_tool], name="get_schema")

run_query_tool = _get_tool("sql_db_query")
run_query_node = ToolNode([run_query_tool], name="run_query")


def list_tables(_state: MessagesState) -> Dict[str, Any]:
    """call the toolkit's list tables tool and return messages that simulate the tool call flow

    The returned dict matches the shape expected by the graph runtime: {"messages": [...]}.
    """
    tool_call = {"name": "sql_db_list_tables", "args": {}, "id": "1", "type": "tool_call"}
    tool_call_message = AIMessage(content="", tool_calls=[tool_call])

    list_tables_tool = _get_tool("sql_db_list_tables")
    tool_message = list_tables_tool.invoke(tool_call)
    response = AIMessage(f"Available tables: {tool_message.content}")

    return {"messages": [tool_call_message, tool_message, response]}


def call_get_schema(state: MessagesState) -> Dict[str, Any]:
    llm_with_tools = llm.bind_tools([get_schema_tool], tool_choice="any")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


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
"""


def generate_query(state: MessagesState) -> Dict[str, Any]:
    system_message = {"role": "system", "content": generate_query_system_prompt}
    llm_with_tools = llm.bind_tools([run_query_tool])
    response = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [response]}


check_query_system_prompt = f"""
You are a SQL expert with a strong attention to detail.
Double check the {sql_db.dialect} query for common mistakes, including:
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
"""


def check_query(state: MessagesState) -> Dict[str, Any]:
    system_message = {"role": "system", "content": check_query_system_prompt}

    tool_call = state["messages"][-1].tool_calls[0]
    user_message = {"role": "user", "content": tool_call["args"]["query"]}
    llm_with_tools = llm.bind_tools([run_query_tool], tool_choice="any")
    response = llm_with_tools.invoke([system_message, user_message])

    response.id = state["messages"][-1].id
    return {"messages": [response]}


def should_continue(state: MessagesState) -> Literal[END, "check_query"]:
    """decide whether the graph should continue to the query check step.

    returns either the END sentinel (to finish) or the string name of the next
    node ("check_query"). We avoid a strict Literal return annotation here to
    keep typing simple and compatible with the graph runtime.
    """
    messages = state["messages"]
    last_message = messages[-1]
    return END if not getattr(last_message, "tool_calls", None) else "check_query"


# Build the state graph
builder = StateGraph(MessagesState)
builder.add_node(list_tables)
builder.add_node(call_get_schema)
builder.add_node(get_schema_node, "get_schema")
builder.add_node(generate_query)
builder.add_node(check_query)
builder.add_node(run_query_node, "run_query")

builder.add_edge(START, "list_tables")
builder.add_edge("list_tables", "call_get_schema")
builder.add_edge("call_get_schema", "get_schema")
builder.add_edge("get_schema", "generate_query")
builder.add_conditional_edges("generate_query", should_continue)
builder.add_edge("check_query", "run_query")
builder.add_edge("run_query", "generate_query")

sql_agent = builder.compile()


def run_sql_agent(query: str) -> str:
    """Invoke the compiled SQL subgraph with a single user query string

    Returns the content of the final message produced by the graph
    """
    result = sql_agent.invoke({"messages": [HumanMessage(content=query)]})
    return result["messages"][-1].content


sql_agent_tool = StructuredTool.from_function(
    func=run_sql_agent,
    name="sql_agent_tool",
    description="Executes SQL queries on the storage database and returns structured results.",
)


if __name__ == "__main__":
    question = "What's the most expensive product in the inventory?"

    #stream the graph execution to stdout for debugging/demonstration
    for step in sql_agent.stream({"messages": [{"role": "user", "content": question}]},
        stream_mode="values"):
        step["messages"][-1].pretty_print()
