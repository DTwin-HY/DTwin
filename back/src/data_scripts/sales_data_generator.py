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
    products = fetch_product_data()
    # num_products = len(products)
    product_ids = []
    prices = {}
    for id, price in products.items():
        product_ids.append(id)
        prices[id] = price
    
    print("tässä prodyucts length: ",len(products))

    # prices = {}
    # for name in product_names:
    #     if random.random() < 0.8:
    #         prices[name] = round(random.uniform(1, 20), 2)
    #     else:
    #         prices[name] = round(random.uniform(20, 100), 2)

    start_date = datetime.now() - timedelta(days=num_days)
    dates = [(start_date + timedelta(days=i)).date() for i in range(num_days)]

    sales_records = []
    for date in dates:
        for product_id in product_ids:
            price = Decimal(str(prices[product_id]))

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
                    "product_id": product_id,
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
                "product": record["product_id"],
                "items_sold": record["quantity"],
                "unit_price": float(prices[record["product_id"]]),
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

    # num_days = config.get("data.sales_days_to_generate", 100)
    num_days = 1

    generate_sales_data(num_days, output_path)


if __name__ == "__main__":
    main()
