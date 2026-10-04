from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Any
from langgraph.types import interrupt
import asyncio

class State(TypedDict):
    val: str

async def node(state: State):
    ans = interrupt("Hello")
    return {"val": ans}

def build():
    builder = StateGraph(State)
    builder.add_node("node", node)
    builder.add_edge(START, "node")
    builder.add_edge("node", END)
    from langgraph.checkpoint.memory import MemorySaver
    return builder.compile(checkpointer=MemorySaver())

async def main():
    graph = build()
    cfg = {"configurable": {"thread_id": "1"}}
    res = await graph.ainvoke({"val": "init"}, cfg)
    print("res 1:", res)
    from langgraph.types import Command
    res2 = await graph.ainvoke(Command(resume="world"), cfg)
    print("res 2:", res2)

asyncio.run(main())
