#!/bin/bash

set -e

REGION="sa-east-1"
CLUSTER="iscoolgpt-cluster2"
SERVICE="iscoolgpt-service"
REPO="iscoolgpt"

echo "🔐 Fazendo login no ECR..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO"

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI

echo "🏗️  Fazendo build da imagem..."
docker build --platform linux/amd64 -t $ECR_URI:latest .

echo "📤 Enviando imagem para ECR..."
docker push $ECR_URI:latest

echo "🚀 Atualizando serviço ECS..."
aws ecs update-service \
  --cluster $CLUSTER \
  --service $SERVICE \
  --force-new-deployment \
  --region $REGION \
  --query 'service.serviceName' \
  --output text

echo "⏳ Aguardando serviço estabilizar (30 segundos)..."
sleep 30

echo "📋 Obtendo IP público..."
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER --service-name $SERVICE --region $REGION --query 'taskArns[0]' --output text)

if [ -z "$TASK_ARN" ]; then
    echo "❌ Nenhuma tarefa encontrada. Verifique o serviço no console AWS."
    exit 1
fi

IP=$(aws ecs describe-tasks --cluster $CLUSTER --tasks $TASK_ARN --region $REGION --query 'tasks[0].attachments[0].details[?name==`publicIPv4Address`].value' --output text)

if [ -z "$IP" ] || [ "$IP" == "None" ]; then
    echo "⚠️  IP público não encontrado. Verifique no console AWS:"
    echo "   ECS → Clusters → $CLUSTER → Services → $SERVICE → Tasks"
else
    echo ""
    echo "✅ Deploy concluído!"
    echo "🌐 IP Público: $IP"
    echo ""
    echo "🧪 Testar API:"
    echo "   curl http://$IP:3000/"
    echo "   curl -X POST http://$IP:3000/api/tutor/ask -H 'Content-Type: application/json' -d '{\"question\": \"O que é Docker?\"}'"
fi

