import matplotlib.pyplot as plt
import pandas as pd
import os
import base64
from io import BytesIO
from PIL import Image
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
        elif task == "create_graph":
            month = request.get("month")
            if not month:
                raise ValueError("Month parameter is required for creating sales graph.")
            return self.tool.create_sales_graph(month)
        else:
            return f"Unknown task: {task}"

class SalesTool:
    def __init__(self, csv_path: str):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Sales data not found at: {csv_path}")
        try:
            self.sales_data = pd.read_csv(csv_path)
            self.sales_data["date"] = pd.to_datetime(self.sales_data["date"])
            self.sales_data["month"] = self.sales_data["date"].dt.to_period("M")
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

    def create_sales_graph(self, month: str, graph_type: str = "line"):
        """
        Create a line or bar graph visualizing daily revenue for a specific month.
        Return the graph as a base64-encoded image for the supervisor.
        """
        filtered_data = self.sales_data[self.sales_data['month'].astype(str) == month]
        if filtered_data.empty:
            return {
                "status": "error",
                "message": f"No sales data for {month}"
            }


        aggregated_data = (
            filtered_data.groupby("date")
            .agg(total_revenue=("revenue", "sum"))
            .reset_index()
        )

        aggregated_data["7_day_avg"] = aggregated_data["total_revenue"].rolling(7).mean()

        plt.figure(figsize=(10, 6))

        if graph_type == "bar":
            plt.bar(aggregated_data["date"], aggregated_data["total_revenue"], label="Daily Revenue")
        else:
            plt.plot(
                aggregated_data["date"],
                aggregated_data["total_revenue"],
                marker="o",
                label="Daily revenue",
            )

        plt.plot(
            aggregated_data["date"],
            aggregated_data["7_day_avg"],
            linestyle="--",
            label="7-Day Avg"
        )

        plt.title(f"Daily Sales Revenue for {month}")
        plt.xlabel("Date")
        plt.ylabel("Revenue")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        plt.close()
        buffer.seek(0)

        img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()

        return {
            "status": "success",
            "type": "image",
            "format": "png",
            "data": img_b64,
            "caption": f"Daily Sales Revenue for {month}"
        }

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
def create_sales_graph(month: str) -> dict:
    """
    Returns a base64-encoded image of a graph that visualizes daily revenue for a specific month.
    """
    request = {"task": "create_graph", "month": month}
    return sales_agent_instance.handle_request(request)



if __name__ == "__main__":
    sales_agent = create_react_agent(
        name="sales_agent",
        model="openai:gpt-5-nano",
        tools=[generate_sales_report, create_sales_graph],
        prompt=(
            "You are a sales agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Assist ONLY with sales-related tasks\n"
            "- When asked to create a graph, use the create_sales_graph tool\n"
            "- After you're done with your tasks, respond to the supervisor directly\n"
            "- Respond ONLY with the results of your work, do NOT include ANY other text."),
    )

    result = sales_agent.invoke(
        {"messages": [HumanMessage(content="Generate sales graph for September")]}
    )

    print(result["messages"][-1].content)