# 🎓 IsCoolGPT

> Tutor virtual de Cloud Computing para estudantes

[![Node.js](https://img.shields.io/badge/Node.js-20+-339933?logo=node.js)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://docker.com/)

---

## Sobre

API de tutoria para auxiliar estudantes no aprendizado de **Cloud Computing**. Utiliza IA para responder perguntas sobre conceitos de computação em nuvem.

---

## Instalação

```bash
git clone https://github.com/Diegofescorel/IsCoolGPT.git
cd IsCoolGPT
npm install
```

## Configuração

Crie o arquivo `.env`:

```env
OPENROUTER_API_KEY=sua_chave
PORT=3000
```

## Executar

```bash
# Dev
npm run dev

# Docker
docker compose up -d
```

Acesse: http://localhost:3000

---

## API

### `GET /`

Status da API.

```json
{
  "status": "online",
  "service": "IsCoolGPT",
  "version": "1.0.0"
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
| `npm start` | Produção |
| `npm run dev` | Desenvolvimento |
| `npm test` | Testes |

---

## Autor

**Diego Escorel** - CESAR School 2025
