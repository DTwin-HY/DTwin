from src.utils.check_pending_tool_call import check_pending_tool_call

class DummySnapshot:
    def __init__(self, messages):
        self.values = {"messages": list(messages)}


class AssistantMsg:
    def __init__(self, id, tool_calls=None, additional_kwargs=None, content=""):
        self.id = id
        self.content = content
        self.tool_calls = tool_calls or []
        self.additional_kwargs = additional_kwargs or {}

class ToolMessage:
    # Only shape the code under test probes: class name and tool_call_id
    def __init__(self, tool_call_id, content="ok"):
        self.tool_call_id = tool_call_id
        self.content = content

def test_check_pending_tool_call_true():
    # History: assistant called tool tc-a and got answered; later tc-b pending, no answer
    history = [
        AssistantMsg("a1", tool_calls=[{"id": "tc-a"}]),
        ToolMessage(tool_call_id="tc-a"),
        AssistantMsg("a2", tool_calls=[{"id": "tc-b"}]),  # pending
    ]
    snap = DummySnapshot(history)
    assert check_pending_tool_call(snap) is True

def test_check_pending_tool_call_false():
    # faulty object
    snap2 = {"faulty": "object"}
    assert check_pending_tool_call(snap2) is False

    # no messages
    snap3 = DummySnapshot([])
    assert check_pending_tool_call(snap3) is False
