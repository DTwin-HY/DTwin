import pandas as pd
import os
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

class SalesAgent:
    def __init__(self, sales_tool):
        self.tool = sales_tool

    def handle_request(self, request: dict):
        task = request.get("task")
        if task == "sales_report":
            return self.tool.generate_sales_report()

class SalesTool:
    def __init__(self, csv_path: str):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Sales data not found at: {csv_path}")
        try:
            self.sales_data = pd.read_csv(csv_path)
        except Exception as e:
            raise ValueError(f"Failed to read CSV: {e}")   

    def generate_sales_report(self):
        """Return key monthly sales metrics: total revenue, total items sold, best-selling product."""
        self.sales_data['date'] = pd.to_datetime(self.sales_data['date'])
        self.sales_data['month'] = self.sales_data['date'].dt.to_period('M')

        report = []
        for month, group in self.sales_data.groupby('month'):
            total_revenue = group['revenue'].sum()
            total_items = group['items_sold'].sum()
            best_product_row = group.groupby('product')['items_sold'].sum().idxmax()
            best_product_sold = group.groupby('product')['items_sold'].sum()[best_product_row]

            report.append({
                "month": str(month),
                "total_revenue": float(total_revenue),
                "total_items_sold": int(total_items),
                "best_selling_product": best_product_row,
                "best_selling_product_units": int(best_product_sold)
            })

        return report

csv_path = os.path.join(os.path.dirname(__file__), "../data/mock_month_sales_data.csv")

sales_tool = SalesTool(csv_path)
sales_agent_instance = SalesAgent(sales_tool)

@tool
def generate_sales_report() -> list:
    """
    Return key monthly sales metrics, including:
      - total revenue per month
      - total items sold per month
      - best-selling product per month and number of items sold
    Example output:
    [
      {
        "month": "2025-09",
        "total_revenue": 1370.84,
        "total_items_sold": 179,
        "best_selling_product": "G",
        "best_selling_product_units": 46
      }
    ]
    """
    request = {"task": "sales_report"}
    return sales_agent_instance.handle_request(request)

@tool
def create_sales_graph():
    """
    """
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

if __name__ == "__main__":
    result = sales_agent.invoke(
        {"messages": [HumanMessage(content="Generate sales report for September")]}
    )

    print(result["messages"][-1].content)
