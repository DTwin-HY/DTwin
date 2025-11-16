import pandas as pd
import sys
import types
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.services.dataframe_creation import create_product_sales_data, csv_to_pd, create_dataframe_tool

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

def test_create_dataframe_tool_creates_csv_and_command(tmp_path, monkeypatch):
    # 1. Vaihda työskentelykansio väliaikaiseen hakemistoon
    monkeypatch.chdir(tmp_path)

    # 2. Feikki runtime, jossa on tool_call_id
    runtime = types.SimpleNamespace(tool_call_id="test123")

    # 3. Kutsu työkalun "raaka" funktio (koska @tool tekee siitä Tool-olion)
    command = create_dataframe_tool.func("any prompt", runtime=runtime)

    # 4. Tarkista että tiedosto syntyi oikeaan paikkaan
    expected_dir = tmp_path / "dataframes"
    expected_file = expected_dir / "dataframe_test123.csv"

    assert expected_dir.is_dir()
    assert expected_file.is_file()

    # 5. Lue CSV ja varmista että se on DataFrame
    df = pd.read_csv(expected_file)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

    # 6. Tarkista Commandin sisältö
    # 6. Tarkista Commandin sisältö
    assert isinstance(command.update, dict)
    assert "messages" in command.update
    messages = command.update["messages"]
    assert len(messages) == 1

    # tarkistetaan, että relatiivinen polku mainitaan viestissä
    assert "dataframes/dataframe_test123.csv" in messages[0].content
