from packages.agents.swarn_agents.base.agent_state import AgentState
from packages.rag.retriever import get_legal_vectorstore
import os

async def retrieve_statutes(deps, state: AgentState) -> dict:
    query = state.get("task", "")
    events = list(state.get("events", []))
    
    docs = []
    
    # We can use deps.settings to get the DB URL. If not available, fallback to os env.
    db_url = getattr(deps.settings, "database_url", None) if deps.settings else os.getenv("DATABASE_URL")
    
    if db_url:
        store = get_legal_vectorstore(db_url)
        docs = await store.asimilarity_search(query, k=3)
    
    events.append({
        "type": "legal_statutes_retrieved",
        "payload": {
            "query": query,
            "documents": [{"content": d.page_content, "citation": d.metadata.get("citation", "Unknown")} for d in docs]
        }
    })
    
    return {"events": events}
