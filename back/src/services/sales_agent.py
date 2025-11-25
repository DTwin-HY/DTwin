import base64
from datetime import datetime, timedelta
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool

from ..extensions import db
from ..models.models import Sale
from .sql_agent import sql_agent_tool


class SalesAgent:
    def __init__(self, sales_tool):
        self.tool = sales_tool

    def handle_request(self, request: dict):
        task = request.get("task")

        if task == "sales_report":
            return self.tool.generate_sales_report(
                start_date=request.get("start_date"),
                end_date=request.get("end_date"),
                group_by=request.get("group_by"),
            )

        if task == "create_graph":
            month = request.get("month")
            if not month:
                raise ValueError("Month parameter is required for creating sales graph.")
            return self.tool.create_sales_graph(month)
        return f"Unknown task: {task}"


class SalesTool:
    def _fetch_sales_data(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        product: str | None = None,
    ):
        """
        Fetch only the required subset of sales data from the database.
        """
        query = db.session.query(
<<<<<<< HEAD
            Sale.date.label("date"),
=======
            Sale.timestamp.label("date"),
>>>>>>> 6c89492 (fix llm prompts)
            Sale.product_id.label("product"),
            Sale.quantity.label("items_sold"),
            Sale.amount.label("revenue"),
        )

        if start_date:
            start_date = pd.to_datetime(start_date)
            query = query.filter(Sale.date >= start_date)

        if end_date:
            end_date = pd.to_datetime(end_date) + timedelta(days=1) - timedelta(seconds=1)
            query = query.filter(Sale.date <= end_date)

        if product:
            query = query.filter(Sale.product_id == product)

        rows = query.all()

        if not rows:
            return pd.DataFrame(columns=["date", "product", "items_sold", "revenue"])

        df = pd.DataFrame([r._asdict() for r in rows])
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")
        return df

    def generate_sales_report(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        group_by: str = "month",
    ):
        """Return key sales metrics: total revenue, total items sold, best-selling product."""
        if start_date and not end_date:
            end_date = start_date

        sales_data = self._fetch_sales_data(start_date, end_date)
        if sales_data.empty:
            return {"status": "error", "message": "No sales data for requested range"}

        # Ensure datetimes
        sales_data["date"] = pd.to_datetime(sales_data["date"], errors="coerce")

        # Determine grouping
        if group_by == "year":
            sales_data["period"] = sales_data["date"].dt.to_period("Y")
        elif group_by == "month":
            sales_data["period"] = sales_data["date"].dt.to_period("M")
        elif group_by == "week":
            sales_data["period"] = sales_data["date"].dt.to_period("W")
        elif group_by == "day":
            sales_data["period"] = sales_data["date"].dt.date
        else:
            raise ValueError("Invalid group_by value (must be 'year', 'month', 'week', or 'day')")

        report = []

        for period, group in sales_data.groupby("period"):
            total_revenue = group["revenue"].sum()
            total_items = group["items_sold"].sum()

            best_product_series = group.groupby("product")["items_sold"].sum()
            best_product = best_product_series.idxmax()
            best_units = best_product_series.max()

            report.append(
                {
                    "period": str(period),
                    "total_revenue": float(total_revenue),
                    "total_items_sold": int(total_items),
                    "best_selling_product": best_product,
                    "best_selling_product_units": int(best_units),
                }
            )

        return {
            "status": "success",
            "data": report,
            "group_by": group_by,
            "date_range": {
                "start_date": str(start_date) if start_date else None,
                "end_date": str(end_date) if end_date else None,
            },
        }

    def create_sales_graph(self, month: str, graph_type: str = "line"):
        sales_data = self._fetch_sales_data(month)
        if sales_data.empty:
            return {"status": "error", "message": f"No sales data for {month}"}

        aggregated_data = (
            sales_data.groupby("date").agg(total_revenue=("revenue", "sum")).reset_index()
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


sales_tool = SalesTool()
sales_agent_instance = SalesAgent(sales_tool)


@tool
def generate_sales_report(
    start_date: str | None = None,
    end_date: str | None = None,
    group_by: str = "month",
) -> dict:
    """
    Generate a report of key sales metrics over a given date range and grouping.

    Parameters:
      - start_date (optional)
      - end_date (optional)
      - group_by (optional): "year", "month", "week", or "day"

    Returns:
      A structured JSON report containing:
        - total revenue
        - total items sold
        - best-selling product and number of units
        grouped by the requested period.

    Example output:
    {
      "status": "success",
      "group_by": "month",
      "data": [
        {
          "period": "2025-09",
          "total_revenue": 12345.67,
          "total_items_sold": 421,
          "best_selling_product": "A",
          "best_selling_product_units": 92
        }
      ],
      "date_range": {
        "start_date": "2025-09-01",
        "end_date": "2025-09-30"
      }
    }
    """
    request = {
        "task": "sales_report",
        "start_date": start_date,
        "end_date": end_date,
        "group_by": group_by,
    }
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


sales_agent = create_agent(
    name="sales_agent",
    model="openai:gpt-4o-mini",
    tools=[generate_sales_report, create_sales_graph, sql_agent_tool],
    system_prompt=(
        "You are a smart sales analytics assistant."
        " Before starting, read these instructions carefully.\n"
        "You have access to structured tools and a SQL agent.\n\n"
        "Decision rules:\n"
        "1. If the user asks for a **report**, call ONLY the generate_sales_report tool."
        "Do not call create_sales_graph or sql_agent_tool."
        "- However, if the request is unclear, incomplete, or the timeframe (e.g., daily, weekly,"
        "  monthly, yearly) cannot be confidently identified, call the `sql_agent_tool` instead."
        "2. If the user asks for a **graph**, call the create_sales_graph tool."
        "3. If the user asks an **analytical**, **custom**, or **unstructured** question "
        "(e.g., comparisons, date ranges, averages, correlations), use the `sql_agent_tool`.\n"
        "4. Always return **only the tool output**. No explanations, no preamble, "
        "no markdown formatting.\n\n"
        "FORBIDDEN:\n"
        "- Adding text like 'Here is...', 'I created...'\n"
        "- Explaining what you did\n"
        "- Formatting the output\n"
        "- Any text before/after the tool output\n\n"
        "RETURN ONLY THE TOOL OUTPUT AS-IS."
    ),
)


@tool
def sales_agent_tool(prompt: str) -> str:
    """
    Wraps the sales_agent as a single tool.
    Takes a user prompt string (report, graph, or analytical question)
    and returns the agent's response as a string.
    """
    result = sales_agent.invoke({"messages": [HumanMessage(content=prompt)]})
    return result["messages"][-1].content


if __name__ == "__main__":
    result = sales_agent.invoke(
        {"messages": [HumanMessage(content="Generate sales graph for September")]}
    )

    print(result["messages"][-1].content)
