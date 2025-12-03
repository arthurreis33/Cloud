# 🔍 Troubleshooting: Problemas no CD (Deploy AWS)

Este guia lista todos os pontos onde o CD pode falhar e como resolver.

---

## 📋 Checklist de Verificação Rápida

### 1. **Secrets no GitHub** ⚠️
- [ ] `AWS_ACCESS_KEY_ID` configurado
- [ ] `AWS_SECRET_ACCESS_KEY` configurado
- [ ] Credenciais estão corretas e não expiraram

### 2. **Recursos AWS** ⚠️
- [ ] Repositório ECR existe: `iscoolgpt`
- [ ] Cluster ECS existe: `iscoolgpt-cluster2`
- [ ] Serviço ECS existe: `iscoolgpt-service`
- [ ] Task Definition existe: `iscoolgpt-task`
- [ ] Região correta: `sa-east-1`

### 3. **Permissões IAM** ⚠️
- [ ] Usuário tem permissão para ECR (push/pull)
- [ ] Usuário tem permissão para ECS (update service)
- [ ] Usuário tem permissão para EC2 (describe network interfaces)

---

## 🚨 Pontos de Falha no Workflow CD

### **ETAPA 1: Configurar Credenciais AWS** (Linha 27-32)

**Erro possível:**
```
Error: The security token included in the request is invalid
```

**Causas:**
- ❌ Secret `AWS_ACCESS_KEY_ID` não configurado ou incorreto
- ❌ Secret `AWS_SECRET_ACCESS_KEY` não configurado ou incorreto
- ❌ Credenciais expiradas
- ❌ Região incorreta (`AWS_REGION: sa-east-1`)

**Solução:**
1. Verifique os secrets no GitHub: Settings → Secrets and variables → Actions
2. Verifique se as credenciais estão corretas:
   ```bash
   aws configure
   aws sts get-caller-identity
   ```
3. Verifique a região no arquivo `cd.yml` (linha 12)

---

### **ETAPA 2: Login no Amazon ECR** (Linha 34-36)

**Erro possível:**
```
Error: Unable to locate credentials
Error: An error occurred (AccessDeniedException) when calling the GetAuthorizationToken operation
```

**Causas:**
- ❌ Repositório ECR não existe
- ❌ Usuário não tem permissão `ecr:GetAuthorizationToken`
- ❌ Região incorreta

**Solução:**
1. Verifique se o repositório existe:
   ```bash
   aws ecr describe-repositories --repository-names iscoolgpt --region sa-east-1
   ```
2. Se não existir, crie:
   ```bash
   aws ecr create-repository --repository-name iscoolgpt --region sa-east-1
   ```
3. Verifique permissões IAM:
   - `ecr:GetAuthorizationToken`
   - `ecr:BatchCheckLayerAvailability`
   - `ecr:GetDownloadUrlForLayer`
   - `ecr:BatchGetImage`

---

### **ETAPA 3: Build e Push da Imagem Docker** (Linha 38-49)

**Erro possível:**
```
Error: failed to solve: failed to fetch
Error: denied: Your Authorization Token has expired
Error: denied: The image does not exist or you don't have permission
```

**Causas:**
- ❌ Dockerfile com erro
- ❌ Imagem muito grande
- ❌ Token ECR expirado
- ❌ Sem permissão para push no ECR

**Solução:**
1. Teste o build localmente:
   ```bash
   docker build --platform linux/amd64 -t iscoolgpt .
   ```
2. Verifique permissões ECR:
   - `ecr:PutImage`
   - `ecr:InitiateLayerUpload`
   - `ecr:UploadLayerPart`
   - `ecr:CompleteLayerUpload`
3. Verifique se o repositório existe e está acessível

---

### **ETAPA 4: Deploy no Amazon ECS** (Linha 51-67)

**Erro possível:**
```
Error: An error occurred (ClusterNotFoundException) when calling the DescribeTaskDefinition operation
Error: An error occurred (ServiceNotFoundException) when calling the UpdateService operation
Error: An error occurred (InvalidParameterException) when calling the UpdateService operation
```

**Causas:**
- ❌ Task Definition `iscoolgpt-task` não existe
- ❌ Cluster `iscoolgpt-cluster2` não existe
- ❌ Serviço `iscoolgpt-service` não existe
- ❌ Nomes incorretos no arquivo `cd.yml`

**Solução:**

1. **Verificar Task Definition:**
   ```bash
   aws ecs describe-task-definition \
     --task-definition iscoolgpt-task \
     --region sa-east-1
   ```
   Se não existir, crie usando os scripts em `setup-cloudshell.sh` ou `setup-simple.sh`

2. **Verificar Cluster:**
   ```bash
   aws ecs describe-clusters \
     --clusters iscoolgpt-cluster2 \
     --region sa-east-1
   ```
   Se não existir:
   ```bash
   aws ecs create-cluster \
     --cluster-name iscoolgpt-cluster2 \
     --region sa-east-1
   ```

3. **Verificar Serviço:**
   ```bash
   aws ecs describe-services \
     --cluster iscoolgpt-cluster2 \
     --services iscoolgpt-service \
     --region sa-east-1
   ```
   Se não existir, crie usando os scripts de setup

4. **Verificar nomes no `cd.yml`:**
   ```yaml
   env:
     ECS_CLUSTER: iscoolgpt-cluster2    # ← Verifique se está correto
     ECS_SERVICE: iscoolgpt-service    # ← Verifique se está correto
   ```

5. **Verificar permissões ECS:**
   - `ecs:DescribeTaskDefinition`
   - `ecs:UpdateService`
   - `ecs:DescribeServices`

---

### **ETAPA 5: Aguardar Estabilização** (Linha 69-75)

