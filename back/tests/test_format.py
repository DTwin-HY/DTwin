'''
import pytest
from langchain_core.messages import AIMessage, ToolMessage
from src.utils import format as fmt

make_agent_chunk = (('supervisor:test',), {'agent': {'messages':[AIMessage(
    content='',
    additional_kwargs={},
    response_metadata={},
    name='supervisor',
    id='test',
    tool_calls=[
        {
            'name': 'transfer_to_storage_agent',
            'args': {},
            'id': 'call_IZlc5jH5jbmaBAf3SykE39dg',
            'type': 'tool_call'
        }
    ],
    usage_metadata={}
)]}})

(('storage_agent:60753d78-8101-c99e-1cc4-9c908e8609b7',), {'agent': {'messages': [AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_bUzxvbZReE5siyT58AuLImYU', 'function': {'arguments': '{}', 'name': 'list_inventory'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 659, 'prompt_tokens': 4234, 'total_tokens': 4893, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 640, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-5-nano-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-CT7iyDyuRefZiPyTZlzX3wam11ugU', 'service_tier': 'default', 'finish_reason': 'tool_calls', 'logprobs': None}, name='storage_agent', id='run--02480a9b-b4e8-4715-a3ad-4e98555360cf-0', tool_calls=[{'name': 'list_inventory', 'args': {}, 'id': 'call_bUzxvbZReE5siyT58AuLImYU', 'type': 'tool_call'}], usage_metadata={'input_tokens': 4234, 'output_tokens': 659, 'total_tokens': 4893, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 640}})]}})
(('storage_agent:60753d78-8101-c99e-1cc4-9c908e8609b7',), {'tools': {'messages': [ToolMessage(content='{"status": "ok", "inventory": {"A100": 50, "B200": 20, "C300": 0}}', name='list_inventory', id='665bcd51-9c84-4fd4-95d9-f06d61cf382b', tool_call_id='call_bUzxvbZReE5siyT58AuLImYU')]}})
(('storage_agent:60753d78-8101-c99e-1cc4-9c908e8609b7',), {'agent': {'messages': [AIMessage(content='{ "A100": 50, "B200": 20, "C300": 0 }', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 479, 'prompt_tokens': 4291, 'total_tokens': 4770, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 448, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-5-nano-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-CT7j5cCY20Z0fzejHMa5Wy1CQnxbF', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None}, name='storage_agent', id='run--73466d9f-985c-454c-a33a-b44149ce8fc8-0', usage_metadata={'input_tokens': 4291, 'output_tokens': 479, 'total_tokens': 4770, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 448}})]}})
(('supervisor:368f6a92-4cba-b6ab-5cc7-4a3b59f73d3a',), {'agent': {'messages': [AIMessage(content='The current inventory of the warehouse is:\n- A100: 50 units\n- B200: 20 units\n- C300: 0 units\n\nLet me know if you need further action or information!', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 44, 'prompt_tokens': 3827, 'total_tokens': 3871, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4.1-2025-04-14', 'system_fingerprint': 'fp_422e2d36a8', 'id': 'chatcmpl-CT7jAzwWzMCqCGbD3ufhek0spp95N', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None}, name='supervisor', id='run--9db0d059-ca24-47c6-8a92-e3acef2d4a58-0', usage_metadata={'input_tokens': 3827, 'output_tokens': 44, 'total_tokens': 3871, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})]}})
def test_extract_ai():
    m = AIMessage(tool_calls=[{"name": "list_inventory"}])
    out = fmt.extract(m)
    assert out["content"] == []
    assert out["tool_calls"] == [{"name": "list_inventory"}]


def test_extract_without_attributes():
    m = ToolMessage(content="Moi")
    out = fmt.extract(m)
    assert out["content"] == []
    assert out["tool_calls"] == "Moi"


def test_format_chunk_basic(monkeypatch):
    #monkeypatch.setattr(fmt, "convert_to_messages", lambda msgs: msgs)

    chunk = (
        ("supervisor:abcd",),
        {
            "agent": {"messages": [AIMessage(content="agent says hi", tool_calls=[])]},
            "tools": {"messages": [ToolMessage(content='{"status":"ok","inventory":{}}', tool_calls=[])]},
        },
    )

    res = fmt.format_chunk(chunk)
    assert isinstance(res, list)
    # two nodes -> two entries
    assert len(res) == 2

    agent_entry = next((r for r in res if r["node"] == "agent"), None)
    tools_entry = next((r for r in res if r["node"] == "tools"), None)

    assert agent_entry is not None
    assert agent_entry["subgraph"] == "supervisor"
    assert agent_entry["kind"] == "agent"
    assert agent_entry["messages"] == [{"content": "agent says hi", "tool_calls": []}]

    assert tools_entry is not None
    assert tools_entry["kind"] == "tools"
    assert tools_entry["messages"] == [{"content": '{"status":"ok","inventory":{}}', "tool_calls": []}]


def test_format_chunk_last_message(monkeypatch):
    monkeypatch.setattr(fmt, "convert_to_messages", lambda msgs: msgs)

    chunk = (
        ("storage_agent:xyz",),
        {
            "agent": {
                "messages": [
                    make_ai(content="first", tool_calls=[]),
                    make_ai(content="second", tool_calls=[]),
                ]
            }
        },
    )

    res = fmt.format_chunk(chunk, last_message=True)
    assert len(res) == 1
    assert res[0]["messages"] == [{"content": "second", "tool_calls": []}]


def test_format_chunk_empty_namespace(monkeypatch):
    monkeypatch.setattr(fmt, "convert_to_messages", lambda msgs: msgs)
    # empty namespace should return empty list per implementation
    chunk = ((), {"agent": {"messages": [make_ai(content="x", tool_calls=[])]}})
    res = fmt.format_chunk(chunk)
    assert res == []
'''