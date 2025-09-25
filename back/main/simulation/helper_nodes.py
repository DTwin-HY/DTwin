from .state import GeneralState, LogEntry

def update_inventory(state: GeneralState, product_id: int, change: int) -> GeneralState:
    """
    Update inventory quantities.
    Raises ValueError if the resulting quantity would be negative.
    """
    if product_id in state['inventory']:
        new_quantity = state['inventory'][product_id]['quantity'] + change
        if new_quantity < 0:
            raise ValueError(f"Cannot reduce Product ID {product_id} below zero")
        state['inventory'][product_id]['quantity'] = new_quantity
        return state
    else:
        raise KeyError(f"Product ID {product_id} not found in inventory.")

def add_log(state: GeneralState, new_log: LogEntry) -> GeneralState:
    """
    Add a new log entry to the logs list.
    """
    state['logs'].append(new_log)
    return state

def update_cash_register(state: GeneralState, change: float) -> GeneralState:
    """
    Add or subtract from the cash register
    """
    if state['cash_register'] + change < 0:
        raise ValueError("Cash register cannot go negative")
    state['cash_register'] += change
    return state
