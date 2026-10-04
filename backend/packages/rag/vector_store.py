import os
import logging
from typing import List, Any, Optional, Iterable

from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class MockVectorStore(VectorStore):
    def add_texts(self, texts: Iterable[str], metadatas: Optional[List[dict]] = None, **kwargs: Any) -> List[str]:
        return []
    
    def similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> List[Document]:
        return [
            Document(page_content=f"Mock rule for: {query}. Ensure all safety guidelines are followed.", metadata={"citation": "Mock Statute Section 1"}),
            Document(page_content=f"Generic compliance requirement related to {query}.", metadata={"citation": "General Code 402"})
        ]

    async def asimilarity_search(self, query: str, k: int = 4, **kwargs: Any) -> List[Document]:
        return self.similarity_search(query, k=k, **kwargs)

    @classmethod
    def from_texts(cls, texts: List[str], embedding: Any, metadatas: Optional[List[dict]] = None, **kwargs: Any) -> "MockVectorStore":
        return cls()

def get_legal_vectorstore(connection_string: str = None, api_key: str = None) -> VectorStore:
    final_api_key = api_key or os.getenv("GOOGLE_API_KEY")
    if not final_api_key:
        logger.warning("GOOGLE_API_KEY not set. Falling back to mock vector store.")
        return MockVectorStore()
        
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=final_api_key
    )
    
    db_url = connection_string or os.getenv("DATABASE_URL")
    if not db_url:
        logger.warning("DATABASE_URL not set. Falling back to mock vector store.")
        return MockVectorStore()
        
    try:
        store = PGVector(
            embeddings=embeddings,
            collection_name="legal_statutes",
            connection=db_url,
            use_jsonb=True
        )
        return store
    except Exception as e:
        logger.error(f"Failed to initialize PGVector: {e}. Falling back to mock vector store.")
        return MockVectorStore()
