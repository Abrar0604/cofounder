import os
import argparse
import asyncio
from langchain_core.documents import Document
from packages.rag.vector_store import get_legal_vectorstore

# Sample dummy compliance rules for FSSAI / FDA testing
DUMMY_RULES = [
    Document(
        page_content="Any cold-chain distribution process extending beyond 30 days requires mandatory accelerated shelf-life testing and pathogen challenge studies prior to launch.",
        metadata={"citation": "FSSAI Safety Guideline 102.3"}
    ),
    Document(
        page_content="Products positioned as 'Premium' must transparently disclose the origin of raw materials on the primary packaging panel.",
        metadata={"citation": "Consumer Protection Act Sec 42"}
    ),
    Document(
        page_content="Caffeine content in ready-to-drink beverages must not exceed 145mg per 250ml. If exceeded, a strict statutory warning is required on the label.",
        metadata={"citation": "FSSAI Caffeine Mandate 2023"}
    )
]

async def ingest_documents():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set. Skipping ingestion (using mock vector store in dev).")
        return
        
    store = get_legal_vectorstore(db_url)
    
    if hasattr(store, 'add_documents'):
        print(f"Ingesting {len(DUMMY_RULES)} compliance rules into PGVector...")
        store.add_documents(DUMMY_RULES)
        print("Ingestion complete!")
    else:
        print("Store returned is a mock store. Skipping actual ingestion.")

if __name__ == "__main__":
    asyncio.run(ingest_documents())
