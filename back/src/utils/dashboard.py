from flask import jsonify
from ..index import app


SALES_GRAPH_DATA = {
                "current_quarter": {0:20, 1:20, 2:20, 3:20, 4:20,5:20},
                "previous_quarter": {0:20, 1:20, 2:20, 3:20, 4:20,5:20},
                "ytd": {0:20, 1:20, 2:20, 3:20, 4:20,5:20},
}

SALES = {
        "current_quarter": {"amount":3300, "growth": 0.10},
        "previous_quarter":{"amount":3000, "growth": 0.13},
        "ytd": {"amount":11500, "growth": 0.09},
        "raw_graph_data": SALES_GRAPH_DATA

        }


REVENUE_GRAPH_DATA = {
                "current_quarter": {0:20, 1:20, 2:20, 3:20, 4:20,5:20},
                "previous_quarter": {0:20, 1:20, 2:20, 3:20, 4:20,5:20},
                "ytd": {0:20, 1:20, 2:20, 3:20, 4:20,5:20},
}

REVENUE = {
        "current_quarter": {"amount":22000, "growth": 0.10},
        "previous_quarter":{"amount":20000, "growth": 0.13},
        "ytd": {"amount":120000, "growth": 0.09},
        "raw_graph_data": REVENUE_GRAPH_DATA
        }


TRANSACTIONS_GRAPH_DATA = {
                "current_quarter": {0:20, 1:20, 2:20, 3:20, 4:20,5:20},
                "previous_quarter": {0:20, 1:20, 2:20, 3:20, 4:20,5:20},
                "ytd": {0:20, 1:20, 2:20, 3:20, 4:20,5:20},
}

TRANSACTIONS = {
        "current_quarter": {"amount":1100, "growth": 0.10},
        "previous_quarter":{"amount":1000, "growth": 0.13},
        "ytd": {"amount":3750, "growth": 0.09},
        "raw_graph_data": TRANSACTIONS_GRAPH_DATA
        }


TEMP_DICT = {
                "sales": SALES,
                "revenue":REVENUE,
                "transactions":TRANSACTIONS
}

def fetch_dashboard_data():

    return TEMP_DICT




if __name__ == "__main__":
   my_stuff =  fetch_dashboard_data()
   print(my_stuff)
