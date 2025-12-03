# ✅ Checklist - Recursos AWS Necessários

Seu cluster `iscoolgpt-cluster2` já existe! Agora verifique se estes recursos também foram criados:

## 🔍 Verifique no Console AWS

### 1️⃣ Task Definition
- Acesse: https://console.aws.amazon.com/ecs/
- Clique em **Definições de Tarefa** (Task Definitions)
- Procure por: **iscoolgpt-task**
- Se NÃO existir → Você precisa criar

### 2️⃣ Service
- Clique em **Clusters**
- Selecione: **iscoolgpt-cluster2**
- Role para baixo e procure por: **Services** (Serviços)
- Procure por: **iscoolgpt-service**
- Se NÃO existir → Você precisa criar

### 3️⃣ ECR Repository
- Acesse: https://console.aws.amazon.com/ecr/
- Procure por: **iscoolgpt**
- Se NÃO existir → Você precisa criar

---

## 📋 Se algum estiver faltando:

### Se falta Task Definition:
1. Vá para https://console.aws.amazon.com/ecs/
2. Clique em **Definições de Tarefa** → **Criar nova definição de tarefa**
3. Configure com:
   - **Nome:** `iscoolgpt-task`
   - **Tipo de compatibilidade:** FARGATE
   - **CPU:** 256
   - **Memória:** 512
   - **Role de execução:** ecsTaskExecutionRole
   - **Container name:** iscoolgpt-app
   - **Imagem:** `176977333713.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt:latest`
   - **Porta:** 3000

### Se falta Service:
1. Vá para https://console.aws.amazon.com/ecs/
2. Clique em **Clusters** → **iscoolgpt-cluster2**
3. Clique em **Criar** (Create service)
4. Configure com:
   - **Task Definition:** iscoolgpt-task
   - **Número de tarefas:** 1
   - **Nome do serviço:** iscoolgpt-service
   - **VPC:** padrão
   - **Security Groups:** abra porta 3000
   - **IP público:** ENABLED

### Se falta ECR Repository:
1. Vá para https://console.aws.amazon.com/ecr/
2. Clique em **Repositórios** → **Criar repositório**
3. Configure com:
   - **Nome:** iscoolgpt
   - **Scan on push:** Ativado

---

## 🚀 Próximos Passos (Depois de Confirmar Tudo):

### 1. Fazer Push da Imagem Docker

```powershell
# 1. Build da imagem
docker build -t iscoolgpt .

# 2. Login no ECR
aws ecr get-login-password --region sa-east-1 | docker login --username AWS --password-stdin 176977333713.dkr.ecr.sa-east-1.amazonaws.com

# 3. Taggear
docker tag iscoolgpt:latest 176977333713.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt:latest

# 4. Push
docker push 176977333713.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt:latest
```

### 2. Fazer Commit e Push para Disparar GitHub Actions

```powershell
git add .github/workflows/cd.yml
git commit -m "chore: atualizar cluster para iscoolgpt-cluster2"
git push origin main
```

### 3. Monitorar GitHub Actions
- Vá para: https://github.com/arthurreis33/Cloud/actions
- Veja o workflow `CD - Deploy AWS` executar
- Quando terminar, você verá a URL da API nos logs

### 4. Testar a API

```powershell
# Substituir com o IP públco da tarefa (vem nos logs do GitHub Actions)
$PUBLIC_IP = "xxx.xxx.xxx.xxx"

curl -X POST http://$PUBLIC_IP:3000/api/tutor/ask `
  -H "Content-Type: application/json" `
  -d '{"question": "O que é Docker?"}'
```

---

## 📝 Informações Importantes

- **Conta AWS:** 176977333713
- **Região:** sa-east-1
- **Cluster:** iscoolgpt-cluster2
- **Repositório ECR:** iscoolgpt
- **Task Definition:** iscoolgpt-task
- **Service:** iscoolgpt-service
- **Porta da API:** 3000

---

**Verifique tudo no console e me avise qual recurso está faltando!** ✅
