import os
import random
import uuid
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

from .. import config

load_dotenv()

CONNECTION_STRING = os.getenv("DATABASE_URL")


def generate_data(data_rows: int, output_path: Path):
    names = [str(uuid.uuid4()) for _ in range(data_rows)]
    prices = [round(random.uniform(0, 100), 2) for _ in range(data_rows)]
    amounts = [random.randint(0, 1 << 12) for _ in range(data_rows)]

    data = {"name": names, "price": prices, "amount": amounts}
    output_df = pd.DataFrame(data)

    engine = create_engine(CONNECTION_STRING)

    try:
        output_df.to_sql(name="products", con=engine, if_exists="replace", index=False)
    finally:
        engine.dispose()

    output_df.to_csv(output_path, index=False)

    print(f"Generated {len(output_df)} rows")
    print(output_df.head())
    print("Data generated successfully")


def main():
    output_filename = config.get("data.filename", "data.csv")
    output_path = Path(__file__).resolve().parent / output_filename  # parent_dir/filename.csv

    data_rows = config.get("data.rows_to_generate", 100000)

    generate_data(data_rows, output_path)


if __name__ == "__main__":
    main()
