# 🧪 Guia de Testes

## ✅ Comportamento Esperado

### 1. **Servidor inicia normalmente**
Mesmo sem a chave da API, o servidor FastAPI deve iniciar sem erros:
```bash
python main.py
```

Você verá:
```
[AI] Inicializando provider - Key configurada: False
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:3000
```

### 2. **Endpoint de status funciona**
```bash
curl http://localhost:3000/
```

Resposta esperada:
```json
{
  "status": "online",
  "service": "IsCoolGPT",
  "version": "2.0.0",
  "endpoints": {
    "tutor": "/api/tutor/ask"
  }
}
```

### 3. **Requisição sem chave da API retorna erro**

```bash
curl -X POST http://localhost:3000/api/tutor/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é cloud computing?"}'
```

**Resposta esperada (sem chave):**
```json
{
  "detail": "Erro ao processar pergunta, tente novamente mais tarde"
}
```

**No console do servidor você verá:**
```
[Tutor] Nova requisição recebida
[Tutor] Processando pergunta: O que é cloud computing?...
[AI] Tentativa 1 falhou: OPENROUTER_API_KEY não configurada. Configure no arquivo .env
[AI] Tentativa 2 falhou: OPENROUTER_API_KEY não configurada. Configure no arquivo .env
[Tutor] Falha ao gerar resposta: Não foi possível obter resposta da IA
```

## 🔑 Como Testar com Chave Válida

1. **Criar arquivo `.env`:**
```env
OPENROUTER_API_KEY=sua_chave_real_aqui
PORT=3000
APP_URL=http://localhost:3000
```

2. **Reiniciar o servidor:**
```bash
python main.py
```

3. **Fazer requisição:**
```bash
curl -X POST http://localhost:3000/api/tutor/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é Docker?"}'
```

**Resposta esperada (com chave válida):**
```json
{
  "question": "O que é Docker?",
  "answer": "Docker é uma plataforma de containerização..."
}
```

## 🐛 Erros Comuns

### Erro: "OPENROUTER_API_KEY não configurada"
**Causa:** Arquivo `.env` não existe ou não contém a chave
**Solução:** Criar arquivo `.env` na raiz do projeto com a chave

### Erro: "Erro HTTP 401"
**Causa:** Chave da API inválida ou expirada
**Solução:** Verificar chave no site do OpenRouter

### Erro: "Erro HTTP 429"
**Causa:** Limite de requisições excedido
**Solução:** Aguardar ou verificar plano da API

## 📝 Notas

- O servidor **sempre inicia**, mesmo sem chave
- Apenas o endpoint `/api/tutor/ask` requer a chave
- O endpoint `/` (status) funciona sempre
- A documentação interativa em `/docs` também funciona sempre

