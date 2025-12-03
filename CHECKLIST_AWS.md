# ✅ Checklist Rápido - Configuração AWS

## 🎯 Ordem de Execução

### Fase 1: Preparação (5 minutos)
- [ ] Conta AWS criada
- [ ] Região configurada: **São Paulo (sa-east-1)**
- [ ] Alertas de billing configurados

### Fase 2: IAM - Permissões (10 minutos)
- [ ] Usuário IAM criado: `github-actions-deploy`
- [ ] Política personalizada criada e anexada
- [ ] Access Keys criadas e **SALVAS EM LOCAL SEGURO**
  - Access Key ID: `_________________`
  - Secret Access Key: `_________________`

### Fase 3: ECR - Registry (5 minutos)
- [ ] Repositório criado: `iscoolgpt`
- [ ] URI do repositório anotada: `_________________`

### Fase 4: ECS - Infraestrutura (15 minutos)
- [ ] Cluster criado: `iscoolgpt-cluster`
- [ ] Role `ecsTaskExecutionRole` verificada/criada
- [ ] Task Definition criada: `iscoolgpt-task`
- [ ] Service criado: `iscoolgpt-service`
- [ ] Security Group configurado (porta 3000 aberta)
- [ ] IP público habilitado

### Fase 5: GitHub - Secrets (5 minutos)
- [ ] Secret `AWS_ACCESS_KEY_ID` adicionado
- [ ] Secret `AWS_SECRET_ACCESS_KEY` adicionado
- [ ] Secret `OPENROUTER_API_KEY` adicionado
- [ ] Workflow `.github/workflows/cd.yml` verificado

### Fase 6: Primeiro Deploy (10 minutos)
- [ ] Código commitado e push para `main`
- [ ] GitHub Actions executando
- [ ] Imagem Docker no ECR
- [ ] Tarefa ECS rodando
- [ ] IP público anotado: `_________________`
- [ ] API testada e funcionando

---

## 📝 Informações Importantes

### Account ID AWS
```
_________________
```
*(Encontre em: IAM → Dashboard → Account ID)*

### Região
```
sa-east-1 (São Paulo)
```

### Nomes dos Recursos
- **ECR Repository:** `iscoolgpt`
- **ECS Cluster:** `iscoolgpt-cluster`
- **ECS Service:** `iscoolgpt-service`
- **Task Definition:** `iscoolgpt-task`

---

## 🚨 Antes de Começar

1. ✅ Tenha sua chave OpenRouter pronta
2. ✅ Tenha um repositório GitHub criado
3. ✅ Tenha o código commitado localmente
4. ✅ Reserve ~1 hora para configurar tudo

---

## 💰 Estimativa de Custos

- **Fargate (0.25 vCPU, 0.5 GB):** ~$0.044/hora
- **24/7:** ~$32/mês
- **Apenas testes:** Desligue quando não usar!

---

## 📚 Documentação Completa

Veja `GUIA_AWS.md` para instruções detalhadas passo a passo.

---

**Boa sorte! 🚀**

