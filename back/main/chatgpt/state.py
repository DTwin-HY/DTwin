from typing import TypedDict, Annotated, Dict, Any, List
from langgraph.graph.message import add_messages

class GeneralState(TypedDict):
    """
    general state shared across all conversations
    """
    conversations: List
    cash_register: float
    inventory: Dict[str, Dict[str, Any]]
    completed_transactions: List[Dict[str, Any]]
    is_raining: bool
    lat: float
    lon: float
    lat: float
    lon: float

class ConversationState(TypedDict):
    """
    conversation-specific state
    """
    messages: Annotated[list, add_messages]
    conversation_turn: int
    conversation_active: bool
    max_turns: int

def init_general_state(n, lat=None, lon=None) -> GeneralState:
    """
    inits the general state with n empty conversations and some initial cash and inventory
    """
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
    """
    inits the conversation-specific state with empty messages and turn count
    """
    return {
        "messages": [],
        "conversation_turn": 0,
        "conversation_active": True,
        "max_turns": 10
    }
