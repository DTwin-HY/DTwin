import numpy as np
import pandas as pd


def np_to_pd(path: str) -> pd.DataFrame:
    """Load a npy file and convert it to a Pandas DataFrame."""
    data = np.load(path)

    df = pd.DataFrame(data)
    df.columns = ["sales", "price", "customers", "sunny"]

    return str(df)