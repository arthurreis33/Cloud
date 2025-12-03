# 🧪 Como Testar Manualmente no Terminal

## 📋 Passo a Passo Completo

### 1. **Ativar o Ambiente Virtual**
```bash
cd "/Users/diegoescorel/Downloads/Trabalhou de cloud(arthur)/IsCoolGPT"
source venv/bin/activate
```

Você deve ver `(venv)` no início da linha do terminal.

### 2. **Verificar se o arquivo .env existe e tem a chave**
```bash
cat .env
```

Deve mostrar algo como:
```
OPENROUTER_API_KEY=sk-or-v1-sua_chave_aqui
PORT=3000
APP_URL=http://localhost:3000
```

### 3. **Iniciar o Servidor**

Em um terminal, execute:
```bash
python main.py
```

Você deve ver:
```
[LLM] Inicializando cliente OpenRouter - Chave configurada: True
INFO:     Started server process [XXXXX]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:3000 (Press CTRL+C to quit)
Servidor rodando em http://localhost:3000
Pressione CTRL+C para parar.
```

**Deixe este terminal aberto!** O servidor precisa estar rodando.

### 4. **Abrir um NOVO Terminal**

Abra outro terminal (ou nova aba) e vá para o diretório do projeto.

### 5. **Testar o Endpoint de Status**

```bash
curl http://localhost:3000/
```

**Resposta esperada:**
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

✅ Se funcionou, o servidor está rodando!

### 6. **Testar o Endpoint do Assistente**

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

**Resposta esperada (sem chave ou chave inválida):**
```json
{
  "detail": "Erro ao processar consulta, tente novamente mais tarde"
}
```

### 7. **Testar com Outras Perguntas**

```bash
# Pergunta sobre Cloud Computing
curl -X POST http://localhost:3000/api/tutor/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Explique o que é AWS S3"}'

# Pergunta sobre Kubernetes
curl -X POST http://localhost:3000/api/tutor/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é Kubernetes?"}'
```

### 8. **Ver Logs no Terminal do Servidor**

No terminal onde o servidor está rodando, você verá logs como:
```
[Assistente] Nova consulta recebida
[Assistente] Analisando consulta: O que é Docker?...
[LLM] Enviando solicitação (1/3)
[LLM] Resposta completa recebida
[Assistente] Resposta processada com sucesso
```

## 🔍 Verificar se Está Funcionando

### ✅ Sinais de que está funcionando:
- Servidor inicia sem erros
- `curl http://localhost:3000/` retorna JSON
- `Chave configurada: True` aparece nos logs
- Requisições retornam respostas (não apenas erros)

### ❌ Problemas comuns:

#### Porta 3000 em uso:
```bash
# Ver qual processo está usando
lsof -i:3000

# Matar o processo
lsof -ti:3000 | xargs kill -9

# Ou usar outra porta
# Edite .env e mude PORT=3001
```

#### Chave não configurada:
```bash
# Verificar .env
cat .env

# Se não existir, criar:
echo "OPENROUTER_API_KEY=sk-or-v1-sua_chave" > .env
echo "PORT=3000" >> .env
echo "APP_URL=http://localhost:3000" >> .env
```

#### Erro de conexão:
```bash
# Verificar se servidor está rodando
curl http://localhost:3000/

# Se não responder, verificar logs no terminal do servidor
```

## 📝 Exemplos de Teste Mais Detalhados

### Teste com formatação bonita (jq):
```bash
curl -X POST http://localhost:3000/api/tutor/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é Docker?"}' | python -m json.tool
```

### Teste salvando resposta em arquivo:
```bash
curl -X POST http://localhost:3000/api/tutor/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é Cloud Computing?"}' > resposta.json

cat resposta.json
```

### Teste de erro (sem pergunta):
```bash
curl -X POST http://localhost:3000/api/tutor/ask \
  -H "Content-Type: application/json" \
  -d '{}'
```

Deve retornar erro 422 (validação).

## 🎯 Resumo Rápido

```bash
# Terminal 1: Iniciar servidor
source venv/bin/activate
python main.py

# Terminal 2: Testar
curl http://localhost:3000/
curl -X POST http://localhost:3000/api/tutor/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é Docker?"}'
```

Pronto! 🚀

