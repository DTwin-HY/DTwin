from datetime import datetime

import numpy as np
import pandas as pd


def create_product_sales_data(rows: int = 30):
    """Generate (by default 30 rows of) daily product data for simulation testing."""
    np.random.seed(42)  # same numbers each run, for reproducibility

    sales = np.random.randint(70, 200, size=rows)
    price = np.round(np.random.uniform(10.0, 15.0, size=30), 2)
    customers = np.random.randint(40, 100, size=rows)
    sunny = np.random.choice([0, 1], size=rows).astype(bool)

    # Combine into a dataframe
    df = pd.DataFrame({"sales": sales, "price": price, "customers": customers, "sunny": sunny})

    return df


if __name__ == "__main__":
    df = create_product_sales_data()
    print(df.head())
