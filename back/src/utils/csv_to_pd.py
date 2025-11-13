import pandas as pd


def csv_to_pd(path: str) -> pd.DataFrame:
    """
    Load a csv file and convert it to a Pandas DataFrame.
    Temporarily returns string for testing purposes.
    """
    df = pd.read_csv(path)
    return str(df)