**Erro possível:**
```
Error: Waiter ServicesStable failed: Max attempts exceeded
```

**Causas:**
- ❌ Container não inicia (erro na aplicação)
- ❌ Imagem não encontrada no ECR
- ❌ Variáveis de ambiente faltando (OPENROUTER_API_KEY)
- ❌ Porta incorreta
- ❌ Health check falhando
- ❌ Sem recursos disponíveis (CPU/memória)

**Solução:**

1. **Verificar logs do ECS:**
   ```bash
   aws logs tail /ecs/iscoolgpt-task --follow --region sa-east-1
   ```

2. **Verificar status da task:**
   ```bash
   aws ecs list-tasks \
     --cluster iscoolgpt-cluster2 \
     --service-name iscoolgpt-service \
     --region sa-east-1
   
   # Pegar o ARN da task e verificar detalhes
   aws ecs describe-tasks \
     --cluster iscoolgpt-cluster2 \
     --tasks <TASK_ARN> \
     --region sa-east-1
   ```

3. **Verificar Secrets Manager:**
   - A Task Definition precisa do secret `OPENROUTER_API_KEY`
   - Verifique se o secret existe:
     ```bash
     aws secretsmanager describe-secret \
       --secret-id openrouter-api-key \
       --region sa-east-1
     ```

4. **Verificar Task Definition:**
   - Imagem deve apontar para: `ACCOUNT_ID.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt:latest`
   - Porta deve ser 3000
   - Variáveis de ambiente devem estar configuradas

---

### **ETAPA 6: Obter Informações da Tarefa** (Linha 77-106)

**Erro possível:**
```
Error: An error occurred (InvalidParameterException) when calling the DescribeTasks operation
Error: IP não disponível ainda
```

**Causas:**
- ❌ Task não está rodando
- ❌ Network interface não configurada
- ❌ Sem IP público atribuído
- ❌ Security Group bloqueando

**Solução:**

1. **Verificar se a task está rodando:**
   ```bash
   aws ecs describe-tasks \
     --cluster iscoolgpt-cluster2 \
     --tasks <TASK_ARN> \
     --region sa-east-1 \
     --query 'tasks[0].lastStatus'
   ```

2. **Verificar Network Interface:**
   - A task precisa ter um IP público se quiser acessar externamente
   - Verifique a configuração do serviço ECS

3. **Verificar Security Group:**
   - Deve permitir tráfego na porta 3000
   - Deve permitir tráfego de saída para internet

---

## 🔧 Comandos Úteis para Diagnóstico

### Verificar Status Completo

```bash
# 1. Verificar ECR
aws ecr describe-repositories --region sa-east-1

# 2. Verificar ECS Cluster
aws ecs describe-clusters --clusters iscoolgpt-cluster2 --region sa-east-1

# 3. Verificar ECS Service
aws ecs describe-services \
  --cluster iscoolgpt-cluster2 \
  --services iscoolgpt-service \
  --region sa-east-1

# 4. Verificar Task Definition
aws ecs describe-task-definition \
  --task-definition iscoolgpt-task \
  --region sa-east-1

# 5. Verificar Tasks em execução
aws ecs list-tasks \
  --cluster iscoolgpt-cluster2 \
  --service-name iscoolgpt-service \
  --region sa-east-1

# 6. Verificar Logs
aws logs tail /ecs/iscoolgpt-task --follow --region sa-east-1
```

### Verificar Permissões IAM

```bash
# Verificar identidade
aws sts get-caller-identity

# Testar permissões ECR
aws ecr get-authorization-token --region sa-east-1

# Testar permissões ECS
aws ecs describe-clusters --region sa-east-1
```

---

## 📝 Checklist de Recursos AWS Necessários

### ✅ ECR (Elastic Container Registry)
- [ ] Repositório: `iscoolgpt`
- [ ] Região: `sa-east-1`
- [ ] Política de acesso configurada

### ✅ ECS (Elastic Container Service)
- [ ] Cluster: `iscoolgpt-cluster2`
- [ ] Task Definition: `iscoolgpt-task`
- [ ] Service: `iscoolgpt-service`
- [ ] Log Group: `/ecs/iscoolgpt-task`

### ✅ IAM (Identity and Access Management)
- [ ] Role: `ecsTaskExecutionRole` (para tasks)
- [ ] Usuário com permissões para GitHub Actions:
  - ECR: `ecr:*`
  - ECS: `ecs:UpdateService`, `ecs:Describe*`
  - EC2: `ec2:DescribeNetworkInterfaces`

### ✅ Secrets Manager
- [ ] Secret: `openrouter-api-key` ou `iscoolgpt/openrouter-key`
- [ ] Valor: Chave da API OpenRouter

### ✅ VPC e Networking
- [ ] VPC configurada
- [ ] Subnets públicas
- [ ] Security Group permitindo porta 3000

---

## 🎯 Resolução Rápida por Erro

### Erro: "ClusterNotFoundException"
```bash
aws ecs create-cluster --cluster-name iscoolgpt-cluster2 --region sa-east-1
```

### Erro: "ServiceNotFoundException"
Use o script `setup-cloudshell.sh` ou `setup-simple.sh` para criar o serviço

### Erro: "TaskDefinitionNotFoundException"
Use o script `setup-cloudshell.sh` ou `setup-simple.sh` para criar a task definition

### Erro: "RepositoryNotFoundException"
```bash
aws ecr create-repository --repository-name iscoolgpt --region sa-east-1
```

### Erro: "AccessDeniedException"
Verifique permissões IAM do usuário usado no GitHub Actions

---

## 📚 Referências

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [GitHub Actions AWS](https://github.com/aws-actions)

