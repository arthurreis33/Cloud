# 🧪 Como Testar AWS Localmente (Sem GitHub)

## 📋 Pré-requisitos

1. ✅ AWS CLI instalado e configurado
2. ✅ Docker instalado e rodando
3. ✅ Recursos AWS criados:
   - ECR repositório: `iscoolgpt`
   - ECS cluster: `iscoolgpt-cluster2`
   - Task Definition criada
   - Service criado

---

## 🚀 Passo a Passo

### 1. Verificar AWS CLI

```bash
# Verificar se está configurado
aws sts get-caller-identity

# Deve mostrar seu Account ID
```

Se não estiver configurado:
```bash
aws configure
# Digite suas credenciais (Access Key ID e Secret)
# Região: sa-east-1
```

### 2. Fazer Login no ECR

```bash
# Fazer login no ECR (substitua ACCOUNT_ID pelo seu)
aws ecr get-login-password --region sa-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.sa-east-1.amazonaws.com
```

**Ou use este comando automático:**
```bash
# Pega o Account ID automaticamente
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws ecr get-login-password --region sa-east-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.sa-east-1.amazonaws.com
```

Você deve ver: `Login Succeeded`

### 3. Obter URI do Repositório ECR

```bash
# Listar repositórios
aws ecr describe-repositories --repository-names iscoolgpt --region sa-east-1

# Ou pegar apenas a URI
ECR_URI=$(aws ecr describe-repositories --repository-names iscoolgpt --region sa-east-1 --query 'repositories[0].repositoryUri' --output text)
echo $ECR_URI
```

Anote a URI (algo como: `123456789012.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt`)

### 4. Build da Imagem Docker

```bash
# No diretório do projeto
cd "/Users/diegoescorel/Downloads/Trabalhou de cloud(arthur)/IsCoolGPT"

# Build da imagem (substitua ECR_URI pela URI que você anotou)
docker build --platform linux/amd64 -t iscoolgpt:latest .

# Tag da imagem para ECR
docker tag iscoolgpt:latest $ECR_URI:latest
```

**Ou tudo em um comando:**
```bash
ECR_URI=$(aws ecr describe-repositories --repository-names iscoolgpt --region sa-east-1 --query 'repositories[0].repositoryUri' --output text)
docker build --platform linux/amd64 -t $ECR_URI:latest .
```

### 5. Push da Imagem para ECR

```bash
# Push da imagem
docker push $ECR_URI:latest
```

Isso pode demorar alguns minutos na primeira vez.

### 6. Atualizar o Serviço ECS

```bash
# Forçar novo deploy do serviço
aws ecs update-service \
  --cluster iscoolgpt-cluster2 \
  --service iscoolgpt-service \
  --force-new-deployment \
  --region sa-east-1
```

Você deve ver uma resposta com o status do serviço.

### 7. Verificar Status da Tarefa

```bash
# Listar tarefas do serviço
aws ecs list-tasks \
  --cluster iscoolgpt-cluster2 \
  --service-name iscoolgpt-service \
  --region sa-east-1

# Pegar detalhes da tarefa (substitua TASK_ARN pelo ARN retornado acima)
aws ecs describe-tasks \
  --cluster iscoolgpt-cluster2 \
  --tasks TASK_ARN \
  --region sa-east-1 \
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
  --output text
```

### 8. Obter IP Público

```bash
# Listar tarefas
TASK_ARN=$(aws ecs list-tasks --cluster iscoolgpt-cluster2 --service-name iscoolgpt-service --region sa-east-1 --query 'taskArns[0]' --output text)

# Obter detalhes da tarefa
aws ecs describe-tasks \
  --cluster iscoolgpt-cluster2 \
  --tasks $TASK_ARN \
  --region sa-east-1 \
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
  --output text

# Ou mais simples - pegar IP público diretamente
aws ecs describe-tasks \
  --cluster iscoolgpt-cluster2 \
  --tasks $TASK_ARN \
  --region sa-east-1 \
  --query 'tasks[0].attachments[0].details[?name==`publicIPv4Address`].value' \
  --output text
```

