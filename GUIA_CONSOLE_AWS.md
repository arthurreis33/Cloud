# 📖 Guia Completo - Setup AWS via Console

Siga este guia **na ordem exata** para configurar sua infraestrutura AWS para o IsCoolGPT.

---

## ✅ Passo 1: Criar Role IAM (ecsTaskExecutionRole)

### 1.1 - Acessar IAM
- Abra: https://console.aws.amazon.com/
- Na barra de busca no topo, digite: **IAM**
- Clique em **IAM** (Gerenciamento de Identidade e Acesso)

### 1.2 - Criar Nova Role
- No menu esquerdo, clique em **Funções**
- Clique no botão azul **Criar função**

### 1.3 - Selecionar Tipo de Confiança
- Em **Tipo de entidade confiável**, selecione: **Serviço da AWS**
- Na caixa de busca de serviços, digite: **ecs**
- Selecione **Elastic Container Service**
- Abaixo, procure por: **Elastic Container Service Task**
- Clique em **Próximo**

### 1.4 - Anexar Políticas
- Na caixa de busca, procure: **AmazonECSTaskExecutionRolePolicy**
- ✅ Marque a caixa ao lado desta política
- Clique em **Próximo**

### 1.5 - Nomear a Role
- **Nome da função:** `ecsTaskExecutionRole`
- **Descrição:** `Role para execução de tarefas ECS`
- Clique em **Criar função**

✅ **Role criada!** Você verá: `ecsTaskExecutionRole` na lista de funções

---

## ✅ Passo 2: Criar Repositório ECR

### 2.1 - Acessar ECR
- Na barra de busca, digite: **ECR**
- Clique em **Elastic Container Registry**

### 2.2 - Criar Repositório
- Clique em **Criar repositório** (Create repository)

### 2.3 - Configurar Repositório
- **Nome do repositório:** `iscoolgpt`
- **Tag de imagem mutável:** ✅ Marque (Mutable)
- **Verificação de imagem no push:** ✅ Marque (Scan on push)
- Clique em **Criar repositório**

✅ **Repositório criado!** Anote a **URI** que aparecer (ex: `176977333713.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt`)

---

## ✅ Passo 3: Criar Cluster ECS

### 3.1 - Acessar ECS
- Na barra de busca, digite: **ECS**
- Clique em **Elastic Container Service**

### 3.2 - Criar Cluster
- Clique em **Clusters** no menu esquerdo
- Clique em **Criar cluster**

### 3.3 - Configurar Cluster
- **Nome do cluster:** `iscoolgpt-cluster`
- Deixe as outras opções com os valores padrão
- Clique em **Criar**

✅ **Cluster criado!**

---

## ✅ Passo 4: Criar Security Group

### 4.1 - Acessar EC2
- Na barra de busca, digite: **EC2**
- Clique em **EC2 Dashboard**

### 4.2 - Criar Security Group
- No menu esquerdo, clique em **Security Groups** (Grupos de segurança)
- Clique em **Criar grupo de segurança**

### 4.3 - Configurar Security Group
- **Nome do grupo de segurança:** `iscoolgpt-sg`
- **Descrição:** `Security Group para IsCoolGPT`
- Deixe a VPC padrão selecionada

### 4.4 - Adicionar Regra de Entrada
- Clique em **Adicionar regra**
- **Tipo:** TCP customizado
- **Intervalo de portas:** `3000`
- **Fonte:** `0.0.0.0/0` (Qualquer lugar)
- Clique em **Criar grupo de segurança**

✅ **Security Group criado!**

---

## ✅ Passo 5: Criar Log Group no CloudWatch

### 5.1 - Acessar CloudWatch
- Na barra de busca, digite: **CloudWatch**
- Clique em **CloudWatch**

### 5.2 - Criar Log Group
- No menu esquerdo, clique em **Grupos de log** (Log Groups)
- Clique em **Criar grupo de log**

### 5.3 - Configurar Log Group
- **Nome do grupo de log:** `/ecs/iscoolgpt-task`
- Clique em **Criar grupo de log**

✅ **Log Group criado!**

---

## ✅ Passo 6: Criar Secret no Secrets Manager

### 6.1 - Acessar Secrets Manager
- Na barra de busca, digite: **Secrets Manager**
- Clique em **Secrets Manager**

### 6.2 - Criar Secret
- Clique em **Armazenar um novo segredo** (Store a new secret)

### 6.3 - Configurar Secret
- **Tipo de segredo:** Selecione **Outro tipo de segredo** (Other type of secret)
- Na seção de pares chave-valor, coloque:
  - **Chave:** `OPENROUTER_API_KEY`
  - **Valor:** `sk-or-v1-xxxxxxxxxxxxxx` (sua chave OpenRouter)

### 6.4 - Nomear Secret
- **Nome do segredo:** `openrouter-api-key`
- Clique em **Armazenar segredo** (Store secret)

✅ **Secret criado!**

---

## ✅ Passo 7: Criar Task Definition

### 7.1 - Acessar ECS Task Definitions
- Na barra de busca, digite: **ECS**
- Clique em **Elastic Container Service**
- No menu esquerdo, clique em **Definições de tarefa** (Task Definitions)
- Clique em **Criar nova definição de tarefa**

### 7.2 - Configurar Definição
- **Nome da família de tarefas:** `iscoolgpt-task`
- **Compatibilidade:** Selecione **FARGATE**

### 7.3 - Configurar Recursos
- **CPU:** `0.25 vCPU`
- **Memória:** `512 MB`

### 7.4 - Configurar Role
- **Role de execução de tarefa:** `ecsTaskExecutionRole`

