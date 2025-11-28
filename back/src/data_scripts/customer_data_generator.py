# pylint: disable=too-many-branches, too-many-locals
import os
import random
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


from ..models import models

load_dotenv()

CONNECTION_STRING = os.getenv("DATABASE_URL")


def customer_data_exists():
    engine = create_engine(CONNECTION_STRING)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM customers"))
        count = result.scalar()
    return count > 0


def generate_customers_data(num_days: int):
    start_date = datetime.now() - timedelta(days=num_days)
    dates = [(start_date + timedelta(days=i)).date() for i in range(num_days)]

    customer_records = []
    for date in dates:
        for _ in range(num_days):
            prop = random.uniform(0, 100)

            if prop > 75:
                customer_count = random.randint(12, 25)
            elif prop > 50:
                customer_count = random.randint(25, 50)
            elif prop > 25:
                customer_count = random.randint(50, 75)
            else:
                customer_count = random.randint(75, 100)

            customer_records.append(
                {
                    "amount": customer_count,
                    "date": datetime.combine(date, datetime.min.time()),
                }
            )

    engine = create_engine(CONNECTION_STRING)

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
                "amount": record["amount"],
                "date": record["date"].date()
            }
            for record in customer_records
        ]
    )


    print(f"Generated {len(customer_df)} customer records for {num_days} days")
    print(customer_df.head())
    print("Customer data generated successfully")


def main():
    if customer_data_exists():
        print("Database already contains customer data, skipping population...")
        return

    num_days = 1000

    generate_customers_data(num_days)

if __name__ == "__main__":
    main()
