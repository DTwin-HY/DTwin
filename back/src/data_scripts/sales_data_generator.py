# pylint: disable=too-many-branches, too-many-locals
import os
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


from ..database.product_db import fetch_product_data
from .. import config
from ..models import models

load_dotenv()

CONNECTION_STRING = os.getenv("DATABASE_URL")


def sales_data_exists():
    engine = create_engine(CONNECTION_STRING)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM sales"))
        count = result.scalar()
    return count > 0


def generate_sales_data(num_days: int, output_path: Path):
    print("Fetching product data from database...", fetch_product_data()["1"])
    num_products = config.get("data.num_products", 100)
    product_names = []
    for i in range(num_products):
        n = i
        name = ""
        while n >= 0:
            name = chr(65 + (n % 26)) + name
            n = n // 26 - 1
        product_names.append(name)

    prices = {}
    for name in product_names:
        if random.random() < 0.8:
            prices[name] = round(random.uniform(1, 20), 2)
        else:
            prices[name] = round(random.uniform(20, 100), 2)

    start_date = datetime.now() - timedelta(days=num_days)
    dates = [(start_date + timedelta(days=i)).date() for i in range(num_days)]

    sales_records = []
    for date in dates:
        for product_name in product_names:
            price = Decimal(str(prices[product_name]))

            if price > 80:
                items_sold = random.choice([0] * 5 + list(range(1, 6)))
            elif price > 50:
                items_sold = random.choice([0] * 3 + list(range(1, 12)))
            elif price > 30:
                items_sold = random.randint(0, 25)
            else:
                items_sold = random.randint(0, 50)

            revenue = Decimal(str(round(items_sold * float(price), 2)))

            sales_records.append(
                {
                    "transaction_id": str(uuid.uuid4()),
                    "item_id": product_name,
                    "quantity": items_sold,
                    "timestamp": datetime.combine(date, datetime.min.time()),
                    "amount": revenue,
                }
            )

    engine = create_engine(CONNECTION_STRING)

    sales_table = models.Sale.__table__
    sales_table.create(engine, checkfirst=True)

    try:
        with engine.begin() as conn:
            try:
                conn.execute(text("TRUNCATE TABLE sales RESTART IDENTITY CASCADE;"))
            except Exception:
                conn.execute(sales_table.delete())

            conn.execute(sales_table.insert(), sales_records)
    finally:
        engine.dispose()

    sales_df = pd.DataFrame(
        [
            {
                "date": record["timestamp"].date(),
                "product": record["item_id"],
                "items_sold": record["quantity"],
                "unit_price": float(prices[record["item_id"]]),
                "revenue": float(record["amount"]),
            }
            for record in sales_records
        ]
    )

    if config.get("write_to_csv", False):
        sales_df.to_csv(output_path, index=False)

    print(f"Generated {len(sales_df)} sales records for {num_days} days")
    print(f"Total revenue: ${sales_df['revenue'].sum():.2f}")
    print(f"Total items sold: {sales_df['items_sold'].sum()}")
    print(sales_df.head())
    print("Sales data generated successfully")


def main():
    if sales_data_exists():
        print("Database already contains sales data, skipping population...")
        return
    output_filename = config.get("data.sales_filename", "sales_data.csv")
    output_path = Path(__file__).resolve().parent / output_filename

    num_days = config.get("data.sales_days_to_generate", 1000)

    generate_sales_data(num_days, output_path)


if __name__ == "__main__":
    main()
