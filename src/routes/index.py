from fastapi import APIRouter
from src.routes.tutor_routes import router as tutor_router

router = APIRouter()

# Health check / Info
@router.get('/')
async def root():
    return {
        'status': 'online',
        'service': 'IsCoolGPT',
        'version': '2.0.0',
        'endpoints': {
            'tutor': '/api/tutor/ask'
        }
    }

# Rotas do assistente
router.include_router(tutor_router, prefix='/api/tutor', tags=['tutor'])

