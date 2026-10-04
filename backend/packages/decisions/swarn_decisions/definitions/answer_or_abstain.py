from pydantic import BaseModel
from typing import List

class DocumentInfo(BaseModel):
    content: str
    citation: str

class AnswerOrAbstainState(BaseModel):
    task: str
    documents: List[DocumentInfo]

