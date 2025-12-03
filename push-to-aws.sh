#!/bin/bash

# Script para testar Docker localmente e enviar para AWS ECR
# Uso: ./push-to-aws.sh

# Configurações
AWS_ACCOUNT_ID="176977333713"  # ⚠️ ALTERE PARA SEU ACCOUNT ID SE DIFERENTE
AWS_REGION="sa-east-1"
ECR_REPOSITORY="iscoolgpt"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_TAG="latest"

echo "=========================================="
echo "🐳 TESTAR DOCKER E ENVIAR PARA AWS"
echo "=========================================="
echo ""

# Verificar se AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI não está instalado!"
    echo "   Instale: brew install awscli"
    exit 1
fi

# Verificar se Docker está rodando
if ! docker info &> /dev/null; then
    echo "❌ Docker não está rodando!"
    echo "   Inicie o Docker Desktop"
    exit 1
fi

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado!"
    exit 1
fi

echo "✅ Pré-requisitos verificados"
echo ""

# Opção 1: Testar localmente primeiro
read -p "Deseja testar localmente antes de enviar? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo ""
    echo "🧪 Testando Docker localmente..."
    echo ""
    
    # Parar containers anteriores
    docker compose down 2>/dev/null
    
    # Build e testar
    echo "🔨 Construindo imagem..."
    docker compose build
    
    echo "🚀 Iniciando container..."
    docker compose up -d
    
    echo "⏳ Aguardando 5 segundos..."
    sleep 5
    
    echo "🧪 Testando API..."
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ API está funcionando localmente!"
    else
        echo "⚠️  API não respondeu, mas continuando..."
    fi
    
    echo ""
    read -p "Deseja continuar e enviar para AWS? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "❌ Cancelado pelo usuário"
        exit 0
    fi
    
    # Parar container local
    docker compose down
    echo ""
fi

# Fazer login no ECR
echo "🔐 Fazendo login no ECR..."
if aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${ECR_REGISTRY} 2>/dev/null; then
    echo "✅ Login realizado com sucesso!"
else
    echo "❌ Erro ao fazer login no ECR"
    echo "   Verifique suas credenciais AWS: aws configure"
    exit 1
fi

# Verificar se repositório existe
echo ""
echo "🔍 Verificando repositório ECR..."
if aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --region ${AWS_REGION} &>/dev/null; then
    echo "✅ Repositório ${ECR_REPOSITORY} existe"
else
    echo "⚠️  Repositório não existe, criando..."
    aws ecr create-repository --repository-name ${ECR_REPOSITORY} --region ${AWS_REGION}
    echo "✅ Repositório criado!"
fi

# Build da imagem
echo ""
echo "🔨 Construindo imagem Docker..."
docker build --platform linux/amd64 -t iscoolgpt:local .

if [ $? -ne 0 ]; then
    echo "❌ Erro ao construir imagem"
    exit 1
fi

# Criar tags
echo ""
echo "🏷️  Criando tags..."
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
docker tag iscoolgpt:local ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
docker tag iscoolgpt:local ${ECR_REGISTRY}/${ECR_REPOSITORY}:${TIMESTAMP}

# Push para ECR
echo ""
echo "📤 Enviando imagens para ECR..."
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${TIMESTAMP}

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Imagens enviadas com sucesso!"
    echo ""
    echo "📦 URI da imagem:"
    echo "   ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"
    echo "   ${ECR_REGISTRY}/${ECR_REPOSITORY}:${TIMESTAMP}"
    echo ""
    echo "🚀 Próximo passo: Atualizar o serviço ECS"
    echo "   aws ecs update-service \\"
    echo "     --cluster iscoolgpt-cluster2 \\"
    echo "     --service iscoolgpt-service \\"
    echo "     --force-new-deployment \\"
    echo "     --region ${AWS_REGION}"
else
    echo "❌ Erro ao enviar imagens"
    exit 1
fi

