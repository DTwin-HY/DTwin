import pytest
import json
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
    usage_metadata={
        'input_tokens': 5146,
        'output_tokens': 13,
        'total_tokens': 5159,
        'input_token_details': {'audio': 0, 'cache_read': 0},
        'output_token_details': {'audio': 0, 'reasoning': 0}
    }
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
    assert not res

def test_extract_with_dict_image_content():
    image_dict = {
        "type": "image",
        "source_type": "base64",
        "data": "encoded_data_here",
        "mime_type": "image/jpeg"
    }
    message = AIMessage(content=[image_dict])
    result = fmt.extract(message)

    assert result["content"] == [image_dict]
    assert result["tool_calls"] == []

def test_extract_with_json_string_image_content():
    image_dict = {
        "type": "image",
        "source_type": "base64",
        "data": "string_encoded_data"
    }
    json_string = json.dumps(image_dict)
    message = AIMessage(content=json_string)
    result = fmt.extract(message)

    assert result["content"] == []
    assert result["image_data"] == image_dict
    assert result["tool_calls"] == []

def test_extract_with_invalid_json_string():
    invalid_json = '{"type": "image", but this is not valid json'
    message = AIMessage(content=invalid_json)
    result = fmt.extract(message)

    assert result["content"] == invalid_json
    assert "image_data" not in result
    assert result["tool_calls"] == []

def test_extract_with_non_image_json():
    non_image_dict = {"type": "text", "data": "some text"}
    json_string = json.dumps(non_image_dict)
    message = AIMessage(content=json_string)
    result = fmt.extract(message)

    assert result["content"] == json_string
    assert "image_data" not in result
    assert result["tool_calls"] == []

def test_extract_with_regular_string_content():
    content = "This is a regular message"
    message = AIMessage(content=content)
    result = fmt.extract(message)

    assert result["content"] == content
    assert "image_data" not in result
    assert result["tool_calls"] == []

def test_extract_with_json_string_containing_image():
    image_dict = {
        "_from_tool": True,
        "type": "image",
        "data": "tool_image_data",
        "format": "png"
    }
    json_string = json.dumps(image_dict)
    message = ToolMessage(content=json_string, tool_call_id="test123")
    result = fmt.extract(message)

    assert result["content"] == []
    assert result["image_data"] == image_dict
    assert result["tool_calls"] == []

def test_extract_message_with_no_content_attribute():
    """Test message without content attribute"""
    class MinimalMessage:
        pass

    message = MinimalMessage()
    result = fmt.extract(message)

    assert result["content"] == ""
    assert result["tool_calls"] == []
