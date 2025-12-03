# 🚀 Guia Completo de Configuração AWS

## 📋 Índice
1. [Configuração Inicial da Conta AWS](#1-configuração-inicial-da-conta-aws)
2. [Criar Usuário IAM para GitHub Actions](#2-criar-usuário-iam-para-github-actions)
3. [Criar ECR (Elastic Container Registry)](#3-criar-ecr-elastic-container-registry)
4. [Criar ECS Cluster](#4-criar-ecs-cluster)
5. [Criar Task Definition](#5-criar-task-definition)
6. [Criar ECS Service](#6-criar-ecs-service)
7. [Configurar GitHub Secrets](#7-configurar-github-secrets)
8. [Testar Deploy](#8-testar-deploy)

---

## 1. Configuração Inicial da Conta AWS

### 1.1. Criar Conta AWS
- Acesse: https://aws.amazon.com/
- Clique em "Criar uma conta AWS"
- Preencha seus dados
- **IMPORTANTE:** Configure alertas de billing para não ter surpresas!

### 1.2. Configurar Região
- No canto superior direito, escolha a região: **São Paulo (sa-east-1)**
- Todos os recursos serão criados nesta região

### 1.3. Ativar MFA (Recomendado)
- Vá em **IAM** → **Usuários** → Seu usuário
- Aba **Segurança** → **Ativar MFA**

---

## 2. Criar Usuário IAM para GitHub Actions

### 2.1. Criar Usuário
1. Acesse **IAM** no console AWS
2. Clique em **Usuários** → **Adicionar usuários**
3. Nome: `github-actions-deploy`
4. Tipo de acesso: **Acesso programático**
5. Clique em **Próximo**

### 2.2. Criar Política Personalizada
1. Vá em **Políticas** → **Criar política**
2. Clique em **JSON** e cole:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecs:UpdateService",
                "ecs:DescribeServices",
                "ecs:DescribeTaskDefinition",
                "ecs:RegisterTaskDefinition"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": "arn:aws:iam::*:role/ecsTaskExecutionRole"
        }
    ]
}
```

3. Nome da política: `GitHubActionsDeployPolicy`
4. Clique em **Criar política**

### 2.3. Anexar Política ao Usuário
1. Volte em **Usuários** → `github-actions-deploy`
2. Aba **Permissões** → **Adicionar permissões**
3. Selecione **Anexar políticas diretamente**
4. Procure e selecione `GitHubActionsDeployPolicy`
5. Clique em **Próximas etapas** → **Adicionar permissões**

### 2.4. Criar Access Keys
1. No usuário `github-actions-deploy`, aba **Credenciais de segurança**
2. Clique em **Criar chave de acesso**
3. Tipo: **Aplicação em execução fora da AWS**
4. Descrição: `GitHub Actions CI/CD`
5. Clique em **Criar chave de acesso**
6. **IMPORTANTE:** Copie e salve:
   - **Access Key ID**
   - **Secret Access Key** (só aparece uma vez!)

---

## 3. Criar ECR (Elastic Container Registry)

### 3.1. Criar Repositório
1. Acesse **ECR** no console AWS
2. Clique em **Criar repositório**
3. Configurações:
   - **Visibilidade:** Privado
   - **Nome do repositório:** `iscoolgpt`
   - **Tag de imagem:** Deixar padrão
4. Clique em **Criar repositório**

### 3.2. Anotar URI do Repositório
- Copie a **URI do repositório** (algo como: `123456789012.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt`)
- Você vai precisar disso depois

---

## 4. Criar ECS Cluster

### 4.1. Criar Cluster
1. Acesse **ECS** no console AWS
2. Clique em **Clusters** → **Criar cluster**
3. Configurações:
   - **Nome do cluster:** `iscoolgpt-cluster`
   - **Infraestrutura:** **AWS Fargate** (serverless, sem gerenciar servidores)
4. Clique em **Criar**

### 4.2. Criar Role de Execução (se não existir)
1. Acesse **IAM** → **Funções**
2. Procure por `ecsTaskExecutionRole`
3. Se não existir:
   - Clique em **Criar função**
   - Tipo: **AWS service** → **Elastic Container Service** → **Elastic Container Service Task**
   - Clique em **Próximo**
   - Selecione política: `AmazonECSTaskExecutionRolePolicy`
   - Nome: `ecsTaskExecutionRole`
   - Clique em **Criar função**

---

## 5. Criar Task Definition

### 5.1. Criar Task Definition
1. No **ECS**, vá em **Task definitions** → **Criar nova definição de tarefa**
2. Configurações:
   - **Família:** `iscoolgpt-task`
   - **Tipo de lançamento:** Fargate
   - **Sistema operacional/Arquitetura:** Linux/X86_64
   - **CPU:** 0.25 vCPU (256)
   - **Memória:** 0.5 GB (512)
   - **Role de execução da tarefa:** `ecsTaskExecutionRole`

### 5.2. Configurar Container
1. Clique em **Adicionar container**
2. Configurações:
   - **Nome do container:** `iscoolgpt-app`
   - **URI da imagem:** Cole a URI do ECR (ex: `123456789012.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt:latest`)
   - **Porta de mapeamento:** `3000` (protocolo TCP)
   - **Variáveis de ambiente:**
     - `OPENROUTER_API_KEY` = (deixe vazio, vamos usar Secrets Manager depois)
     - `PORT` = `3000`
     - `APP_URL` = (deixe vazio por enquanto)
   - **Health check:** (opcional, pode deixar vazio)
3. Clique em **Adicionar**
4. Clique em **Criar**

---

## 6. Criar ECS Service

### 6.1. Criar Service
1. No cluster `iscoolgpt-cluster`, clique em **Serviços** → **Criar**
2. Configurações:
   - **Família:** `iscoolgpt-task`
   - **Revisão:** `1` (latest)
   - **Nome do serviço:** `iscoolgpt-service`
   - **Tipo de serviço:** Replica
   - **Número de tarefas:** `1`

### 6.2. Configurar Rede
1. **VPC:** Selecione a VPC padrão
2. **Subnets:** Selecione pelo menos 2 subnets públicas
3. **Grupo de segurança:** Clique em **Editar**
   - Adicione regra:
     - Tipo: **Personalizado TCP**
     - Porta: `3000`
     - Origem: **Qualquer lugar (0.0.0.0/0)**
4. **Auto-assign public IP:** **Habilitado**

### 6.3. Configurar Load Balancer (Opcional)
- Por enquanto, pode pular (vamos usar IP público direto)

### 6.4. Criar Service
1. Revise as configurações
2. Clique em **Criar**

---

## 7. Configurar GitHub Secrets

### 7.1. Acessar Secrets no GitHub
1. Vá no seu repositório GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Clique em **New repository secret**

### 7.2. Adicionar Secrets
Adicione os seguintes secrets:

#### Secret 1: `AWS_ACCESS_KEY_ID`
- **Name:** `AWS_ACCESS_KEY_ID`
- **Value:** (Access Key ID que você salvou no passo 2.4)

#### Secret 2: `AWS_SECRET_ACCESS_KEY`
- **Name:** `AWS_SECRET_ACCESS_KEY`
- **Value:** (Secret Access Key que você salvou no passo 2.4)

#### Secret 3: `OPENROUTER_API_KEY`
- **Name:** `OPENROUTER_API_KEY`
- **Value:** (Sua chave OpenRouter do arquivo .env)

### 7.3. Atualizar Workflow CD
1. Vá em `.github/workflows/cd.yml`
2. Verifique se os nomes estão corretos:
   - `ECR_REPOSITORY: iscoolgpt`
   - `ECS_CLUSTER: iscoolgpt-cluster`
   - `ECS_SERVICE: iscoolgpt-service`
   - `AWS_REGION: sa-east-1`

---

## 8. Testar Deploy

### 8.1. Fazer Push para GitHub
```bash
git add .
git commit -m "Configuração inicial AWS"
git push origin main
```

### 8.2. Verificar GitHub Actions
1. No GitHub, vá em **Actions**
2. Você deve ver o workflow rodando
3. Clique no workflow para ver os logs

### 8.3. Verificar ECS
1. No console AWS, vá em **ECS** → **Clusters** → `iscoolgpt-cluster`
2. Aba **Serviços** → `iscoolgpt-service`
3. Aba **Tarefas** → Veja se a tarefa está rodando
4. Clique na tarefa → Veja o **IP público**

### 8.4. Testar API
```bash
# Substitua pelo IP público da tarefa
curl http://IP_PUBLICO:3000/
```

---

## 🔧 Configurações Adicionais

### Configurar Secrets Manager (Recomendado)
Em vez de colocar a chave OpenRouter na Task Definition, use Secrets Manager:

1. **Secrets Manager** → **Armazenar um novo segredo**
2. Tipo: **Outro tipo de segredo**
3. Cole: `{"OPENROUTER_API_KEY": "sua_chave_aqui"}`
4. Nome: `iscoolgpt/openrouter-key`
5. Na Task Definition, adicione:
   - **Secrets** → Adicionar
   - **Nome:** `OPENROUTER_API_KEY`
   - **Valor de:** `arn:aws:secretsmanager:sa-east-1:ACCOUNT_ID:secret:iscoolgpt/openrouter-key`

### Configurar CloudWatch Logs
1. Na Task Definition, em **Logging**:
   - **Driver de log:** `awslogs`
   - **Opções:**
     - `awslogs-group`: `/ecs/iscoolgpt`
     - `awslogs-region`: `sa-east-1`
     - `awslogs-stream-prefix`: `ecs`

2. Criar Log Group:
   - **CloudWatch** → **Log groups** → **Criar grupo de logs**
   - Nome: `/ecs/iscoolgpt`

---

## ⚠️ Importante: Custos

### Recursos Gratuitos (Free Tier)
- **ECR:** 500 MB/mês grátis
- **ECS Fargate:** Não tem free tier (cobrado por uso)
- **Data Transfer:** Primeiros 100 GB/mês grátis

### Estimativa de Custos (Fargate)
- **CPU:** ~$0.04/hora (0.25 vCPU)
- **Memória:** ~$0.004/hora (0.5 GB)
- **Total:** ~$0.044/hora = ~$32/mês se rodar 24/7

### Dicas para Economizar
1. Use **instâncias spot** (não disponível em Fargate)
2. Desligue o serviço quando não estiver usando
3. Configure **auto-scaling** para 0 tarefas quando não houver tráfego
4. Monitore custos no **Cost Explorer**

---

## 📝 Checklist Final

- [ ] Conta AWS criada e configurada
- [ ] Usuário IAM criado com permissões
- [ ] Access Keys criadas e salvas
- [ ] ECR repositório criado
- [ ] ECS cluster criado
- [ ] Task definition criada
- [ ] ECS service criado
- [ ] GitHub secrets configurados
- [ ] Workflow CD atualizado com nomes corretos
- [ ] Primeiro deploy testado
- [ ] API acessível via IP público

---

## 🆘 Troubleshooting

### Erro: "Access Denied"
- Verifique se as permissões IAM estão corretas
- Verifique se as Access Keys estão corretas no GitHub

### Erro: "Repository not found"
- Verifique se o nome do repositório ECR está correto
- Verifique se está na região correta

### Tarefa não inicia
- Verifique os logs do CloudWatch
- Verifique se a imagem foi enviada corretamente para o ECR
- Verifique se as variáveis de ambiente estão corretas

### API não responde
- Verifique se o security group permite porta 3000
- Verifique se o IP público está correto
- Verifique os logs do CloudWatch

---

**Pronto! Siga os passos na ordem e você terá tudo configurado!** 🚀

