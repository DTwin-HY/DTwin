from typing import TypedDict, Annotated, Dict, Any, List
from langgraph.graph.message import add_messages

class ConversationState(TypedDict):
    messages: Annotated[list, add_messages]
    cash_register: float
    inventory: Dict[str, Dict[str, Any]]
    conversation_turn: int
    conversation_active: bool
    max_turns: int
    completed_transactions: List[Dict[str, Any]]

def init_cash_and_inventory_state() -> ConversationState:
    return {
        "messages": [],
        "cash_register": 400.0,
        "inventory": {
            "strawberries_small": {"stock": 20, "price": 3.0, "name": "Small box"},
            "strawberries_medium": {"stock": 15, "price": 5.0, "name": "Medium box"},
        },
        "conversation_turn": 0,
        "conversation_active": True,
        "max_turns": 8,
        "completed_transactions": []
    }