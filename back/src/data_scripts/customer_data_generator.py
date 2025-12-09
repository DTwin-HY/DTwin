# pylint: disable=too-many-branches, too-many-locals
import os
import random
import sys
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from ..models import models
from ..utils.logger import logger

load_dotenv()

CONNECTION_STRING = os.getenv("DATABASE_URL")


def customer_data_exists():
    engine = create_engine(CONNECTION_STRING)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM customers"))
        count = result.scalar()
    return count > 0


def query_sales(engine, start_date, end_date):
    """
    due to unfixed errors this is written twice instead of importing from database/sales
    """
    sales_sql = text(
        """
    SELECT 
            date,
            SUM(quantity) as quantity
    FROM 
            sales
    WHERE 
            date BETWEEN :start_date AND :end_date
    GROUP BY 
            date
    ORDER BY
            date; 
    """
    )
    with engine.connect() as conn:
        rows = (
            conn.execute(
                sales_sql, {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}
            )
            .mappings()
            .all()
        )
        return {row["date"].date().isoformat(): float(row["quantity"]) for row in rows}


def generate_customers_data(num_days: int):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=max(1, num_days) - 1)
    dates = [start_date + timedelta(days=i) for i in range(num_days)]

    engine = create_engine(CONNECTION_STRING)

    sales_map = query_sales(engine, start_date, end_date)

    customer_records = []
    for d in dates:
        avg_products = 5.0  # average products per customer
        total_amount = sales_map.get(d.isoformat(), 0.0)
        multiplier = random.uniform(0.8, 1.2)  # variability in customer spending
        customers = int(round((total_amount / avg_products) * multiplier))
        if customers < 0:
            customers = 0

        customer_records.append(
            {
                "daily_customer_amount": customers,
                "date": datetime.combine(d, datetime.min.time()),
            }
        )

    customer_table = models.Customer.__table__
    customer_table.create(engine, checkfirst=True)

    try:
        with engine.begin() as conn:
            try:
                conn.execute(text("TRUNCATE TABLE customers RESTART IDENTITY CASCADE;"))
            except Exception:
                conn.execute(customer_table.delete())

            conn.execute(customer_table.insert(), customer_records)
    finally:
        engine.dispose()

    customer_df = pd.DataFrame(
        [
            {
                "daily_customer_amount": record["daily_customer_amount"],
                "date": record["date"].date(),
            }
            for record in customer_records
        ]
    )

    logger.info(f"Generated {len(customer_df)} customer records for {num_days} days")
    logger.debug(customer_df.head())
    logger.info("Customer data generated successfully")


def main():
    if customer_data_exists():
        logger.info("Database already contains customer data, skipping population...")
        return

    num_days = 1000

    generate_customers_data(num_days)


if __name__ == "__main__":
    main()
