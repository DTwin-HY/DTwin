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
    names = [str(uuid.uuid4()) for _ in range(data_rows)]
    prices = [round(random.uniform(0, 100), 2) for _ in range(data_rows)]
    amounts = [random.randint(0, 1 << 12) for _ in range(data_rows)]

    engine = create_engine(CONNECTION_STRING)

    product_table = models.Product.__table__
    inventory_table = models.Inventory.__table__
    product_table.create(engine, checkfirst=True)
    inventory_table.create(engine, checkfirst=True)

    products = [{"name": name, "price": Decimal(str(price))} for name, price in zip(names, prices)]

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
                for name, amount in zip(names, amounts)
            ]

            conn.execute(inventory_table.insert(), inventory_rows)
    finally:
        engine.dispose()

    products_df = pd.DataFrame(
        {"id": [name_to_id[name] for name in names], "name": names, "price": prices}
    )
    inventory_df = pd.DataFrame(
        {"amount": amounts, "product_id": [name_to_id[name] for name in names]}
    )

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

    data_rows = config.get("data.rows_to_generate", 100)

    generate_data(data_rows, output_path)


if __name__ == "__main__":
    main()
