from typing import TypedDict, Annotated, List, Dict
from langgraph.graph.message import add_messages

class LogEntry(TypedDict):
    """
    Object used inside logs list
    """
    product_id: str
    amount: int
    event_type: str
    timestamp: str

class InventoryItem(TypedDict):
    """
    Object used inside inventory dict
    """
    product_id: int
    name: str
    quantity: int
    price: float

class GeneralState(TypedDict):
    """
    general state
    """
    cash_register: float
    inventory: Dict[int, InventoryItem]
    logs: List[LogEntry]
    is_raining: bool
    supervisor_conversation: Annotated[list, add_messages]
