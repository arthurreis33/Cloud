from pydantic import BaseModel, Field, field_validator

class QuestionRequest(BaseModel):
    question: str = Field(..., description='Consulta para o assistente', min_length=1)
    
    @field_validator('question')
    @classmethod
    def validate_question_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Envie uma pergunta no campo "question"')
        return v.strip()

