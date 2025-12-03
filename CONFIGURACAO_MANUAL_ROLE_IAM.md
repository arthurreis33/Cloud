# ⚠️ CONFIGURAÇÃO MANUAL AWS - IsCoolGPT

Seu usuário IAM `github-actions-deploy` não tem permissão para criar a Role `ecsTaskExecutionRole`. Você precisa fazer essa parte manualmente pelo console AWS com sua conta.

## 📋 Passos Manuais no Console AWS

### 1. Criar Role IAM (ecsTaskExecutionRole) - FAZER VIA CONSOLE

1. Abra: https://console.aws.amazon.com/iam/
2. Clique em **Funções** → **Criar função**
3. **Tipo de Confiança:**
   - Selecione: **Serviço da AWS**
   - Procure: **Elastic Container Service**
   - Selecione: **Elastic Container Service Task**
   - Clique em **Próximo**

4. **Políticas:**
   - Procure: `AmazonECSTaskExecutionRolePolicy`
   - Marque a caixa ✅
   - Clique em **Próximo**

5. **Nome da Função:**
   - Digite: `ecsTaskExecutionRole`
   - Clique em **Criar função**

6. ✅ Role criada!

---

### 2. Depois que a Role Estiver Criada

Após criar a role manualmente, execute este script Python para completar o setup:

```bash
python setup-aws-final.py
```

Esse script vai:
✅ Criar Repositório ECR (`iscoolgpt`)
✅ Criar Cluster ECS (`iscoolgpt-cluster2`)
✅ Criar Log Group (CloudWatch)
✅ Criar Secret (OpenRouter API Key)
✅ Criar Task Definition
✅ Criar Security Group
✅ Criar ECS Service

---

## ❓ Por que o usuário IAM não pode criar a role?

Seu usuário `github-actions-deploy` foi criado com uma política personalizada que permite apenas:
- Fazer push de imagens no ECR ✅
- Atualizar o ECS Service ✅
- Outras operações no ECS ✅

Mas **não permite criar roles IAM** (isso é restrito a usuários com permissão administrativa).

## ✅ Checklist

- [ ] Role `ecsTaskExecutionRole` criada manualmente no console
- [ ] Script `setup-aws-final.py` executado com sucesso
- [ ] GitHub Secrets configurados (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, OPENROUTER_API_KEY)
- [ ] Primeira imagem Docker enviada para ECR
- [ ] GitHub Actions dispara automaticamente e faz deploy
- [ ] IP público da tarefa obtido e testado

---

## 🚨 Importante: Segurança

**NUNCA** coloque suas credenciais de root ou admin em um repositório Git ou GitHub Secrets!

Use SEMPRE um usuário IAM específico com permissões limitadas, como o `github-actions-deploy`.
