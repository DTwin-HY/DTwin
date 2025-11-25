from flask import jsonify
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from ..index import app
from ..database.sales import query_transactions, query_sales


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
        sales = create_sales_data()

        return sales


def get_quarter_dates() -> dict:
    """
    Returns a dictionary with start and end dates for current, previous, and previous-previous quarters.

    Returns:
        dict: Dictionary with quarter ranges as tuples of (start_date, end_date) strings
    """
    # Parse input date
    date = datetime.today()
    
    # Determine current quarter
    current_quarter = (date.month - 1) // 3 + 1
    
    # Calculate start of current quarter
    current_quarter_start = datetime(date.year, (current_quarter - 1) * 3 + 1, 1)
    current_quarter_end = current_quarter_start + relativedelta(months=3) - timedelta(days=1)
    
    # Previous quarter
    previous_quarter_start = current_quarter_start - relativedelta(months=3)
    previous_quarter_end = current_quarter_start - timedelta(days=1)
    
    # Previous-previous quarter
    previous_previous_start = previous_quarter_start - relativedelta(months=3)
    previous_previous_end = previous_quarter_start - timedelta(days=1)

    
    
    return {
        'current': (current_quarter_start.strftime('%Y-%m-%d'), current_quarter_end.strftime('%Y-%m-%d')),
        'previous': (previous_quarter_start.strftime('%Y-%m-%d'), previous_quarter_end.strftime('%Y-%m-%d')),
        'previous_previous': (previous_previous_start.strftime('%Y-%m-%d'), previous_previous_end.strftime('%Y-%m-%d'))
    }

def create_raw_graph_data(column: list) -> list:
        result = []
        first = True
        for entry in column:
                if first:
                        value = entry
                        first = False
                else:
                        value = entry + result[-1]
                result.append(value)
        
        return result

def build_dataset(df:pd.DataFrame, type: str):
        #Set times
        quarters =  get_quarter_dates()
        today = datetime.today()
        todays_date = today.strftime('%Y-%m-%d')
        end_of_previous_year = str(today.year-1) + '-12-31'

        # Set time slices
        current_quarter = df[(df.timestamp >= quarters['current'][0]) & (df.timestamp <=quarters['current'][1])]
        previous_quarter = df[(df.timestamp >= quarters['previous'][0]) & (df.timestamp <=quarters['previous'][1])]
        previous_previous_quarter = df[(df.timestamp >= quarters['previous_previous'][0]) & (df.timestamp <=quarters['previous_previous'][1])]
        
        this_year = df[(df.timestamp > end_of_previous_year)]
        last_year = df[(df.timestamp <= end_of_previous_year)]

        # Calc total revenues per time period
        current_q_total = int(current_quarter[type].sum())
        previous_q_total = int(previous_quarter[type].sum())
        previous_previous_q_total = int(previous_previous_quarter[type].sum())
        this_year_total = int(this_year[type].sum())
        last_year_total = int(last_year[type].sum())

        #total growth per time period
        qurrent_q_r_growth = round((current_q_total / previous_q_total)-1,2)
        previous_q_r_growth = round((previous_q_total / previous_previous_q_total)-1,2)
        ytd_growth = round((this_year_total / last_year_total) -1,2)

        #Create graph data
        current_graph_data = create_raw_graph_data(current_quarter[type])
        previous_graph_data = create_raw_graph_data(previous_quarter[type])
        ytd_graph_data = create_raw_graph_data(this_year[type])



        return {
                'current_quarter': 
                        {'amount': current_q_total, 'growth':qurrent_q_r_growth},
                'previous_quarter':
                        {'amount': previous_q_total, 'growth': previous_q_r_growth},
                'ytd': 
                        {'amount': this_year_total, 'growth':ytd_growth},
                'raw_graph_data': {
                        'current_quarter': current_graph_data,
                        'previous_quarter':previous_graph_data,
                        'ytd':ytd_graph_data
                        }

                }



def create_sales_data():
        #Set time stuff
        today = datetime.today()
        todays_date = today.strftime('%Y-%m-%d')
        last_year = str(today.year-1) + '-01-01'

        #Retrieve raw query data from database
        raw_sales_query = query_sales(last_year,todays_date)
        raw_transactions_query = query_transactions(last_year,todays_date)

        #Set data into DF
        df = pd.DataFrame.from_records(raw_sales_query, columns=["timestamp","quantity","revenue"])
        tdf = pd.DataFrame.from_records(raw_transactions_query, columns=["timestamp", "transactions"])
     
        #Set data:
        result = {}
        result["revenue"] = build_dataset(df,'revenue')
        result["sales"] = build_dataset(df,'quantity')
        result["transactions"] = build_dataset(tdf, 'transactions')
        

        return result



if __name__ == "__main__":
        test_function()