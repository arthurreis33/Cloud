# 🚀 Setup via AWS CloudShell

Use este método para criar todos os recursos AWS com acesso total!

## ✅ Passo 1: Abrir CloudShell

1. Abra o console AWS: https://176977333713.signin.aws.amazon.com/console
2. No canto superior direito, clique no ícone de **terminal** (>_)
3. Selecione **CloudShell**
4. Aguarde a inicialização (leva 30 segundos)

## ✅ Passo 2: Fazer Upload do Script

No CloudShell, você pode fazer upload do arquivo `setup-cloudshell.sh`:

### Opção A: Via Upload Direto
1. No CloudShell, clique em **ações** (⋮) 
2. Selecione **Upload file**
3. Selecione o arquivo `setup-cloudshell.sh` do seu computador
4. Clique em **Upload**

### Opção B: Copiar e Colar
1. Abra o arquivo `setup-cloudshell.sh` no seu editor
2. Copie TODO o conteúdo
3. No CloudShell, crie um novo arquivo:
   ```bash
   cat > setup.sh << 'EOF'
   # Cole todo o conteúdo aqui
   EOF
   ```

## ✅ Passo 3: Executar o Script

No CloudShell, rode:

```bash
chmod +x setup.sh
./setup.sh
```

O script vai:
- ✅ Criar Repositório ECR
- ✅ Criar Log Group CloudWatch
- ✅ Criar Security Group
- ✅ Criar Task Definition
- ✅ Criar ECS Service

## ✅ Passo 4: Monitorar Execução

Você verá cada etapa com ✅ ou ⚠️ 

Se tudo passar, você terá:
- ECR: iscoolgpt
- Task Definition: iscoolgpt-task
- Service: iscoolgpt-service
- Log Group: /ecs/iscoolgpt-task

## ✅ Passo 5: Fazer Commit e Push

Após o script terminar, volta para seu terminal local:

```powershell
git add .
git commit -m "chore: preparar infraestrutura AWS"
git push origin main
```

## ✅ Passo 6: Monitorar GitHub Actions

Vá para: https://github.com/arthurreis33/Cloud/actions

Você verá:
1. **CI** rodando (testes e lint)
2. **CD** rodando (build Docker e push ECR)
3. Deploy no ECS automaticamente

## 🎯 Durante o Deploy

Os logs do GitHub Actions mostrarão:
- Status do build Docker
- Status do push no ECR
- Status do deploy ECS
- **URL da API** (ex: http://xxx.xxx.xxx.xxx:3000)

## ✅ Passo 7: Testar a API

Após os logs mostrarem sucesso:

```powershell
# Substituir com o IP do log
$IP = "xxx.xxx.xxx.xxx"

curl -X POST http://$IP:3000/api/tutor/ask `
  -H "Content-Type: application/json" `
  -d '{"question": "O que é Docker?"}'
```

Você deve receber uma resposta da IA!

## 🆘 Troubleshooting

### Se receber erro de permissão no CloudShell
- Use o console com conta de root/admin
- Verifique se o IAM está correto

### Se o Service não inicia
- Verifique os logs em CloudWatch: `/ecs/iscoolgpt-task`
- Procure por erros de inicialização

### Se a porta 3000 não está acessível
- Verifique Security Group: `iscoolgpt-sg`
- Verifique se tem regra para porta 3000

---

**Pronto! Siga estes passos e seu CI/CD estará completo!** 🎉
