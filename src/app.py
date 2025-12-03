from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.routes.index import router

app = FastAPI(
    title='IsCoolGPT',
    description='Assistente inteligente de estudos em Cloud Computing',
    version='3.0.0'
)

app.include_router(router)


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={'error': 'Rota Não Encontrada'}
    )

