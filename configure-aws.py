#!/usr/bin/env python3
import os
import sys

print("╔════════════════════════════════════════════════════════════════════╗")
print("║           CONFIGURAR CREDENCIAIS AWS (IAM User)                   ║")
print("╚════════════════════════════════════════════════════════════════════╝")
print()
print("Você criou um usuário IAM 'github-actions-deploy' com Access Keys.")
print("Essas credenciais foram exibidas UMA VEZ durante a criação.")
print()
print("SE VOCÊ PERDEU as credenciais:")
print("1. Vá em: AWS Console → IAM → Usuários → github-actions-deploy")
print("2. Aba: Credenciais de segurança")
print("3. Clique em: Criar chave de acesso")
print("4. Copie a nova Access Key ID e Secret Access Key")
print()
print("=" * 70)
print()

access_key = input("📝 Digite seu AWS Access Key ID (ex: AKIA...): ").strip()
secret_key = input("📝 Digite seu AWS Secret Access Key (ex: ...): ").strip()

if not access_key or not secret_key:
    print("❌ Credenciais não podem estar vazias!")
    sys.exit(1)

# Validar formato básico
if not access_key.startswith('AKIA'):
    print("⚠️  Aviso: Access Key não tem formato esperado (deve começar com AKIA)")

# Criar diretório .aws se não existir
aws_dir = os.path.expanduser('~/.aws')
os.makedirs(aws_dir, exist_ok=True)

# Criar arquivo de credenciais
credentials_file = os.path.join(aws_dir, 'credentials')
with open(credentials_file, 'w') as f:
    f.write(f"""[default]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
""")

# Criar arquivo de configuração
config_file = os.path.join(aws_dir, 'config')
with open(config_file, 'w') as f:
    f.write("""[default]
region = sa-east-1
output = json
""")

print()
print("✅ Credenciais AWS configuradas com sucesso!")
print(f"   Arquivo: {credentials_file}")
print()
print("Próximo passo: Execute o setup-aws.py novamente")
