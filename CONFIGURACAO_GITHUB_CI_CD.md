# 🔧 Configuração do CI/CD no GitHub

Este guia explica como configurar corretamente o CI/CD no GitHub para o projeto IsCoolGPT.

## 📋 Pré-requisitos

1. Repositório criado no GitHub
2. Código commitado e enviado para o repositório
3. Acesso de administrador ao repositório

---

## 🔐 Passo 1: Configurar Secrets no GitHub

Os **Secrets** são variáveis de ambiente seguras que o GitHub Actions usa durante a execução.

### Como acessar:

1. Vá para seu repositório no GitHub
2. Clique em **Settings** (Configurações)
3. No menu lateral, clique em **Secrets and variables** → **Actions**
4. Clique em **New repository secret**

### Secrets necessários:

#### 1. `OPENROUTER_API_KEY` (Obrigatório para testes)
- **Nome:** `OPENROUTER_API_KEY`
- **Valor:** Sua chave da API OpenRouter (começa com `sk-or-v1-`)
- **Onde obter:** https://openrouter.ai/keys
- **Usado em:** CI (testes)

#### 2. `AWS_ACCESS_KEY_ID` (Obrigatório para deploy)
- **Nome:** `AWS_ACCESS_KEY_ID`
- **Valor:** Sua chave de acesso AWS
- **Onde obter:** AWS Console → IAM → Users → Security credentials
- **Usado em:** CD (deploy)

#### 3. `AWS_SECRET_ACCESS_KEY` (Obrigatório para deploy)
- **Nome:** `AWS_SECRET_ACCESS_KEY`
- **Valor:** Sua chave secreta AWS
- **Onde obter:** AWS Console → IAM → Users → Security credentials
- **Usado em:** CD (deploy)

### ⚠️ Importante sobre AWS Credentials:

As credenciais AWS precisam ter as seguintes permissões:
- **ECR:** `ecr:GetAuthorizationToken`, `ecr:BatchCheckLayerAvailability`, `ecr:GetDownloadUrlForLayer`, `ecr:BatchGetImage`, `ecr:PutImage`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`
- **ECS:** `ecs:UpdateService`, `ecs:DescribeServices`, `ecs:ListTasks`, `ecs:DescribeTasks`
- **EC2:** `ec2:DescribeNetworkInterfaces` (para obter IP público)

---

## 📁 Passo 2: Estrutura dos Arquivos de Workflow

Os arquivos de workflow devem estar em:
```
.github/
└── workflows/
    ├── ci.yml    # Pipeline de CI (testes, lint, build)
    └── cd.yml    # Pipeline de CD (deploy AWS)
```

### ✅ Verificar se os arquivos existem:

```bash
ls -la .github/workflows/
```

Você deve ver:
- `ci.yml`
- `cd.yml`

---

## 🔄 Passo 3: Como os Workflows Funcionam

### CI Workflow (`.github/workflows/ci.yml`)

**Quando executa:**
- Push na branch `main`
- Pull Request para `main`

**O que faz:**
1. ✅ Faz checkout do código
2. ✅ Configura Python 3.11
3. ✅ Instala dependências (`requirements.txt` e `requirements-dev.txt`)
4. ✅ Executa lint com Flake8
5. ✅ Executa testes com Pytest
6. ✅ Faz build da imagem Docker

**Status:** Se passar, o CD pode executar.

### CD Workflow (`.github/workflows/cd.yml`)

**Quando executa:**
- Push na branch `main` (após CI passar)
- Manualmente via `workflow_dispatch`

**O que faz:**
1. ✅ Faz checkout do código
2. ✅ Configura credenciais AWS
3. ✅ Faz login no Amazon ECR
4. ✅ Build e push da imagem Docker para ECR
5. ✅ Atualiza o serviço ECS
6. ✅ Aguarda estabilização
7. ✅ Obtém informações da tarefa (IP público)

**Dependência:** Só executa se o CI passar.

---

## 🛠️ Passo 4: Configurações no Código

### Arquivo `.github/workflows/ci.yml`

**Configurações importantes:**
- `python-version: '3.11'` - Versão do Python
- `OPENROUTER_API_KEY` - Secret necessário para testes

### Arquivo `.github/workflows/cd.yml`

**Configurações importantes:**
```yaml
env:
  AWS_REGION: sa-east-1              # Região AWS
  ECR_REPOSITORY: iscoolgpt          # Nome do repositório ECR
  ECS_CLUSTER: iscoolgpt-cluster2    # Nome do cluster ECS
  ECS_SERVICE: iscoolgpt-service     # Nome do serviço ECS
