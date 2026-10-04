from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_legal_statutes(text: str, chunk_size: int = 1000, chunk_overlap: int = 100):
    # Legal statutes often have structured sections, we split on newlines and specific delimiters
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\nArticle ", "\n\nSection ", "\n\n", "\n", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return splitter.split_text(text)

