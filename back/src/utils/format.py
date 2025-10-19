from langchain_core.messages import convert_to_messages


def format_chunk(chunk, last_message=False):
    """
    Takes an chunk as an input and returns a list of structured dicts for frontend rendering.
    """
    result = []
    subgraph = None
    if isinstance(chunk, tuple):
        ns, chunk = chunk
        if len(ns) == 0:
            return []
        subgraph = ns[-1].split(":")[0]

    for node_name, node_update in chunk.items():
        print("Currently running", subgraph, node_name)
        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]
        result.append({
            "subgraph": subgraph,
            "node": node_name,
            "messages": [extract(m) for m in messages]
        })
    return result

def extract(message):
    """
    return only the content and tool calls from an AI/tool message
    """
    content = getattr(message, "content", [])
    tool_calls = getattr(message, "tool_calls", [])

    return {
        "content": content,
        "tool_calls": tool_calls
    }
