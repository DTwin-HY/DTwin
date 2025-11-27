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
        WHERE timestamp BETWEEN :start_date AND :end_date;
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


def query_sales(start,end):
    """
    Query sales data for date, quantity and revenue per day.
    Returns a SQLALchemy query result object.
    Args:
        start (str): start date as string
        end (str): end date as string
    """

    sql = text(
        """
        SELECT 
                timestamp,
                SUM(quantity) as quantity,
                SUM(amount)  as revenue 
        FROM 
                sales
        WHERE 
                timestamp BETWEEN :start_date AND :end_date
        GROUP BY 
                timestamp
        ORDER BY
                timestamp; 
        """
    )
    try:
        result = db.session.execute(sql, {"start_date":start, "end_date":end}).fetchall()

        return result

    except Exception:
        db.session.rollback()
        raise

def query_timeperiod_sales(start, end, time_interval):
    """
    Query sales data for quantity and revenue per selected time interval. Returns a query object.
    Args:
        start (str): start date as string
        end (str): end date as string
        time_interval (str):time interval used by postgres date_part(), e.g.'week' or 'month'
    """
    sql = text(
        """
        SELECT 
            date_part(:time_interval, timestamp) as timeperiod,
            SUM(quantity) as quantity,
            SUM(amount)  as revenue 
        FROM 
            sales
        WHERE 
            timestamp BETWEEN :start_date AND :end_date
        GROUP BY 
            timeperiod
        ORDER BY
            timeperiod; 
        """
    )
    try:
        result = db.session.execute(sql, {"start_date":start, "end_date":end,
                                    'time_interval':time_interval}).fetchall()

        return result

    except Exception:
        db.session.rollback()
        raise


def query_transactions(start, end):
    """
    Query daily transactions over selected time period.
    Args:
        start (str): Start date as string
        end (str): End date as string
    """
    sql = text(
        """
        SELECT 
            timestamp, 
            COUNT(transaction_id) as transactions
        FROM 
            sales 
        WHERE 
            timestamp BETWEEN :start_date AND :end_date 
        GROUP BY 
            timestamp 
        ORDER BY 
            timestamp;
        """
    )
    try:
        result = db.session.execute(sql, {"start_date":start, "end_date":end}).fetchall()
        return result

    except Exception:
        db.session.rollback()
        raise

def query_timeperiod_transactions(start, end, time_interval):
    """
    Query transactions over selected time interval, e.g. daily, weekly or monthly.
    Args:
        start (str): start date of query
        end (str): end date of query
        time_interval (str): Selected postgres time interval, e.g. 'day', 'week' or 'month'

    """
    sql = text(
        """
        SELECT 
                date_part(:time_interval, timestamp) as timeperiod, 
                COUNT(transaction_id) as transactions
        FROM 
                sales 
        WHERE 
                timestamp BETWEEN :start_date AND :end_date 
        GROUP BY 
                timeperiod 
        ORDER BY 
                timeperiod;
        """
    )
    try:
        result = db.session.execute(sql, {"start_date":start, "end_date":end,
                                    'time_interval': time_interval}).fetchall()
        return result

    except Exception:
        db.session.rollback()
        raise
