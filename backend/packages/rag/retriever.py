from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

def get_legal_vectorstore(connection_string: str):
    # Initializes pgvector store for legal documents
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY", "dummy")
    )
    
    return PGVector(
        embeddings=embeddings,
        collection_name="legal_statutes",
        connection=connection_string,
        use_jsonb=True
    )
