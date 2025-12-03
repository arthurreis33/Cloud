# 🔐 Como Fazer Push com Conta Diferente no GitHub

## Situação Atual
- ✅ Repositório remoto: `arthurreis33/Cloud` (correto)
- ⚠️ Você precisa autenticar com a conta do **Arthur Reis** para fazer push

---

## 🚀 Opção 1: Personal Access Token (Mais Fácil)

### Passo 1: Criar Token no GitHub do Arthur Reis

1. Acesse: https://github.com/settings/tokens
2. Faça login com a conta **arthurreis33**
3. Clique em **"Generate new token"** → **"Generate new token (classic)"**
4. Configure:
   - **Note:** `Push para Cloud`
   - **Expiration:** Escolha uma data (ou "No expiration")
   - **Scopes:** Marque `repo` (acesso completo aos repositórios)
5. Clique em **"Generate token"**
6. **COPIE O TOKEN** (você só verá uma vez!)

### Passo 2: Usar o Token ao Fazer Push

Quando fizer push, use o token como senha:

```bash
# Quando pedir usuário: digite "arthurreis33"
# Quando pedir senha: cole o token (não a senha do GitHub!)
```

Ou configure diretamente na URL:

```bash
git remote set-url origin https://arthurreis33:SEU_TOKEN_AQUI@github.com/arthurreis33/Cloud.git
```

**⚠️ Cuidado:** Não commite o token no código!

---

## 🔑 Opção 2: SSH Keys (Mais Seguro)

### Passo 1: Gerar Chave SSH (se ainda não tiver)

```bash
ssh-keygen -t ed25519 -C "diegofescorel@gmail.com"
# Pressione Enter para aceitar local padrão
# Digite uma senha (ou deixe vazio)
```

### Passo 2: Copiar Chave Pública

```bash
cat ~/.ssh/id_ed25519.pub
# Copie TODO o conteúdo
```

### Passo 3: Adicionar no GitHub do Arthur Reis

1. Acesse: https://github.com/settings/keys
2. Faça login com a conta **arthurreis33**
3. Clique em **"New SSH key"**
4. Cole a chave pública
5. Salve

### Passo 4: Mudar Remote para SSH

```bash
git remote set-url origin git@github.com:arthurreis33/Cloud.git
```

### Passo 5: Testar Conexão

```bash
ssh -T git@github.com
# Deve aparecer: "Hi arthurreis33! You've successfully authenticated..."
```

---

## 🎯 Opção 3: GitHub CLI (Mais Moderno)

### Instalar GitHub CLI

```bash
brew install gh
```

### Fazer Login

```bash
gh auth login
# Escolha GitHub.com
# Escolha HTTPS
# Autentique com a conta arthurreis33
```

Depois disso, o Git usará automaticamente as credenciais do GitHub CLI.

---

## ✅ Fazer Push Agora

Depois de configurar uma das opções acima:

```bash
# Adicionar arquivos
git add .

# Fazer commit
git commit -m "fix: corrigir configuração CI/CD"

# Fazer push
git push origin main
```

---

## 🔍 Verificar Configuração Atual

```bash
# Ver remote
git remote -v

# Ver usuário configurado
git config user.name
git config user.email
```

---

## ⚠️ Problemas Comuns

### Erro: "Permission denied"
- Verifique se o token/chave SSH está configurado corretamente
- Verifique se você tem acesso ao repositório `arthurreis33/Cloud`

### Erro: "Authentication failed"
- Token pode ter expirado
- Chave SSH pode não estar adicionada no GitHub
- Verifique se está usando a conta correta

### Erro: "Repository not found"
- Verifique se o repositório existe: https://github.com/arthurreis33/Cloud
- Verifique se você tem permissão de escrita no repositório

---

## 💡 Recomendação

Para este caso, recomendo a **Opção 1 (Personal Access Token)** porque:
- ✅ Mais rápido de configurar
- ✅ Funciona imediatamente
- ✅ Não precisa configurar SSH

Depois, se quiser mais segurança, pode migrar para SSH.

