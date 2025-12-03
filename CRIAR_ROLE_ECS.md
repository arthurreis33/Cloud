# 🔧 Como Criar a Role ecsTaskExecutionRole

## 📋 Passo a Passo

### 1. Acessar IAM
1. No console AWS, procure por **IAM** na barra de busca
2. Clique em **IAM**

### 2. Criar Nova Role
1. No menu lateral esquerdo, clique em **Funções** (Roles)
2. Clique no botão **Criar função** (Create role)

### 3. Selecionar Tipo de Confiança
1. Na seção **Tipo de entidade confiável**, selecione:
   - **Serviço da AWS** (AWS service)
2. Na lista de serviços, procure e selecione:
   - **Elastic Container Service**
3. Abaixo, selecione o caso de uso:
   - **Elastic Container Service Task** (não Task Role, mas Task Execution Role)
4. Clique em **Próximo**

### 4. Anexar Políticas
1. Na busca de políticas, procure por: `AmazonECSTaskExecutionRolePolicy`
2. **Marque a caixa** ao lado desta política
3. Clique em **Próximo**

### 5. Configurar Nome
1. **Nome da função:** `ecsTaskExecutionRole`
2. **Descrição:** `Role para execução de tarefas ECS`
3. Clique em **Criar função**

### 6. Verificar
1. Você deve ver a role `ecsTaskExecutionRole` na lista
2. Clique nela para verificar se está correta

---

## ✅ Verificação

A role deve ter:
- **Nome:** `ecsTaskExecutionRole`
- **Política anexada:** `AmazonECSTaskExecutionRolePolicy`
- **Entidade confiável:** `ecs-tasks.amazonaws.com`

---

## 🎯 Próximo Passo

Depois de criar a role, você pode continuar criando a **Task Definition** no ECS.

