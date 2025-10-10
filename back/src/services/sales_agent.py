from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
def generate_sales_report():
    return

@tool
def create_sales_graph():
    return


sales_agent = create_react_agent(
    name="sales_agent",
    model="openai:gpt-5-nano",
    tools=[generate_sales_report, create_sales_graph],
    prompt=(
        "You are a sales agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with sales-related tasks\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."),
)