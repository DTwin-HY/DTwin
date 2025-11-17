def check_pending_tool_call(snapshot) -> bool:
    """
    Return True if there exists ANY pending tool call (from any assistant message),
    i.e. a tool_call id that has no matching ToolMessage later in the history.

    Assumes `snapshot` is supervisor.get_state(config) and snapshot.values["messages"]
    is an ordered list of messages.
    """
    try:
        messages = snapshot.values.get("messages", [])
    except Exception:
        return False

    if not messages:
        return False

    tool_call_ids = []
    responded_ids = set()

    for msg in messages:
        # Collect tool call ids from assistant messages
        if getattr(msg, "tool_calls", None):
            for c in msg.tool_calls:
                cid = getattr(c, "id", None) or (c.get("id") if isinstance(c, dict) else None)
                if cid:
                    tool_call_ids.append(cid)
        else:
            ak = getattr(msg, "additional_kwargs", None)
            if isinstance(ak, dict):
                for c in ak.get("tool_calls", []) or []:
                    cid = c.get("id") or c.get("tool_call_id")
                    if cid:
                        tool_call_ids.append(cid)

        # Collect tool_call_id from ToolMessage responses
        if msg.__class__.__name__ == "ToolMessage":
            tcid = getattr(msg, "tool_call_id", None) or (msg.additional_kwargs.get("tool_call_id") if hasattr(msg, "additional_kwargs") and isinstance(msg.additional_kwargs, dict) else None)
            if tcid:
                responded_ids.add(tcid)

        # Dict-style tool message
        if isinstance(msg, dict) and msg.get("type") == "tool":
            tcid = msg.get("tool_call_id") or msg.get("id")
            if tcid:
                responded_ids.add(tcid)

    # Any tool_call id not answered?
    for cid in tool_call_ids:
        if cid not in responded_ids:
            return True
    return False