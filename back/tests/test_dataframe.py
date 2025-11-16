import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.services.dataframe_creation import create_product_sales_data


def test_returns_dataframe():
    df = create_product_sales_data()
    # Oikea tyyppi
    assert isinstance(df, pd.DataFrame)
    # Oletuksena 30 riviä
    assert len(df) == 30
    # Oikeat kolumnit
    assert list(df.columns) == ["sales", "price", "customers", "sunny"]