```

**⚠️ Ajuste estes valores** conforme sua configuração AWS!

---

## 🚀 Passo 5: Testar o CI/CD

### 1. Fazer um commit e push:

```bash
git add .
git commit -m "test: verificar CI/CD"
git push origin main
```

### 2. Verificar no GitHub:

1. Vá para: `https://github.com/SEU_USUARIO/SEU_REPOSITORIO/actions`
2. Você verá os workflows executando
3. Clique em um workflow para ver os logs

### 3. Verificar logs:

- ✅ **Verde** = Passou
- ❌ **Vermelho** = Falhou (clique para ver o erro)

---

## 🐛 Problemas Comuns e Soluções

### ❌ Erro: "Secret not found"

**Problema:** Secret não configurado no GitHub.

**Solução:**
1. Vá em Settings → Secrets and variables → Actions
2. Adicione o secret faltante
3. Faça um novo commit para reexecutar

### ❌ Erro: "AWS credentials invalid"

**Problema:** Credenciais AWS incorretas ou sem permissões.

**Solução:**
1. Verifique se as credenciais estão corretas
2. Verifique se o usuário IAM tem as permissões necessárias
3. Teste as credenciais localmente:
   ```bash
   aws configure
   aws ecs list-clusters
   ```

### ❌ Erro: "ECR repository not found"

**Problema:** Repositório ECR não existe.

**Solução:**
1. Crie o repositório ECR:
   ```bash
   aws ecr create-repository --repository-name iscoolgpt --region sa-east-1
   ```
2. Ou ajuste o nome no `cd.yml`

### ❌ Erro: "ECS cluster not found"

**Problema:** Cluster ECS não existe.

**Solução:**
1. Crie o cluster ECS
2. Ou ajuste o nome no `cd.yml` (variável `ECS_CLUSTER`)

### ❌ Erro: "Tests failed"

**Problema:** Testes falhando.

**Solução:**
1. Rode os testes localmente:
   ```bash
   pytest src/__tests__/ -v
   ```
2. Corrija os testes
3. Faça commit e push

### ❌ Erro: "Lint failed"

**Problema:** Código não passa no lint.

**Solução:**
1. Rode o lint localmente:
   ```bash
   flake8 src/
   ```
2. Corrija os problemas
3. Faça commit e push

---

## 📊 Monitoramento

### Ver status dos workflows:

1. **GitHub Actions:** `https://github.com/SEU_USUARIO/SEU_REPOSITORIO/actions`
2. **Badge de status:** Adicione ao README:
   ```markdown
   ![CI](https://github.com/SEU_USUARIO/SEU_REPOSITORIO/workflows/CI/badge.svg)
   ```

### Logs importantes:

- **CI:** Verifica se testes e lint passam
- **CD:** Verifica se deploy foi bem-sucedido
- **IP Público:** Aparece no final do log do CD

---

## ✅ Checklist de Configuração

- [ ] Repositório criado no GitHub
- [ ] Código commitado e enviado
- [ ] Secret `OPENROUTER_API_KEY` configurado
- [ ] Secret `AWS_ACCESS_KEY_ID` configurado
- [ ] Secret `AWS_SECRET_ACCESS_KEY` configurado
- [ ] Arquivos `.github/workflows/ci.yml` e `cd.yml` existem
- [ ] Valores no `cd.yml` correspondem à sua infraestrutura AWS
- [ ] Repositório ECR criado
- [ ] Cluster ECS criado
- [ ] Serviço ECS criado
- [ ] Permissões IAM configuradas
- [ ] Teste local passando (`pytest`)
- [ ] Lint local passando (`flake8`)
- [ ] Push feito e workflows executando

---

## 🎯 Próximos Passos

1. Configure os secrets no GitHub
2. Ajuste os valores no `cd.yml` conforme sua AWS
3. Faça um commit e push
4. Monitore os workflows em Actions
5. Verifique se o deploy foi bem-sucedido

---

## 📚 Referências

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)

