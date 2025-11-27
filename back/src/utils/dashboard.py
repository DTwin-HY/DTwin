from datetime import datetime, timedelta
import pandas as pd

from dateutil.relativedelta import relativedelta

from ..database.sales import (query_transactions, query_sales,
                        query_timeperiod_sales, query_timeperiod_transactions)

def fetch_dashboard_data() -> dict:
    """
    Used to fetch dashboard data to the api-layer.
    Returns:
        dict: A dictionary containing dashboard data
    """
    sales = create_sales_data()

    return sales


def get_quarter_dates() -> dict:
    """
    Returns a dictionary with start and end dates for current, previous, 
    and previous-previous quarters.

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
        'current': (current_quarter_start.strftime('%Y-%m-%d'), 
            current_quarter_end.strftime('%Y-%m-%d')),
        'previous': (previous_quarter_start.strftime('%Y-%m-%d'),
            previous_quarter_end.strftime('%Y-%m-%d')),
        'previous_previous': (previous_previous_start.strftime('%Y-%m-%d'), 
            previous_previous_end.strftime('%Y-%m-%d'))
    }



def create_weekly_graph_data(start:str , end:str , datatype:str , time_interval:str) -> list:
    """
    Creates a list of data, used to create datagraphs. 
    Args:
            start (str) : Start date of the graph dataset  
            end (str): End date of the graph dataset  
            datatype (str): Type of data to retrieve, based on query column names    
            time_interval (str): the time interval of the data, e.g. day, week, month or year   
    Returns:
            list: List containing data points for a graph
    """
    graph_data = []
    if datatype == 'transactions':
        query_data = query_timeperiod_transactions(start, end, time_interval)
    else:
        query_data = query_timeperiod_sales(start, end, time_interval)

    for row in query_data:
        graph_data.append(getattr(row, datatype))

    return graph_data


def build_dataset(df:pd.DataFrame, datatype: str) -> dict:
    """
    Builds the datasets for dashboard data
    Args:
        df: a pd.DataFrame object
        datatype: A column name from the df from which dataset is to be created
    Returns:
        dict: Returns a dict containing current quarter, previous quarter and YTD totals,
         growth % and graph data.
    """
    #Set times
    quarters =  get_quarter_dates()
    today = datetime.today()
    todays_date = today.strftime('%Y-%m-%d')
    end_of_previous_year = str(today.year-1) + '-12-31'

    #Calculate a comparable time slice of the previous quarter for growth % comparison
    time_into_quarter = (today - datetime.strptime(quarters['current'][0], '%Y-%m-%d')).days
    prev_q_comp_length = (datetime.strftime((datetime.strptime(quarters['previous'][0],'%Y-%m-%d')
                                 + timedelta(days=time_into_quarter)), '%Y-%m-%d'))

    #Calculate a comparable time slice of the previous year for ytd growth % comparison data
    time_into_year = (today - datetime(today.year, 1, 1)).days
    prev_year_comp_length = (datetime.strftime(datetime(today.year-1, 1, 1)
                                +timedelta(days=time_into_year), '%Y-%m-%d'))

    # Create timeslices from dataframe
    current_quarter = df[(df.timestamp >= quarters['current'][0])
                        & (df.timestamp <=quarters['current'][1])]

    prev_q_comparable = df[(df.timestamp >= quarters['previous'][0])
                        & (df.timestamp <= prev_q_comp_length)]
    previous_quarter = df[(df.timestamp >= quarters['previous'][0])
                        & (df.timestamp <=quarters['previous'][1])]

    previous_previous_quarter = df[(df.timestamp >= quarters['previous_previous'][0])
                        & (df.timestamp <=quarters['previous_previous'][1])]

    this_year = df[(df.timestamp > end_of_previous_year)]
    last_year_comparable = df[df.timestamp <= prev_year_comp_length]

    # Calc totals for datatype per time period
    current_q_total = int(current_quarter[datatype].sum())
    #Just used for current period growth % calc
    prev_q_comparable_total = int(prev_q_comparable[datatype].sum())

    previous_q_total = int(previous_quarter[datatype].sum())
    previous_previous_q_total = int(previous_previous_quarter[datatype].sum())

    this_year_total = int(this_year[datatype].sum())
    last_year_comparable_total = int(last_year_comparable[datatype].sum())

    #total growth per time period
    qurrent_q_r_growth = round((current_q_total / prev_q_comparable_total)-1,2)
    previous_q_r_growth = round((previous_q_total / previous_previous_q_total)-1,2)
    ytd_growth = round((this_year_total / last_year_comparable_total) -1,2)

    #Create graph data
    current_graph_data = create_weekly_graph_data(quarters['current'][0],
                        quarters['current'][1], datatype, 'week')
    previous_graph_data = create_weekly_graph_data(quarters['previous'][0],
                        quarters['previous'][1], datatype, 'week')
    ytd_graph_data = create_weekly_graph_data(str(today.year)
                        +'-01-01', todays_date, datatype, 'month')



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


def create_sales_data() -> dict:
    """
    Used to create a full dashboard dataset from sales data
    Returns:
            dict: Dict containing data for revenue, sales and transactions
    """
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
