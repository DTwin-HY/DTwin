import os
from datetime import datetime, timedelta
from functools import lru_cache

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text

from ..extensions import db
from ..index import app
from ..services.sql_agent import run_sql_agent

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

print("Generating SQL query via LangGraph agent...")
try:
    _SQL_QUERY = run_sql_agent(
        """
        Generate a SQL query that calculates:
        - total revenue (sum of amount or quantity * price),
        - total units sold,
        - number of distinct transactions,
        from a table called 'sales', between :start_date and :end_date.
        Return columns as revenue, sales, transactions.
    """
    )
    if "```sql" in _SQL_QUERY:
        _SQL_QUERY = _SQL_QUERY.split("```sql")[1].split("```")[0].strip()
    print("✅ SQL ready:\n", _SQL_QUERY)
except Exception as e:
    print("SQL generation failed, using fallback:", e)
    _SQL_QUERY = """
        SELECT
            COALESCE(SUM(amount), 0) AS revenue,
            COALESCE(SUM(quantity), 0) AS sales,
            COUNT(DISTINCT transaction_id) AS transactions
        FROM sales
        WHERE timestamp BETWEEN :start_date AND :end_date;
    """


@app.get("/api/sales-data")
def get_sales_data():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not start_date or not end_date:
        return jsonify({"error": "start_date and end_date are required"}), 400

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # If same day, extend the end by +1 day
        if start == end:
            end += timedelta(days=1)

        with engine.connect() as conn:
            result = conn.execute(
                text(_SQL_QUERY),
                {"start_date": start, "end_date": end},
            )
            row = result.mappings().first()

        if not row:
            return jsonify({"revenue": 0, "sales": 0, "transactions": 0})

        revenue = float(row.get("revenue") or 0)
        sales = int(row.get("sales") or 0)
        transactions = int(row.get("transactions") or 0)

        return jsonify(
            {
                "revenue": revenue,
                "sales": sales,
                "transactions": transactions,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e), "revenue": 0, "sales": 0, "transactions": 0}), 500