### 7.5 - Adicionar Container
- Clique em **Adicionar container**
- **Nome do container:** `iscoolgpt-app`
- **Imagem URI:** `176977333713.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt:latest`
  - (Substitua com sua URI do ECR obtida no Passo 2)

### 7.6 - Configurar Porta
- **Mapeamento de porta do container:**
  - **Porta do container:** `3000`
  - **Protocolo:** `tcp`

### 7.7 - Configurar Variáveis de Ambiente
- Role para baixo e encontre **Ambiente**
- Adicione as variáveis:
  - **PORT** = `3000`
  - **PYTHONUNBUFFERED** = `1`
  - **LLM_PROVIDER** = `openrouter`

### 7.8 - Configurar Secrets
- Role para baixo e encontre **Secrets (from Secrets Manager)**
- **Nome:** `OPENROUTER_API_KEY`
- **ARN do valor:** `arn:aws:secretsmanager:sa-east-1:176977333713:secret:openrouter-api-key`

### 7.9 - Configurar Logs
- Role para baixo até encontrar **Log configuration**
- **CloudWatch Log Group:** `/ecs/iscoolgpt-task`
- **Log stream prefix:** `ecs`
- **Região:** `sa-east-1`

### 7.10 - Criar Task Definition
- Clique em **Criar**

✅ **Task Definition criada!**

---

## ✅ Passo 8: Criar ECS Service

### 8.1 - Acessar Cluster
- Na barra de busca, digite: **ECS**
- Clique em **Elastic Container Service**
- Clique em **Clusters**
- Clique em **iscoolgpt-cluster**

### 8.2 - Criar Service
- Clique em **Criar** (Create)

### 8.3 - Configurar Configuração do Service
- **Família de definição de tarefa:** `iscoolgpt-task`
- **Revisão da definição de tarefa:** Selecione a versão mais recente
- **Capacidade de fornecedor de serviço:** Selecione **FARGATE**

### 8.4 - Configurar Deployment
- **Nome do serviço:** `iscoolgpt-service`
- **Número desejado de tarefas:** `1`
- Deixe o resto com os valores padrão
- Clique em **Próximo**

### 8.5 - Configurar Rede
- **VPC:** Selecione a VPC padrão
- **Subnets:** Selecione pelo menos 2 subnets
- **Security groups:** Selecione `iscoolgpt-sg`
- **Atribuir IP público:** ✅ Ativado (ENABLED)
- Clique em **Próximo**

### 8.6 - Configurar Balanceamento de Carga (pular)
- Deixe como **Não usar load balancer**
- Clique em **Próximo**

### 8.7 - Revisar
- Revise as configurações
- Clique em **Criar serviço**

✅ **Service criado!**

---

## ✅ Passo 9: Fazer Push da Imagem Docker

Agora você precisa fazer build e push da imagem Docker para o ECR:

```powershell
# 1. Fazer build da imagem
docker build -t iscoolgpt .

# 2. Login no ECR (substitua com seus dados)
aws ecr get-login-password --region sa-east-1 | docker login --username AWS --password-stdin 176977333713.dkr.ecr.sa-east-1.amazonaws.com

# 3. Taggear imagem
docker tag iscoolgpt:latest 176977333713.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt:latest

# 4. Fazer push
docker push 176977333713.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt:latest
```

✅ **Imagem enviada!**

---

## ✅ Passo 10: Fazer Deploy Automático

Depois que a imagem estiver no ECR:
1. Vá para seu repositório GitHub: https://github.com/arthurreis33/Cloud
2. Faça um commit e push para `main`
3. Vá para a aba **Actions** do repositório
4. Observe o workflow `CI - Deploy AWS` executar
5. Quando terminar, você verá a URL da API nos logs

---

## ✅ Passo 11: Testar a API

Assim que o deployment terminar:

```powershell
# Obter o IP público da tarefa (será mostrado nos logs do GitHub Actions)
$PUBLIC_IP = "xxx.xxx.xxx.xxx"

# Testar endpoint
curl -X POST http://$PUBLIC_IP:3000/api/tutor/ask `
  -H "Content-Type: application/json" `
  -d '{"question": "O que é Docker?"}'
```

---

## 📝 Checklist Final

- [ ] Role IAM `ecsTaskExecutionRole` criada
- [ ] Repositório ECR `iscoolgpt` criado
- [ ] Cluster ECS `iscoolgpt-cluster` criado
- [ ] Security Group `iscoolgpt-sg` criado
- [ ] Log Group `/ecs/iscoolgpt-task` criado
- [ ] Secret `openrouter-api-key` criado
- [ ] Task Definition `iscoolgpt-task` criada
- [ ] Service `iscoolgpt-service` criado
- [ ] Imagem Docker feita push para ECR
- [ ] GitHub Actions rodou com sucesso
- [ ] API testada e funcionando

---

## 🆘 Problemas Comuns

### "Erro de permissão no ECS"
- Verifique se a role `ecsTaskExecutionRole` está criada e anexada

### "Tarefa não inicia"
- Verifique os logs em CloudWatch → Log Groups → `/ecs/iscoolgpt-task`
- Procure por mensagens de erro

### "Não consigo fazer push no ECR"
- Certifique-se de que o usuário IAM `github-actions-deploy` tem permissões ECR
- Verifique o comando de login: `aws ecr get-login-password`

### "Porta 3000 não está acessível"
- Verifique se o Security Group `iscoolgpt-sg` permite entrada na porta 3000
- Verifique se o IP público está sendo atribuído à tarefa

---

**Pronto! Siga este guia passo a passo e sua infraestrutura AWS estará configurada!** 🚀
