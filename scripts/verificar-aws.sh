#!/bin/bash

# Script para verificar configuração AWS
# Uso: ./scripts/verificar-aws.sh

echo "🔍 Verificando configuração AWS..."
echo ""

# Verificar se AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI não está instalado"
    echo "   Instale: https://aws.amazon.com/cli/"
    exit 1
fi

echo "✅ AWS CLI instalado"
echo ""

# Verificar credenciais
echo "📋 Verificando credenciais AWS..."
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ Credenciais AWS configuradas"
    aws sts get-caller-identity
else
    echo "❌ Credenciais AWS não configuradas"
    echo "   Execute: aws configure"
fi

echo ""

# Verificar região
REGION=$(aws configure get region)
echo "🌍 Região configurada: ${REGION:-'não configurada'}"

echo ""
echo "📦 Verificando recursos ECR..."
aws ecr describe-repositories --repository-names iscoolgpt 2>/dev/null && echo "✅ ECR repositório 'iscoolgpt' existe" || echo "❌ ECR repositório 'iscoolgpt' não encontrado"

echo ""
echo "🚀 Verificando recursos ECS..."
aws ecs describe-clusters --clusters iscoolgpt-cluster 2>/dev/null && echo "✅ ECS cluster 'iscoolgpt-cluster' existe" || echo "❌ ECS cluster 'iscoolgpt-cluster' não encontrado"

echo ""
echo "✅ Verificação concluída!"

