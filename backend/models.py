from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str
    k: int = 12
