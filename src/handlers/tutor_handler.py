from fastapi import HTTPException
from src.core.ai_service import process_question
from src.models.request import QuestionRequest

# Handler de consultas ao assistente
async def handle_question(request_data: QuestionRequest):
    user_query = request_data.question

    print('[Assistente] Nova consulta recebida')
    print(f'[Assistente] Analisando consulta: {user_query[:50]}...')

    instruction_prompt = 'Você é um assistente especializado em Computação em Nuvem. Forneça explicações detalhadas, práticas e acessíveis para alunos de graduação. Use exemplos reais sempre que possível e estruture suas respostas de forma organizada.'

    try:
        response_text = await process_question(instruction_prompt, user_query)
        print('[Assistente] Resposta processada com sucesso')

        return {
            'question': user_query,
            'answer': response_text
        }

    except Exception as err:
        print(f'[Assistente] Erro ao processar consulta: {str(err)}')
        raise HTTPException(
            status_code=500,
            detail='Erro ao processar consulta, tente novamente mais tarde'
        )
