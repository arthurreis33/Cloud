#!/bin/bash
# Script para criar recursos AWS via CloudShell
# Execute este script no AWS CloudShell para setup completo

set -e

AWS_REGION="sa-east-1"
AWS_ACCOUNT_ID="176977333713"
ECR_REPOSITORY="iscoolgpt"
ECS_CLUSTER="iscoolgpt-cluster2"
ECS_SERVICE="iscoolgpt-service"
TASK_DEFINITION="iscoolgpt-task"

echo "=========================================="
echo "🚀 SETUP AWS - IsCoolGPT"
echo "=========================================="

# ========================================
# 1. CRIAR REPOSITÓRIO ECR
# ========================================
echo ""
echo "📋 ETAPA 1: Criando Repositório ECR..."

if aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>/dev/null; then
    echo "✅ Repositório $ECR_REPOSITORY já existe!"
else
    echo "🔄 Criando repositório..."
    aws ecr create-repository \
        --repository-name $ECR_REPOSITORY \
        --image-scanning-configuration scanOnPush=true \
        --image-tag-mutability MUTABLE \
        --region $AWS_REGION
    echo "✅ Repositório criado!"
fi

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY"
echo "   URI: $ECR_URI"

# ========================================
# 2. CRIAR LOG GROUP
# ========================================
echo ""
echo "📋 ETAPA 2: Criando Log Group..."

LOG_GROUP="/ecs/$TASK_DEFINITION"

if aws logs describe-log-groups --log-group-name-prefix "$LOG_GROUP" --region $AWS_REGION 2>/dev/null | grep -q "$LOG_GROUP"; then
    echo "✅ Log Group $LOG_GROUP já existe!"
else
    echo "🔄 Criando log group..."
    aws logs create-log-group \
        --log-group-name "$LOG_GROUP" \
        --region $AWS_REGION
    echo "✅ Log Group criado!"
fi

# ========================================
# 3. OBTER VPC PADRÃO
# ========================================
echo ""
echo "📋 ETAPA 3: Obtendo VPC padrão..."

VPC_ID=$(aws ec2 describe-vpcs \
    --filters "Name=is-default,Values=true" \
    --region $AWS_REGION \
    --query 'Vpcs[0].VpcId' \
    --output text)

echo "✅ VPC: $VPC_ID"

# ========================================
# 4. CRIAR SECURITY GROUP
# ========================================
echo ""
echo "📋 ETAPA 4: Criando Security Group..."

SG_NAME="iscoolgpt-sg"

SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$VPC_ID" \
    --region $AWS_REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "")

if [ "$SG_ID" != "" ] && [ "$SG_ID" != "None" ]; then
    echo "✅ Security Group $SG_NAME já existe!"
    echo "   ID: $SG_ID"
else
    echo "🔄 Criando security group..."
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SG_NAME \
        --description "Security Group para IsCoolGPT ECS" \
        --vpc-id $VPC_ID \
        --region $AWS_REGION \
        --query 'GroupId' \
        --output text)
    
    # Adicionar regra para porta 3000
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 3000 \
        --cidr 0.0.0.0/0 \
        --region $AWS_REGION 2>/dev/null || true
    
    echo "✅ Security Group criado!"
    echo "   ID: $SG_ID"
fi

# ========================================
# 5. OBTER SUBNETS
# ========================================
echo ""
echo "📋 ETAPA 5: Obtendo Subnets..."

SUBNETS=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --region $AWS_REGION \
    --query 'Subnets[0:2].SubnetId' \
    --output text)

echo "✅ Subnets: $SUBNETS"

# ========================================
# 6. CRIAR TASK DEFINITION
# ========================================
echo ""
echo "📋 ETAPA 6: Criando Task Definition..."

# Verificar se já existe
EXISTING_TASK=$(aws ecs describe-task-definition \
    --task-definition $TASK_DEFINITION \
    --region $AWS_REGION \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text 2>/dev/null || echo "")

if [ ! -z "$EXISTING_TASK" ] && [ "$EXISTING_TASK" != "None" ]; then
    echo "✅ Task Definition $TASK_DEFINITION já existe!"
else
    echo "🔄 Criando task definition..."
    
    # Criar arquivo JSON temporário
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
        --region $AWS_REGION > /dev/null
    
    rm /tmp/task_def.json
    echo "✅ Task Definition criada!"
fi

# ========================================
# 7. CRIAR ECS SERVICE
# ========================================
echo ""
echo "📋 ETAPA 7: Criando ECS Service..."

# Verificar se já existe
EXISTING_SERVICE=$(aws ecs describe-services \
    --cluster $ECS_CLUSTER \
    --services $ECS_SERVICE \
    --region $AWS_REGION \
    --query 'services[0].serviceArn' \
    --output text 2>/dev/null || echo "")

if [ ! -z "$EXISTING_SERVICE" ] && [ "$EXISTING_SERVICE" != "None" ]; then
    echo "✅ Service $ECS_SERVICE já existe!"
else
    echo "🔄 Criando service..."
    
    SUBNETS_JSON=$(echo $SUBNETS | jq -R 'split(" ") | map(select(length > 0))')
    
    aws ecs create-service \
        --cluster $ECS_CLUSTER \
        --service-name $ECS_SERVICE \
        --task-definition $TASK_DEFINITION \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$(echo $SUBNETS | sed 's/ /,/g' | sed 's/^/"/g' | sed 's/$/"/g' | sed 's/","/\",\"/g')],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
        --region $AWS_REGION > /dev/null
    
    echo "✅ Service criado!"
fi

# ========================================
# RESUMO
# ========================================
echo ""
echo "=========================================="
echo "✅ SETUP CONCLUÍDO!"
echo "=========================================="

echo ""
echo "📋 Resumo da Configuração:"
echo "   Region: $AWS_REGION"
echo "   Account ID: $AWS_ACCOUNT_ID"
echo "   ECR Repository: $ECR_REPOSITORY"
echo "   ECR URI: $ECR_URI"
echo "   ECS Cluster: $ECS_CLUSTER"
echo "   ECS Service: $ECS_SERVICE"
echo "   Task Definition: $TASK_DEFINITION"
echo "   Log Group: $LOG_GROUP"

echo ""
echo "📝 Próximos Passos:"
echo "   1. Verificar se a imagem Docker está no ECR"
echo "   2. Fazer commit e push para disparar GitHub Actions"
echo "   3. Monitorar GitHub Actions"
echo "   4. Testar a API"

echo ""
echo "🎉 Deploy automático pronto!\n"
