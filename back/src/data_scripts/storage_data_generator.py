# pylint: disable=too-many-locals
import os
import random
import uuid
from decimal import Decimal
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from .. import config
from ..models import models
from ..utils.logger import logger

load_dotenv()

CONNECTION_STRING = os.getenv("DATABASE_URL")

items = [
    ("Apple", 1.20),
    ("Banana", 0.80),
    ("Orange", 0.90),
    ("Grapes", 2.50),
    ("Mango", 1.50),
    ("Pineapple", 3.00),
    ("Strawberry", 2.00),
    ("Blueberry", 2.20),
    ("Watermelon", 4.00),
    ("Peach", 1.80),
    ("Cherry", 2.80),
    ("Kiwi", 1.60),
    ("Papaya", 2.30),
    ("Plum", 1.70),
    ("Apricot", 2.10),
    ("Fig", 2.40),
    ("Coconut", 3.50),
    ("Lemon", 0.70),
    ("Lime", 0.75),
    ("Pomegranate", 2.60),
    ("Tangerine", 1.10),
    ("Guava", 1.90),
    ("Passion Fruit", 2.90),
    ("Dragon Fruit", 3.20),
    ("Cantaloupe", 3.10),
    ("Honeydew", 3.30),
    ("Raspberry", 2.70),
    ("Blackberry", 2.85),
    ("Cranberry", 2.95),
    ("Nectarine", 1.95),
]


def inventory_data_exists():
    engine = create_engine(CONNECTION_STRING)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM inventory"))
        count = result.scalar()
    return count > 0


def product_data_exists():
    engine = create_engine(CONNECTION_STRING)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM products"))
        count = result.scalar()
    return count > 0


def generate_data(data_rows: int, output_path: Path):
    """
    Generate product and inventory data and populate the database.
    If data_rows exceeds the number of predefined items, it is capped to that number.
    """
    data_rows = min(data_rows, len(items))
    selected = items[:data_rows]
    engine = create_engine(CONNECTION_STRING)

    product_table = models.Product.__table__
    inventory_table = models.Inventory.__table__
    product_table.create(engine, checkfirst=True)
    inventory_table.create(engine, checkfirst=True)

    products = [{"name": name, "price": Decimal(str(price))} for name, price in selected]
    amounts = [random.randint(0, 1 << 12) for _ in range(data_rows)]

    try:
        with engine.begin() as conn:
            try:
                conn.execute(
                    text(
                        "TRUNCATE TABLE inventory RESTART IDENTITY CASCADE; "
                        "TRUNCATE TABLE products RESTART IDENTITY CASCADE;"
                    )
                )
            except Exception:
                conn.execute(inventory_table.delete())
                conn.execute(product_table.delete())

            result = conn.execute(
                product_table.insert().returning(product_table.c.id, product_table.c.name),
                products,
            )
            inserted = result.mappings().all()
            name_to_id = {row["name"]: row["id"] for row in inserted}

            inventory_rows = [
                {"amount": amount, "product_id": name_to_id[name]}
                for (name, _), amount in zip(selected, amounts)
            ]
            if inventory_rows:
                conn.execute(inventory_table.insert(), inventory_rows)

    finally:
        engine.dispose()

    product_ids = [name_to_id[name] for name, _ in selected] if selected else []
    products_df = pd.DataFrame(
        {
            "id": product_ids,
            "name": [name for name, _ in selected],
            "price": [price for _, price in selected],
        }
    )
    inventory_df = pd.DataFrame({"amount": amounts, "product_id": product_ids})

    if config.get("write_to_csv", False):
        products_csv = output_path.with_name(output_path.stem + "_products.csv")
        inventory_csv = output_path.with_name(output_path.stem + "_inventory.csv")
        products_df.to_csv(products_csv, index=False)
        inventory_df.to_csv(inventory_csv, index=False)

    if config.get("write_to_csv", False):
        products_csv = output_path.with_name(output_path.stem + "_products.csv")
        inventory_csv = output_path.with_name(output_path.stem + "_inventory.csv")
        products_df.to_csv(products_csv, index=False)
        inventory_df.to_csv(inventory_csv, index=False)

    logger.info(f"Generated {len(products_df)} products and {len(inventory_df)} inventory rows")
    logger.debug(products_df.head())
    logger.debug(inventory_df.head())
    logger.info("Data generated successfully")


def main():
    if inventory_data_exists() or product_data_exists():
        if inventory_data_exists():
            logger.info("Database already contains inventory data, skipping population...")
        if product_data_exists():
            logger.info("Database already contains product data, skipping population...")
        return
    output_filename = config.get("data.filename", "data.csv")
    output_path = Path(__file__).resolve().parent / output_filename  # parent_dir/filename.csv

    # data_rows = config.get("data.rows_to_generate", 100)
    data_rows = 30

    generate_data(data_rows, output_path)


if __name__ == "__main__":
    main()
