from flask import jsonify
from ..index import app


SALES = {
        "current_quarter": {"amount":3300, "growth": 0.10},
        "previous_quarter":{"amount":3000, "growth": 0.13},
        "ytd": {"amount":11500, "growth": 0.09}
        }

REVENUE = {
        "current_quarter": {"amount":22000, "growth": 0.10},
        "previous_quarter":{"amount":20000, "growth": 0.13},
        "ytd": {"amount":120000, "growth": 0.09}
        }

TRANSACTIONS = {
        "current_quarter": {"amount":1100, "growth": 0.10},
        "previous_quarter":{"amount":1000, "growth": 0.13},
        "ytd": {"amount":3750, "growth": 0.09}
        }


TEMP_DICT = {
                "sales": SALES,
                "revenue":REVENUE,
                "transactions":TRANSACTIONS
}

def fetch_dashboard_data(start,end):

    return TEMP_DICT




if __name__ == "__main__":
   my_stuff =  fetch_dashboard_data()
   print(my_stuff)
