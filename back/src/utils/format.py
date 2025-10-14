from langchain_core.messages import convert_to_messages


def format_chunk(update, last_message=False):
    """
    Returns a structured dict for frontend rendering.
    Looks terrible but works, should be fixed later
    """
    result = []
    subgraph = None
    if isinstance(update, tuple):
        ns, update = update
        if len(ns) == 0:
            return []
        subgraph = ns[-1].split(":")[0]

    for node_name, node_update in update.items():
        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]
        result.append({
            "subgraph": subgraph,
            "node": node_name,
            "messages": [m.pretty_repr(html=True) for m in messages]
        })
    return result
