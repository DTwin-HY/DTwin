from typing import TypedDict, Annotated, Dict, Any, List
from langgraph.graph.message import add_messages

class GeneralState(TypedDict):
    conversations: List
    cash_register: float
    inventory: Dict[str, Dict[str, Any]]
    completed_transactions: List[Dict[str, Any]]

class ConversationState(TypedDict):
    messages: Annotated[list, add_messages]
    conversation_turn: int
    conversation_active: bool
    max_turns: int

def init_general_state() -> GeneralState:
    return {
        "conversations": [],
        "cash_register": 400.0,
        "inventory": {
            "strawberries_small": {"stock": 20, "price": 3.0, "name": "Small box"},
            "strawberries_medium": {"stock": 15, "price": 5.0, "name": "Medium box"},
        },
        "completed_transactions": []
    }

def init_conversation_state() -> ConversationState:
    return {
        "messages": [],
        "conversation_turn": 0,
        "conversation_active": True,
        "max_turns": 10
    }
