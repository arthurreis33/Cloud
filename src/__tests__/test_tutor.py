import pytest
from unittest.mock import AsyncMock, patch
from src.core.ai_service import process_question

@pytest.mark.asyncio
async def test_process_question_service():
    """Testa o serviço de processamento de IA com mock"""
    with patch('src.integrations.open_router_provider.create_response') as mock_create:
        mock_create.return_value = 'Resposta mockada do assistente'
        
        response = await process_question(
            'Você é um assistente',
            'O que é cloud?'
        )
        
        assert response == 'Resposta mockada do assistente'
        mock_create.assert_called_once_with('Você é um assistente', 'O que é cloud?')
