from langchain_core.tools import tool
from packages.rag.vector_store import get_legal_vectorstore
import asyncio

@tool
async def search_compliance_rules(query: str) -> str:
    """
    Search the vector store for legal compliance rules relevant to the query.
    Use this tool to find regulations, statutes, and constraints for a given domain or product.
    """
    store = get_legal_vectorstore()
    # Try async search first
    if hasattr(store, "asimilarity_search"):
        docs = await store.asimilarity_search(query, k=3)
    else:
        # Fallback to sync if using a store that doesn't support async well
        docs = store.similarity_search(query, k=3)
        
    if not docs:
        return "No relevant compliance rules found."
        
    result = []
    for d in docs:
        citation = d.metadata.get('citation', 'Unknown Source')
        result.append(f"Source: {citation}\nRule: {d.page_content}")
        
    return "\n\n".join(result)
