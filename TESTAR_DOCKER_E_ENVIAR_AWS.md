# 🐳 Testar Docker Localmente e Enviar para AWS

Guia completo para testar o Docker no seu computador e depois enviar para a AWS.

---

## ✅ Passo 1: Corrigir o Problema do OPENROUTER_API_KEY

O `docker-compose.yml` já foi corrigido para carregar o arquivo `.env` automaticamente.

**O que foi alterado:**
- Adicionado `env_file: - .env` para carregar variáveis do arquivo `.env`
- Removida a linha `OPENROUTER_API_KEY=${OPENROUTER_API_KEY}` (agora vem do .env)

---

## 🧪 Passo 2: Testar Docker Localmente

### Opção A: Usando Docker Compose (Recomendado)

```bash
# 1. Parar containers anteriores (se houver)
docker compose down

# 2. Construir e rodar
docker compose up --build

# Ou rodar em background
docker compose up -d --build
```

**Verificar se está funcionando:**
```bash
# Ver logs
docker compose logs -f

# Testar a API
curl http://localhost:3000
```

### Opção B: Usando Docker Diretamente

```bash
# 1. Build da imagem
docker build --platform linux/amd64 -t iscoolgpt:local .

# 2. Rodar o container
docker run -d \
  --name iscoolgpt-test \
  -p 3000:3000 \
  --env-file .env \
  iscoolgpt:local

# 3. Ver logs
docker logs -f iscoolgpt-test

# 4. Testar
curl http://localhost:3000

# 5. Parar e remover
docker stop iscoolgpt-test
docker rm iscoolgpt-test
```

---

## 🚀 Passo 3: Enviar para AWS ECR

### Pré-requisitos

1. **AWS CLI instalado e configurado:**
   ```bash
   aws --version
   aws configure
   ```

2. **Credenciais AWS configuradas:**
   ```bash
   aws sts get-caller-identity
   ```

### Processo Completo

#### 1. Fazer Login no ECR

```bash
# Obter token de autenticação
aws ecr get-login-password --region sa-east-1 | \
  docker login --username AWS --password-stdin \
  176977333713.dkr.ecr.sa-east-1.amazonaws.com
```

**Nota:** Substitua `176977333713` pelo seu Account ID da AWS.

#### 2. Verificar/Criar Repositório ECR

```bash
# Verificar se existe
aws ecr describe-repositories \
  --repository-names iscoolgpt \
  --region sa-east-1

# Se não existir, criar
aws ecr create-repository \
  --repository-name iscoolgpt \
  --region sa-east-1
```

#### 3. Tag da Imagem

```bash
# Definir variáveis
AWS_ACCOUNT_ID="176977333713"  # Substitua pelo seu Account ID
AWS_REGION="sa-east-1"
ECR_REPOSITORY="iscoolgpt"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Tag da imagem
docker tag iscoolgpt:local ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
docker tag iscoolgpt:local ${ECR_REGISTRY}/${ECR_REPOSITORY}:$(date +%Y%m%d-%H%M%S)
```

#### 4. Push para ECR

```bash
# Push da imagem latest
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest

# Push da imagem com tag de data
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:$(date +%Y%m%d-%H%M%S)
```

#### 5. Verificar no ECR

```bash
# Listar imagens no repositório
aws ecr list-images \
  --repository-name iscoolgpt \
  --region sa-east-1
```

---

## 📝 Script Completo (Tudo em Um)

Crie um arquivo `push-to-aws.sh`:

```bash
#!/bin/bash

# Configurações
AWS_ACCOUNT_ID="176977333713"  # ⚠️ ALTERE PARA SEU ACCOUNT ID
AWS_REGION="sa-east-1"
ECR_REPOSITORY="iscoolgpt"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_TAG="latest"

echo "🔐 Fazendo login no ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${ECR_REGISTRY}

echo "🔨 Construindo imagem..."
docker build --platform linux/amd64 -t iscoolgpt:local .

echo "🏷️  Criando tags..."
docker tag iscoolgpt:local ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
docker tag iscoolgpt:local ${ECR_REGISTRY}/${ECR_REPOSITORY}:$(date +%Y%m%d-%H%M%S)

echo "📤 Enviando para ECR..."
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:$(date +%Y%m%d-%H%M%S)

echo "✅ Imagem enviada com sucesso!"
echo "📦 URI: ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"
```

**Tornar executável e rodar:**
```bash
chmod +x push-to-aws.sh
./push-to-aws.sh
```

---

## 🎯 Passo 4: Atualizar ECS Service

Depois de enviar a imagem para o ECR, você precisa atualizar o serviço ECS:

```bash
# Forçar novo deploy
aws ecs update-service \
  --cluster iscoolgpt-cluster2 \
  --service iscoolgpt-service \
  --force-new-deployment \
  --region sa-east-1
```

**Aguardar estabilização:**
```bash
aws ecs wait services-stable \
  --cluster iscoolgpt-cluster2 \
  --services iscoolgpt-service \
  --region sa-east-1
```

---

## 🔍 Verificar se Funcionou

### 1. Ver Logs do ECS

```bash
# Listar tasks
TASK_ARN=$(aws ecs list-tasks \
  --cluster iscoolgpt-cluster2 \
  --service-name iscoolgpt-service \
  --region sa-east-1 \
  --query 'taskArns[0]' \
  --output text)

# Ver logs
aws logs tail /ecs/iscoolgpt-task --follow --region sa-east-1
```

### 2. Obter IP Público

```bash
# Obter informações da task
aws ecs describe-tasks \
  --cluster iscoolgpt-cluster2 \
  --tasks $TASK_ARN \
  --region sa-east-1 \
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
  --output text
```

### 3. Testar API

```bash
# Substitua pelo IP público obtido
curl http://IP_PUBLICO:3000
```

---

## 🐛 Troubleshooting

### Erro: "no basic auth credentials"

**Solução:** Faça login no ECR novamente:
```bash
aws ecr get-login-password --region sa-east-1 | \
  docker login --username AWS --password-stdin \
  176977333713.dkr.ecr.sa-east-1.amazonaws.com
```

### Erro: "repository does not exist"

**Solução:** Crie o repositório:
```bash
aws ecr create-repository --repository-name iscoolgpt --region sa-east-1
```

### Erro: "OPENROUTER_API_KEY não configurada" no Docker

**Solução:** 
1. Verifique se o `.env` existe e tem a chave
2. Use `docker compose up` (já corrigido) ou `--env-file .env` no docker run

### Erro: "AccessDeniedException"

**Solução:** Verifique permissões IAM:
- `ecr:GetAuthorizationToken`
- `ecr:BatchCheckLayerAvailability`
- `ecr:GetDownloadUrlForLayer`
- `ecr:BatchGetImage`
- `ecr:PutImage`
- `ecr:InitiateLayerUpload`
- `ecr:UploadLayerPart`
- `ecr:CompleteLayerUpload`

---

## ✅ Checklist

- [ ] Docker instalado e funcionando
- [ ] Arquivo `.env` configurado com `OPENROUTER_API_KEY`
- [ ] Docker Compose testado localmente
- [ ] AWS CLI instalado e configurado
- [ ] Credenciais AWS configuradas
- [ ] Repositório ECR criado
- [ ] Login no ECR realizado
- [ ] Imagem construída e testada localmente
- [ ] Imagem enviada para ECR
- [ ] ECS Service atualizado
- [ ] API testada na AWS

---

## 🎉 Pronto!

Agora você pode:
1. ✅ Testar localmente com Docker
2. ✅ Enviar para AWS ECR
3. ✅ Fazer deploy no ECS

Tudo funcionando! 🚀

