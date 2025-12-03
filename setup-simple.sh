#!/bin/bash
# Script simplificado para criar Task Definition e Service

AWS_REGION="sa-east-1"
AWS_ACCOUNT_ID="176977333713"
ECR_REPOSITORY="iscoolgpt"
ECS_CLUSTER="iscoolgpt-cluster2"
ECS_SERVICE="iscoolgpt-service"
TASK_DEFINITION="iscoolgpt-task"
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY"
LOG_GROUP="/ecs/$TASK_DEFINITION"

echo "=========================================="
echo "🚀 CRIANDO TASK DEFINITION E SERVICE"
echo "=========================================="

# 1. Criar Task Definition
echo ""
echo "📋 Criando Task Definition..."

cat > /tmp/task_def.json << EOF
{
  "family": "$TASK_DEFINITION",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "iscoolgpt-app",
      "image": "$ECR_URI:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "hostPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "PORT", "value": "3000"},
        {"name": "PYTHONUNBUFFERED", "value": "1"},
        {"name": "LLM_PROVIDER", "value": "openrouter"}
      ],
      "secrets": [
        {
          "name": "OPENROUTER_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$AWS_ACCOUNT_ID:secret:openrouter-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "$LOG_GROUP",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

aws ecs register-task-definition \
    --cli-input-json file:///tmp/task_def.json \
    --region $AWS_REGION

if [ $? -eq 0 ]; then
    echo "✅ Task Definition criada!"
else
    echo "⚠️ Task Definition pode já existir"
fi

rm /tmp/task_def.json

# 2. Obter informações de rede
echo ""
echo "📋 Obtendo informações de rede..."

VPC_ID=$(aws ec2 describe-vpcs \
    --filters "Name=is-default,Values=true" \
    --region $AWS_REGION \
    --query 'Vpcs[0].VpcId' \
    --output text)

SUBNETS=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --region $AWS_REGION \
    --query 'Subnets[0:2].SubnetId' \
    --output text)

SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=iscoolgpt-sg" "Name=vpc-id,Values=$VPC_ID" \
    --region $AWS_REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "")

echo "   VPC: $VPC_ID"
echo "   Subnets: $SUBNETS"
echo "   Security Group: $SG_ID"

# 3. Converter subnets para array JSON
SUBNET_1=$(echo $SUBNETS | awk '{print $1}')
SUBNET_2=$(echo $SUBNETS | awk '{print $2}')

if [ -z "$SUBNET_2" ]; then
    SUBNETS_JSON="[\"$SUBNET_1\"]"
else
    SUBNETS_JSON="[\"$SUBNET_1\",\"$SUBNET_2\"]"
fi

# 4. Criar Service
echo ""
echo "📋 Criando Service..."

aws ecs create-service \
    --cluster $ECS_CLUSTER \
    --service-name $ECS_SERVICE \
    --task-definition $TASK_DEFINITION \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=$SUBNETS_JSON,securityGroups=[\"$SG_ID\"],assignPublicIp=ENABLED}" \
    --region $AWS_REGION

if [ $? -eq 0 ]; then
    echo "✅ Service criado!"
else
    echo "⚠️ Service pode já existir"
fi

echo ""
echo "=========================================="
echo "✅ CONCLUÍDO!"
echo "=========================================="
echo ""
echo "📝 Próximos passos:"
echo "   1. Fazer commit e push no GitHub"
echo "   2. GitHub Actions vai fazer deploy automaticamente"
echo "   3. Testar a API"
