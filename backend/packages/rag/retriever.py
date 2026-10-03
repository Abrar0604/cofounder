from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

def get_legal_vectorstore(connection_string: str, api_key: str = None):
    final_api_key = api_key or os.getenv("GOOGLE_API_KEY")
    if not final_api_key:
        raise ValueError("GOOGLE_API_KEY must be set in the environment or passed directly")
        
    # Initializes pgvector store for legal documents
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=final_api_key
    )
    
    return PGVector(
        embeddings=embeddings,
        collection_name="legal_statutes",
        connection=connection_string,
        use_jsonb=True
    )
