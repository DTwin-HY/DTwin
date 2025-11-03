from sqlalchemy import text

from ..extensions import db
from ..services.sql_agent import run_sql_agent

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


def fetch_sales_data(start, end):
    """
    Execute the sales summary query between start and end datetimes.
    """
    try:
        result = (
            db.session.execute(db.text(_SQL_QUERY), {"start_date": start, "end_date": end})
            .mappings()
            .first()
        )

        revenue = float(result.get("revenue") or 0)
        sales = int(result.get("sales") or 0)
        transactions = int(result.get("transactions") or 0)

        return {"revenue": revenue, "sales": sales, "transactions": transactions}

    except Exception:
        # ensure DB session rollback on error
        db.session.rollback()
        raise
