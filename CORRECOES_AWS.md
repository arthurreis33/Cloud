# 🔧 Correções e Ajustes AWS

## ✅ Correções Aplicadas

### 1. Nome do Cluster Atualizado
- ❌ **Antes:** `iscoolgpt-cluster`
- ✅ **Agora:** `iscoolgpt-cluster2`

**Arquivo atualizado:**
- `.github/workflows/cd.yml` - Linha 10

---

## 📋 Checklist Atualizado

### Recursos AWS (com nomes corretos)
- [ ] **ECR Repository:** `iscoolgpt`
- [ ] **ECS Cluster:** `iscoolgpt-cluster2` ✅
- [ ] **ECS Service:** `iscoolgpt-service`
- [ ] **Task Definition:** `iscoolgpt-task`
- [ ] **IAM Role:** `ecsTaskExecutionRole` (precisa criar)

---

## 🔧 Criar Role ecsTaskExecutionRole

### Opção 1: Via Console (Recomendado)

1. **Acesse IAM:**
   - Console AWS → Buscar "IAM" → **Funções**

2. **Criar Função:**
   - Clique em **Criar função**

3. **Tipo de Confiança:**
   - Selecione **Serviço da AWS**
   - Procure: **Elastic Container Service**
   - Selecione: **Elastic Container Service Task**
   - Clique em **Próximo**

4. **Políticas:**
   - Procure: `AmazonECSTaskExecutionRolePolicy`
   - **Marque a caixa** ✅
   - Clique em **Próximo**

5. **Nome:**
   - **Nome da função:** `ecsTaskExecutionRole`
   - Clique em **Criar função**

### Opção 2: Via AWS CLI

```bash
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ecs-tasks.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }'

aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

---

## 📝 Verificar Configuração

### 1. Verificar Cluster
```bash
aws ecs describe-clusters --clusters iscoolgpt-cluster2
```

### 2. Verificar Role
```bash
aws iam get-role --role-name ecsTaskExecutionRole
```

### 3. Verificar Workflow
O arquivo `.github/workflows/cd.yml` já está atualizado com:
- `ECS_CLUSTER: iscoolgpt-cluster2`

---

## 🎯 Próximos Passos

1. ✅ **Cluster nome atualizado no workflow** - FEITO
2. ⏳ **Criar role `ecsTaskExecutionRole`** - FAZER AGORA
3. ⏳ **Criar Task Definition** (usando a role criada)
4. ⏳ **Criar ECS Service**

---

## 💡 Dica

Se você já criou a Task Definition antes de criar a role, você precisará:
1. Criar a role primeiro
2. Editar a Task Definition existente
3. Selecionar a role `ecsTaskExecutionRole` no campo "Role de execução da tarefa"

---

**Veja o arquivo `CRIAR_ROLE_ECS.md` para instruções detalhadas!**

