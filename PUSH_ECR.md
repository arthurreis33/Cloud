# 📝 Comandos para Fazer Push da Imagem Docker

Se você não fez o push ainda, execute estes comandos no PowerShell:

```powershell
# 1. Build da imagem (se ainda não fez)
docker build -t iscoolgpt .

# 2. Login no ECR
aws ecr get-login-password --region sa-east-1 | docker login --username AWS --password-stdin 176977333713.dkr.ecr.sa-east-1.amazonaws.com

# 3. Taggear a imagem com o URI do ECR
docker tag iscoolgpt:latest 176977333713.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt:latest

# 4. Fazer push para o ECR
docker push 176977333713.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt:latest
```

## ✅ Se tudo deu certo:

Você verá algo como:
```
latest: digest: sha256:abc123... size: 5000
The push refers to repository [176977333713.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt]
latest: digest: sha256:def456... size: 5000
```

## 📋 Próximos Passos Após o Push:

1. **Criar Task Definition e Service** (CloudShell script)
2. **GitHub Actions vai fazer deploy automaticamente**
3. **Testar a API**

---

## 🆘 Se der erro de permissão:

```
AccessDeniedException: User is not authorized
```

Isso significa que suas credenciais AWS não têm permissão de push no ECR.
- Verifique se está usando a chave certa
- Se estiver usando a chave de `github-actions-deploy`, ela já tem permissão

---

**Quer que eu crie um script para automatizar isso?**
