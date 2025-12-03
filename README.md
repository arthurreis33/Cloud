# 🎓 IsCoolGPT

> Tutor virtual de Cloud Computing para estudantes

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://docker.com/)

---

## Sobre

API de tutoria para auxiliar estudantes no aprendizado de **Cloud Computing**. Utiliza IA para responder perguntas sobre conceitos de computação em nuvem.

---

## Instalação

```bash
git clone <seu-repositorio-git>
cd IsCoolGPT

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

**Nota para macOS:** Use `python3` e `pip3` se `python` e `pip` não estiverem disponíveis. O ambiente virtual resolve isso automaticamente.

## Configuração

Crie o arquivo `.env` na raiz do projeto (veja `.env.example` como referência):

```env
OPENROUTER_API_KEY=sua_chave_openrouter_aqui
PORT=3000
APP_URL=http://localhost:3000
```

**Importante:** Nunca commite o arquivo `.env` com chaves reais. Use variáveis de ambiente ou secrets do seu provedor de CI/CD.

## Executar

```bash
# Dev
python main.py

# Ou com uvicorn diretamente
uvicorn src.app:app --reload --port 3000

# Docker
docker compose up -d
```

Acesse: http://localhost:3000

Documentação interativa: http://localhost:3000/docs

---

## API

### `GET /`

Status da API.

```json
{
  "status": "online",
  "service": "IsCoolGPT",
  "version": "2.0.0"
}
```

### `POST /api/tutor/ask`

Faz uma pergunta.

**Request:**
```json
{
  "question": "O que é Docker?"
}
```

**Response:**
```json
{
  "question": "O que é Docker?",
  "answer": "Docker é uma plataforma de containerização..."
}
```

---

## Scripts

| Comando | Descrição |
|---------|-----------|
| `python main.py` | Produção |
| `uvicorn src.app:app --reload` | Desenvolvimento |
| `pytest` | Testes |
| `pytest -v` | Testes verbosos |
| `pytest --cov=src` | Testes com cobertura |

---

## Estrutura do Projeto

```
IsCoolGPT/
├── main.py                 # Ponto de entrada
├── src/
│   ├── app.py              # Aplicação FastAPI
│   ├── routes/             # Rotas da API
│   ├── handlers/           # Handlers de requisições
│   ├── core/               # Serviços principais
│   ├── integrations/       # Integrações externas
│   ├── models/             # Modelos Pydantic
│   └── __tests__/          # Testes
├── requirements.txt        # Dependências
├── Dockerfile              # Configuração Docker
└── docker-compose.yml      # Orquestração Docker
```

---

## Autor

**Arthur Reis** - CESAR School 2025

---

## Licença

ISC
