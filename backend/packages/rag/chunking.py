from typing import List, Dict, Any

class LegalDocumentChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def chunk_document(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Mock implementation of chunking a document."""
        chunks = []
        if not text:
            return chunks
            
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "metadata": {**metadata, "start": start, "end": end}
            })
            start = end - self.overlap
            
        return chunks