**Ou via console AWS:**
1. ECS → Clusters → `iscoolgpt-cluster2`
2. Aba **Serviços** → `iscoolgpt-service`
3. Aba **Tarefas** → Clique na tarefa
4. Veja o **IP público** na seção de rede

### 9. Testar a API

```bash
# Substitua IP_PUBLICO pelo IP que você obteve
IP_PUBLICO="SEU_IP_AQUI"

# Testar endpoint de status
curl http://$IP_PUBLICO:3000/

# Testar endpoint do assistente
curl -X POST http://$IP_PUBLICO:3000/api/tutor/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é Docker?"}'
```

---

## 📝 Script Completo (Copiar e Colar)

Crie um arquivo `testar-aws.sh`:

```bash
#!/bin/bash

set -e

REGION="sa-east-1"
CLUSTER="iscoolgpt-cluster2"
SERVICE="iscoolgpt-service"
REPO="iscoolgpt"

echo "🔐 Fazendo login no ECR..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO"

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI

echo "🏗️  Fazendo build da imagem..."
docker build --platform linux/amd64 -t $ECR_URI:latest .

echo "📤 Enviando imagem para ECR..."
docker push $ECR_URI:latest

echo "🚀 Atualizando serviço ECS..."
aws ecs update-service \
  --cluster $CLUSTER \
  --service $SERVICE \
  --force-new-deployment \
  --region $REGION \
  --query 'service.serviceName' \
  --output text

echo "⏳ Aguardando serviço estabilizar (30 segundos)..."
sleep 30

echo "📋 Obtendo IP público..."
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER --service-name $SERVICE --region $REGION --query 'taskArns[0]' --output text)
IP=$(aws ecs describe-tasks --cluster $CLUSTER --tasks $TASK_ARN --region $REGION --query 'tasks[0].attachments[0].details[?name==`publicIPv4Address`].value' --output text)

echo ""
echo "✅ Deploy concluído!"
echo "🌐 IP Público: $IP"
echo ""
echo "🧪 Testar API:"
echo "curl http://$IP:3000/"
echo "curl -X POST http://$IP:3000/api/tutor/ask -H 'Content-Type: application/json' -d '{\"question\": \"O que é Docker?\"}'"
```

**Para usar:**
```bash
chmod +x testar-aws.sh
./testar-aws.sh
```

---

## 🔍 Verificar Logs

Se algo não funcionar, veja os logs:

```bash
# Listar log groups
aws logs describe-log-groups --log-group-name-prefix /ecs/iscoolgpt --region sa-east-1

# Ver logs recentes
aws logs tail /ecs/iscoolgpt --follow --region sa-east-1
```

---

## ⚠️ Troubleshooting

### Erro: "Repository not found"
- Verifique se o repositório ECR existe
- Verifique se está na região correta (sa-east-1)

### Erro: "Service not found"
- Verifique se o serviço existe no cluster correto
- Verifique o nome: `iscoolgpt-service`

### Tarefa não inicia
- Verifique os logs do CloudWatch
- Verifique se a imagem foi enviada corretamente
- Verifique se as variáveis de ambiente estão corretas

### API não responde
- Verifique se o Security Group permite porta 3000
- Verifique se a tarefa está rodando (status RUNNING)
- Verifique os logs do CloudWatch

---

## ✅ Checklist

- [ ] AWS CLI configurado
- [ ] Login no ECR feito
- [ ] Imagem Docker buildada
- [ ] Imagem enviada para ECR
- [ ] Serviço ECS atualizado
- [ ] Tarefa rodando (status RUNNING)
- [ ] IP público obtido
- [ ] API testada e funcionando

---

**Pronto! Siga os passos e teste sua API na AWS!** 🚀

