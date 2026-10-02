from typing import List, Dict, Any

class LegalDocumentChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def chunk_document(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Mock implementation of chunking a document."""
        if self.chunk_size <= 0 or self.overlap >= self.chunk_size:
            raise ValueError("chunk_size must be positive and overlap must be less than chunk_size")
            
        chunks = []
        if not text:
            return chunks
            
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "metadata": {**metadata, "start": start, "end": end}
            })
            if end == text_length:
                break
            start = end - self.overlap
            
        return chunks
