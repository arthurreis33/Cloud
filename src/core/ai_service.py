from src.integrations.open_router_provider import create_response

# Serviço de processamento de IA
async def process_question(instruction: str, user_query: str) -> str:
    return await create_response(instruction, user_query)
