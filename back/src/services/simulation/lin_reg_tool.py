from typing import Any, Dict

import pandas as pd
from langchain.tools import tool

from ...services.simulation.lin_reg_graph import build_lin_reg_graph


def csv_fetch(dataframe_path: str) -> dict:
    """
    Fetches data saved as csv and returns a dictionary containing data.
    Parameters:
    dataframe_path: str : path to the dataframe csv file.
    """
    path = dataframe_path
    dataframe = pd.read_csv(path, sep=";").to_dict()

    return dataframe


@tool
def lin_reg_tool(data_location: str,y_value) -> Dict[str, Any]:
    """
    Runs the linear regression simulation graph on given data. \n
    Args:
        data_location (str): disk location of a csv file in str format
        y_value (str): Name of the value to be explained, y value in the linear 
            regression    
    """

    try:
        data = csv_fetch(data_location)
    except:
        return "Failed to load data."

    graph = build_lin_reg_graph()
    result = graph.invoke({"df": data, "y_value":y_value})

    return result.get("results", {"errors": result.get("errors", [])})
