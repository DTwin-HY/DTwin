import base64
import os
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent


class SalesAgent:
    def __init__(self, sales_tool):
        self.tool = sales_tool

    def handle_request(self, request: dict):
        task = request.get("task")
        if task == "sales_report":
            return self.tool.generate_sales_report()
        if task == "create_graph":
            month = request.get("month")
            if not month:
                raise ValueError("Month parameter is required for creating sales graph.")
            return self.tool.create_sales_graph(month)
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
        """
        Return key monthly sales metrics: total revenue, total items sold,
        best-selling product.
        """
        self.sales_data["date"] = pd.to_datetime(self.sales_data["date"])
        self.sales_data["month"] = self.sales_data["date"].dt.to_period("M")

        report = []
        for month, group in self.sales_data.groupby("month"):
            total_revenue = group["revenue"].sum()
            total_items = group["items_sold"].sum()
            best_product_row = group.groupby("product")["items_sold"].sum().idxmax()
            best_product_sold = group.groupby("product")["items_sold"].sum()[best_product_row]

            report.append(
                {
                    "month": str(month),
                    "total_revenue": float(total_revenue),
                    "total_items_sold": int(total_items),
                    "best_selling_product": best_product_row,
                    "best_selling_product_units": int(best_product_sold),
                }
            )

        return report

    def create_sales_graph(self, month: str, graph_type: str = "line"):
        filtered_data = self.sales_data[self.sales_data["month"].astype(str) == month]
        if filtered_data.empty:
            return {"status": "error", "message": f"No sales data for {month}"}

        aggregated_data = (
            filtered_data.groupby("date").agg(total_revenue=("revenue", "sum")).reset_index()
        )
        aggregated_data["7_day_avg"] = aggregated_data["total_revenue"].rolling(7).mean()

        plt.figure(figsize=(8, 6), dpi=100)

        if graph_type == "bar":
            plt.bar(aggregated_data["date"], aggregated_data["total_revenue"])
        else:
            plt.plot(aggregated_data["date"], aggregated_data["total_revenue"])

        plt.plot(aggregated_data["date"], aggregated_data["7_day_avg"], linestyle="--")
        plt.xlabel("Date")
        plt.ylabel("Revenue")
        plt.xticks(rotation=45)

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight", dpi=100)
        plt.close()
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()

        return {
            "type": "image",
            "data": image_base64,
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
    Returns base64-encoded image data of a graph that visualizes daily revenue for a specific month.
    The return value should be formatted as a message content block for image display.
    """
    request = {"task": "create_graph", "month": month}
    result = sales_agent_instance.handle_request(request)
    return result


sales_agent = create_react_agent(
    name="sales_agent",
    model="openai:gpt-4o-mini",
    tools=[generate_sales_report, create_sales_graph],
    prompt=(
        "You ONLY call tools and return their output. No thinking, no explanation.\n\n"
        "PROCESS:\n"
        "1. Receive request\n"
        "2. Call appropriate tool\n"
        "3. Return ONLY the tool's return value\n"
        "4. STOP\n\n"
        "FORBIDDEN:\n"
        "- Adding text like 'Here is...', 'I created...'\n"
        "- Explaining what you did\n"
        "- Formatting the output\n"
        "- Any text before/after the tool output\n\n"
        "RETURN ONLY THE TOOL OUTPUT AS-IS."
    ),
)

if __name__ == "__main__":
    result = sales_agent.invoke(
        {"messages": [HumanMessage(content="Generate sales graph for September")]}
    )

    print(result["messages"][-1].content)
