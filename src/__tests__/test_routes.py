import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_endpoint():
    """Testa o endpoint raiz que retorna status da API"""
    response = client.get('/')
    
    assert response.status_code == 200
    assert response.json()['status'] == 'online'
    assert response.json()['service'] == 'IsCoolGPT'

def test_ask_endpoint_without_question():
    """Testa o endpoint /api/tutor/ask sem pergunta"""
    response = client.post('/api/tutor/ask', json={})
    
    assert response.status_code == 422  # FastAPI retorna 422 para validação

def test_ask_endpoint_with_empty_question():
    """Testa o endpoint /api/tutor/ask com pergunta vazia"""
    response = client.post('/api/tutor/ask', json={'question': ''})
    
    assert response.status_code == 422  # FastAPI valida com Pydantic
    
def test_ask_endpoint_with_whitespace_only():
    """Testa o endpoint /api/tutor/ask com apenas espaços"""
    response = client.post('/api/tutor/ask', json={'question': '   '})
    
    assert response.status_code == 422  # Validação do Pydantic

