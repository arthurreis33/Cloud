# 🔧 Configuração do Arquivo .env

## 📝 Variáveis Necessárias

Crie um arquivo chamado `.env` na **raiz do projeto** (mesmo nível do `main.py`) com o seguinte conteúdo:

```env
# ============================================
# CHAVE DA API OPENROUTER (OBRIGATÓRIA)
# ============================================
# Obtenha sua chave em: https://openrouter.ai/keys
# Crie uma conta gratuita e gere uma chave API
OPENROUTER_API_KEY=sk-or-v1-sua_chave_aqui

# ============================================
# PORTA DO SERVIDOR (OPCIONAL)
# ============================================
# Porta onde o servidor vai rodar
# Padrão: 3000 (se não especificar)
PORT=3000

# ============================================
# URL DA APLICAÇÃO (OPCIONAL)
# ============================================
# URL usada no header HTTP-Referer das requisições
# Padrão: http://localhost:3000 (se não especificar)
APP_URL=http://localhost:3000
```

## 🚀 Passo a Passo

### 1. Criar o arquivo `.env`

No terminal, na raiz do projeto:

```bash
cd "/Users/diegoescorel/Downloads/Trabalhou de cloud(arthur)/IsCoolGPT"
touch .env
```

Ou crie manualmente no editor de texto.

### 2. Adicionar o conteúdo mínimo

**Mínimo necessário para funcionar:**
```env
OPENROUTER_API_KEY=sk-or-v1-sua_chave_real_aqui
```

### 3. Obter a chave OpenRouter

1. Acesse: https://openrouter.ai/
2. Crie uma conta (gratuita)
3. Vá em: https://openrouter.ai/keys
4. Clique em "Create Key"
5. Copie a chave (começa com `sk-or-v1-`)
6. Cole no arquivo `.env`

### 4. Exemplo completo

```env
OPENROUTER_API_KEY=sk-or-v1-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
PORT=3000
APP_URL=http://localhost:3000
```

## ⚠️ Importante

1. **NUNCA commite o arquivo `.env`** - Ele já está no `.gitignore`
2. **Nunca compartilhe sua chave** - Ela é pessoal e intransferível
3. **A chave começa com `sk-or-v1-`** - Se não começar assim, está errada
4. **Sem espaços** - Não coloque espaços antes ou depois do `=`

## ✅ Verificar se está funcionando

Após criar o `.env`:

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Iniciar servidor
python main.py
```

Você deve ver:
```
[AI] Inicializando provider - Key configurada: True
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:3000
```

Se aparecer `Key configurada: True`, está correto! ✅

## 🐛 Problemas Comuns

### "Key configurada: False"
- Verifique se o arquivo se chama exatamente `.env` (com o ponto)
- Verifique se está na raiz do projeto
- Verifique se não há espaços extras na linha

### "Erro HTTP 401"
- Chave inválida ou expirada
- Verifique se copiou a chave completa
- Gere uma nova chave no OpenRouter

### "Erro HTTP 429"
- Limite de requisições excedido
- Aguarde alguns minutos ou verifique seu plano

