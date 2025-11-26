from sqlalchemy import text

from ..extensions import db


def fetch_sales_data(start, end):
    """
    Execute the sales summary query between start and end datetimes.
    """
    sql_query = text(
        """
        SELECT
            COALESCE(SUM(amount), 0) AS revenue,
            COALESCE(SUM(quantity), 0) AS sales,
            COUNT(DISTINCT transaction_id) AS transactions
        FROM sales
        WHERE date BETWEEN :start_date AND :end_date;
    """
    )
    try:
        result = (
            db.session.execute(sql_query, {"start_date": start, "end_date": end}).mappings().first()
        )

        revenue = float(result.get("revenue") or 0)
        sales = int(result.get("sales") or 0)
        transactions = int(result.get("transactions") or 0)

        return {"revenue": revenue, "sales": sales, "transactions": transactions}

    except Exception:
        # ensure DB session rollback on error
        db.session.rollback()
        raise
