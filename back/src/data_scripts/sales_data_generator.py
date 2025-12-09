# pylint: disable=too-many-branches, too-many-locals
import os
import random
import sys
import uuid
from datetime import date as _date
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from .. import config
from ..database.product_db import fetch_product_data
from ..models import models
from ..utils.logger import logger

load_dotenv()

CONNECTION_STRING = os.getenv("DATABASE_URL")


def fetch_weather(start_dt: _date, end_dt: _date):
    """
    Fetch daily weather using Open-Meteo (free) and return a map date->sunny (bool).
    Returns {} on failure.
    """
    try:
        lat, lon = 60.1699, 24.9384
        url = "https://archive-api.open-meteo.com/v1/era5"

        # Try daily weathercode first
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "timezone": "Europe/Helsinki",
            "daily": "weathercode",
        }
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        j = resp.json()

        weather_map = {}
        if "daily" in j and "weathercode" in j["daily"]:
            times = j["daily"].get("time", [])
            codes = j["daily"].get("weathercode", [])
            for d, c in zip(times, codes):
                weather_map[d] = c <= 3
            return weather_map
    except Exception as e:
        print("Failed to fetch weather from Open-Meteo: ", e)
        return {}


def sales_data_exists():
    engine = create_engine(CONNECTION_STRING)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM sales"))
        count = result.scalar()
    return count > 0


def generate_sales_data(num_days: int, output_path: Path):
    products = fetch_product_data()
    product_ids = []
    prices = {}
    for id, price in products.items():
        product_ids.append(id)
        prices[id] = price

    logger.info("products data length: ", len(products))

    end_dt = datetime.now().date()
    start_dt = end_dt - timedelta(days=max(1, num_days) - 1)
    dates = [start_dt + timedelta(days=i) for i in range(num_days)]

    sales_records = []

    weather_map = fetch_weather(start_dt, end_dt)

    # default: if a date missing, assume not sunny
    def is_sunny(dt):
        key = dt.isoformat()
        print(key, "sunny:", weather_map.get(key, False))
        return bool(weather_map.get(key, False))

    for date in dates:
        sunny = is_sunny(date)
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

            # if sunny day, increase sales by 10-40%
            if sunny:
                multiplier = random.uniform(1.1, 1.4)
                items_sold = int(round(items_sold * multiplier))

            revenue = Decimal(str(round(items_sold * float(price), 2)))

            sales_records.append(
                {
                    "transaction_id": str(uuid.uuid4()),
                    "product_id": product_id,
                    "quantity": items_sold,
                    "date": datetime.combine(date, datetime.min.time()),
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
                "date": record["date"].date(),
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

    logger.info(f"Generated {len(sales_df)} sales records for {num_days} days")
    logger.info(f"Total revenue: ${sales_df['revenue'].sum():.2f}")
    logger.info(f"Total items sold: {sales_df['items_sold'].sum()}")
    logger.debug(sales_df.head())
    logger.info("Sales data generated successfully")


def main():
    if sales_data_exists():
        logger.info("Database already contains sales data, skipping population...")
        return
    output_filename = config.get("data.sales_filename", "sales_data.csv")
    output_path = Path(__file__).resolve().parent / output_filename

    num_days = 1000

    generate_sales_data(num_days, output_path)


if __name__ == "__main__":
    main()
