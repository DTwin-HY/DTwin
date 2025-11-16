import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.services.dataframe_creation import create_product_sales_data
from src.services.dataframe_creation import csv_to_pd


def test_returns_dataframe():
    df = create_product_sales_data()
    # Oikea tyyppi
    assert isinstance(df, pd.DataFrame)
    # Oletuksena 30 riviä
    assert len(df) == 30
    # Oikeat kolumnit
    assert list(df.columns) == ["sales", "price", "customers", "sunny"]

def test_csv_to_pd_reads_csv(tmp_path):
    # 1. Luodaan väliaikainen csv-tiedosto
    csv_content = "col1,col2\n1,hello\n2,world\n"
    csv_path = tmp_path / "test.csv"
    csv_path.write_text(csv_content, encoding="utf-8")

    # 2. Ajetaan funktio
    df = csv_to_pd(str(csv_path))

    # 3. Tarkistetaan tulos
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["col1", "col2"]
    assert len(df) == 2
    assert df.iloc[0]["col2"] == "hello"
    assert df.iloc[1]["col1"] == 2