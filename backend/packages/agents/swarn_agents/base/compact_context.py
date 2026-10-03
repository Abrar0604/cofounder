from typing import List, Any
from packages.decisions.swarn_decisions.definitions.select_context_to_keep import ContextItemState

def get_message_kind(msg: Any) -> str:
    # Minimal helper to map standard message types
    t = getattr(msg, "type", "")
    if t == "human": return "human"
    if t == "ai": return "ai"
    if t == "tool": return "tool"
    return "other"

async def compact_messages(
    deps, 
    session, 
    ctx, 
    venture_id: str, 
    messages: list, 
    max_messages: int = 24
) -> list:
    if len(messages) <= max_messages:
        return messages
        
    keep_indices = set()
    
    # Always keep system message if present at index 0
    start_idx = 0
    if len(messages) > 0 and getattr(messages[0], "type", "") == "system":
        keep_indices.add(0)
        start_idx = 1
        
    # Always keep the last 6 messages
    for i in range(max(start_idx, len(messages) - 6), len(messages)):
        keep_indices.add(i)
        
    # Always keep tool calls awaiting results
    # and human messages containing an approval decision
    tool_call_ids_pending = set()
    for i, msg in enumerate(messages):
        # Human approval decision check
        if getattr(msg, "type", "") == "human":
            content = str(getattr(msg, "content", ""))
            if "approval_id" in content and "decision" in content:
                keep_indices.add(i)
                
        # Collect tool_calls
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_call_ids_pending.add(tc.get("id"))
                
        # If it's a tool response, we resolve the pending call
        if getattr(msg, "type", "") == "tool":
            tc_id = getattr(msg, "tool_call_id", None)
            if tc_id in tool_call_ids_pending:
                tool_call_ids_pending.remove(tc_id)
                
    # Re-iterate to keep messages that have pending tool calls
    for i, msg in enumerate(messages):
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc.get("id") in tool_call_ids_pending:
                    keep_indices.add(i)
                    break
                    
    # The older candidates we might drop
    candidates = []
    for i in range(start_idx, len(messages)):
        if i not in keep_indices:
            candidates.append(i)
            
    if not candidates:
        return [m for i, m in enumerate(messages) if i in keep_indices]
        
    # Prepare D10 batched call
    d10_states = []
    for age_index, msg_idx in enumerate(candidates):
        msg = messages[msg_idx]
        kind = get_message_kind(msg)
        if kind not in ('human', 'ai', 'tool'):
            kind = 'ai'  # fallback
            
        content = str(getattr(msg, "content", ""))
        d10_states.append(ContextItemState(
            kind=kind,
            age_index=age_index,
            length_chars=len(content),
            excerpt=content[:600]
        ))
        
    # Batch run decisions
    # Assuming deps.decisions.run_batch is implemented
    decisions = await deps.decisions.run_batch('select_context_to_keep', d10_states)
    
    for idx, (msg_idx, decision) in enumerate(zip(candidates, decisions)):
        if decision.choice == 'drop' and decision.outcome == 'AUTO':
            # drop it (do nothing)
            pass
        else:
            # Keep 'keep', 'other', and low-confidence items
            keep_indices.add(msg_idx)
            
    # Enforce tool pairs: never leave either side of a completed pair kept alone
    ai_to_tool_calls = {}
    tool_call_id_to_ai_idx = {}
    tool_call_id_to_tool_idx = {}

    for i, msg in enumerate(messages):
        if getattr(msg, "type", "") == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
            ai_to_tool_calls[i] = [tc.get("id") for tc in msg.tool_calls]
            for tc_id in ai_to_tool_calls[i]:
                tool_call_id_to_ai_idx[tc_id] = i
        
        if getattr(msg, "type", "") == "tool":
            tc_id = getattr(msg, "tool_call_id", None)
            if tc_id:
                if tc_id not in tool_call_id_to_tool_idx:
                    tool_call_id_to_tool_idx[tc_id] = []
                tool_call_id_to_tool_idx[tc_id].append(i)

    changed = True
    while changed:
        changed = False
        new_keeps = set()
        for i in keep_indices:
            # If we keep an AI message, keep its tool results
            if i in ai_to_tool_calls:
                for tc_id in ai_to_tool_calls[i]:
                    for t_idx in tool_call_id_to_tool_idx.get(tc_id, []):
                        if t_idx not in keep_indices and t_idx not in new_keeps:
                            new_keeps.add(t_idx)
                            
            # If we keep a tool message, keep its AI message
            msg = messages[i]
            if getattr(msg, "type", "") == "tool":
                tc_id = getattr(msg, "tool_call_id", None)
                if tc_id in tool_call_id_to_ai_idx:
                    ai_idx = tool_call_id_to_ai_idx[tc_id]
                    if ai_idx not in keep_indices and ai_idx not in new_keeps:
                        new_keeps.add(ai_idx)
        if new_keeps:
            keep_indices.update(new_keeps)
            changed = True
            
    # Rebuild messages
    final_messages = [m for i, m in enumerate(messages) if i in keep_indices]
    return final_messages
