from pydantic import BaseModel, Field
from typing import List

class Reflection(BaseModel):
    missing: str = Field( description="Critique of what is missing")
    superfluous: str = Field( description="Critique of what is superfluous")

class AnswerQuestion(BaseModel):
    answer: str = Field( description="~250 word detailed answer to the question")
    reflection: Reflection = Field( description="your reflection on the initial answer")
    search_query: List[str] = Field( description="1-3 search queries for researching improvements to address the critique of your current answer")

class RevisorAnswer(AnswerQuestion):
    """Revisor your original answer to your question"""
    references: List[str] = Field( description="Citations motivating your update answer.")