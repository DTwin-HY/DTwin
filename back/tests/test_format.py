import pytest
from langchain_core.messages import AIMessage, ToolMessage
from ..src.utils import format as fmt

#realistic agent message and chunk
tool_calls_mock = [
    {
        'name': 'transfer_to_storage_agent',
        'args': {},
        'id': 'test1',
        'type': 'tool_call'
    }
]
agent_message = AIMessage(
    content='',
    additional_kwargs={},
    response_metadata={},
    name='supervisor',
    id='test123',
    tool_calls=tool_calls_mock,
    usage_metadata={'input_tokens': 5146, 'output_tokens': 13, 'total_tokens': 5159, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}}
)
agent_chunk = (('supervisor:test',), {'agent': {'messages': [agent_message]}})

#realistic tool message and chunk
content_mock = '{"status": "ok", "inventory": {"A100": 50, "B200": 20, "C300": 0}}'
tool_message = ToolMessage(
    content=content_mock,
    name='list_inventory',
    id='test123',
    tool_call_id='test1'
)
tool_chunk = (('storage_agent:test',), {'tools': {'messages': [tool_message]}})

def test_extract_ai():
    m = agent_message
    out = fmt.extract(m)
    assert out["content"] == ""
    assert out["tool_calls"] == tool_calls_mock

def test_extract_tool():
    m = tool_message
    out = fmt.extract(m)
    assert out["content"] == content_mock
    assert out["tool_calls"] == []

def test_format_chunk_agent():
    res = fmt.format_chunk(agent_chunk)
    res = res[0]
    assert res["subgraph"] == "supervisor"
    assert res["node"] == "agent"
    assert res["kind"] == "agent"
    assert res["messages"] == [{"content": "", "tool_calls": tool_calls_mock}]

def test_format_chunk_tools():
    res = fmt.format_chunk(tool_chunk)
    res = res[0]
    assert res["subgraph"] == "storage_agent"
    assert res["node"] == "tools"
    assert res["kind"] == "tools"
    assert res["messages"] == [{"content": content_mock, "tool_calls": []}]

def test_format_chunk_other_type():
    other_chunk = (('other_node:test',), {'other_node': {'messages': [agent_message]}})
    res = fmt.format_chunk(other_chunk)
    res = res[0]
    assert res["kind"] == "other"

def test_format_chunk_multiple_messages():
    multi_message_chunk = (('supervisor:test',), {'agent': {'messages': [agent_message]*3}})
    res = fmt.format_chunk(multi_message_chunk)
    assert len(res[0]["messages"]) == 3

def test_format_chunk_last_message():
    multi_message_chunk = (('supervisor:test',), {'agent': {'messages': [agent_message]*3}})
    res = fmt.format_chunk(multi_message_chunk, last_message=True)
    assert len(res[0]["messages"]) == 1

def test_format_chunk_empty_namespace():
    empty_ns_chunk = ((), {'agent': {'messages': agent_message}})
    res = fmt.format_chunk(empty_ns_chunk)
    assert res == []
