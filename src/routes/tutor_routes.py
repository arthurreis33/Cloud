from fastapi import APIRouter
from src.handlers.tutor_handler import handle_question
from src.models.request import QuestionRequest

router = APIRouter()

# POST /api/tutor/ask - Envia uma consulta ao assistente
@router.post('/ask')
async def ask_endpoint(request_data: QuestionRequest):
    return await handle_question(request_data)

