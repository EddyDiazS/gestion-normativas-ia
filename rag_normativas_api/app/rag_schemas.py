from pydantic import BaseModel
from typing import Optional, List


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5
    session_id: Optional[str] = None


class Source(BaseModel):
    document: str
    article: str


class AnswerResponse(BaseModel):
    answer: str
    verified: bool
    sources: Optional[List[Source]] = None
