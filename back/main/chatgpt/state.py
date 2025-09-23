from typing import TypedDict, Annotated, Dict, Any, List
from langgraph.graph.message import add_messages

class GeneralState(TypedDict):
    conversations: List
    cash_register: float
    inventory: Dict[str, Dict[str, Any]]
    completed_transactions: List[Dict[str, Any]]
    is_raining: bool
    lat: float
    lon: float

class ConversationState(TypedDict):
    messages: Annotated[list, add_messages]
    conversation_turn: int
    conversation_active: bool
    max_turns: int

def init_general_state(n, lat=None, lon=None) -> GeneralState:
    state = {
        "conversations": n*[None],
        "cash_register": 400.0,
        "inventory": {
            "strawberries_small": {"stock": 20, "price": 3.0, "name": "Small box"},
            "strawberries_medium": {"stock": 15, "price": 5.0, "name": "Medium box"},
        },
        "completed_transactions": [],
        "is_raining": False
    }
    if lat is not None:
        state["lat"] = lat
    if lon is not None:
        state["lon"] = lon
    return state

def init_conversation_state() -> ConversationState:
    return {
        "messages": [],
        "conversation_turn": 0,
        "conversation_active": True,
        "max_turns": 10
    }
