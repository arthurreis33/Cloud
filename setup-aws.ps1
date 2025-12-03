# ========================================
# Script de Setup AWS para IsCoolGPT
# ========================================
# Executar: .\setup-aws.ps1
# IMPORTANTE: Configure as variáveis abaixo antes de rodar!

# ========================================
# 1. CONFIGURAR VARIÁVEIS
# ========================================

# Altere essas variáveis conforme sua conta AWS:
$AWS_ACCOUNT_ID = "176977333713"  # Ex: 123456789012 (encontre em IAM → Dashboard)
$AWS_REGION = "sa-east-1"                 # São Paulo
$ECR_REPOSITORY = "iscoolgpt"
$ECS_CLUSTER = "iscoolgpt-cluster2"
$ECS_SERVICE = "iscoolgpt-service"
$TASK_DEFINITION = "iscoolgpt-task"
$OPENROUTER_API_KEY = "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"  # Cole sua chave aqui

# ========================================
# 2. CRIAR ROLE IAM (ecsTaskExecutionRole)
# ========================================
Write-Host "`n📋 ETAPA 1: Criando Role IAM (ecsTaskExecutionRole)..." -ForegroundColor Cyan

# Verificar se role já existe
$role_exists = aws iam get-role --role-name ecsTaskExecutionRole 2>$null
if ($role_exists) {
    Write-Host "✅ Role ecsTaskExecutionRole já existe!" -ForegroundColor Green
} else {
    Write-Host "🔄 Criando role..." -ForegroundColor Yellow
    
    # Criar arquivo temporário com a política de confiança
    $trust_policy = @{
        Version = "2012-10-17"
        Statement = @(
            @{
                Effect = "Allow"
                Principal = @{
                    Service = "ecs-tasks.amazonaws.com"
                }
                Action = "sts:AssumeRole"
            }
        )
    } | ConvertTo-Json

    # Salvar em arquivo temporário
    $trust_policy | Out-File -FilePath "$env:TEMP\trust-policy.json" -Encoding UTF8

    # Criar role
    aws iam create-role `
        --role-name ecsTaskExecutionRole `
        --assume-role-policy-document file://$env:TEMP\trust-policy.json

    Write-Host "⏳ Anexando policy AmazonECSTaskExecutionRolePolicy..." -ForegroundColor Yellow
    
    # Anexar política
    aws iam attach-role-policy `
        --role-name ecsTaskExecutionRole `
        --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

    Write-Host "✅ Role criada com sucesso!" -ForegroundColor Green
    Start-Sleep -Seconds 2
}

# ========================================
# 3. CRIAR REPOSITÓRIO ECR
# ========================================
Write-Host "`n📋 ETAPA 2: Criando Repositório ECR..." -ForegroundColor Cyan

$repo_exists = aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>$null
if ($repo_exists) {
    Write-Host "✅ Repositório $ECR_REPOSITORY já existe!" -ForegroundColor Green
    $ecr_uri = aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION --query 'repositories[0].repositoryUri' --output text
} else {
    Write-Host "🔄 Criando repositório ECR..." -ForegroundColor Yellow
    
    aws ecr create-repository `
        --repository-name $ECR_REPOSITORY `
        --region $AWS_REGION `
        --image-tag-mutability MUTABLE `
        --image-scanning-configuration scanOnPush=true

    $ecr_uri = aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION --query 'repositories[0].repositoryUri' --output text
    Write-Host "✅ Repositório criado: $ecr_uri" -ForegroundColor Green
}

# ========================================
# 4. CRIAR CLUSTER ECS
# ========================================
Write-Host "`n📋 ETAPA 3: Criando Cluster ECS..." -ForegroundColor Cyan

$cluster_exists = aws ecs describe-clusters --clusters $ECS_CLUSTER --region $AWS_REGION --query 'clusters[0].clusterName' --output text 2>$null
if ($cluster_exists -eq $ECS_CLUSTER) {
    Write-Host "✅ Cluster $ECS_CLUSTER já existe!" -ForegroundColor Green
} else {
    Write-Host "🔄 Criando cluster..." -ForegroundColor Yellow
    
    aws ecs create-cluster `
        --cluster-name $ECS_CLUSTER `
        --region $AWS_REGION
    
    Write-Host "✅ Cluster criado: $ECS_CLUSTER" -ForegroundColor Green
}

# ========================================
# 5. CRIAR TASK DEFINITION
# ========================================
Write-Host "`n📋 ETAPA 4: Criando Task Definition..." -ForegroundColor Cyan

# Criar arquivo de task definition JSON
$task_def_json = @{
    family = $TASK_DEFINITION
    networkMode = "awsvpc"
    requiresCompatibilities = @("FARGATE")
    cpu = "256"
    memory = "512"
    executionRoleArn = "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole"
    containerDefinitions = @(
        @{
            name = "iscoolgpt-app"
            image = "${ecr_uri}:latest"
            portMappings = @(
                @{
                    containerPort = 3000
                    hostPort = 3000
                    protocol = "tcp"
                }
            )
            environment = @(
                @{
                    name = "PORT"
                    value = "3000"
                }
                @{
                    name = "APP_URL"
                    value = "http://localhost:3000"
                }
            )
            secrets = @(
                @{
                    name = "OPENROUTER_API_KEY"
                    valueFrom = "arn:aws:secretsmanager:${AWS_REGION}:${AWS_ACCOUNT_ID}:secret:iscoolgpt/openrouter-key"
                }
            )
            logConfiguration = @{
                logDriver = "awslogs"
                options = @{
                    "awslogs-group" = "/ecs/iscoolgpt"
                    "awslogs-region" = $AWS_REGION
                    "awslogs-stream-prefix" = "ecs"
                }
            }
        }
    )
} | ConvertTo-Json -Depth 10

# Salvar em arquivo
$task_def_json | Out-File -FilePath "$env:TEMP\task-definition.json" -Encoding UTF8

Write-Host "🔄 Registrando task definition..." -ForegroundColor Yellow

# Registrar task definition
aws ecs register-task-definition `
    --cli-input-json file://$env:TEMP\task-definition.json `
    --region $AWS_REGION

Write-Host "✅ Task Definition criada: $TASK_DEFINITION" -ForegroundColor Green

# ========================================
# 6. OBTER IDs DE SUBNETS E SECURITY GROUP
# ========================================
Write-Host "`n📋 ETAPA 5: Obtendo IDs de Subnet e Security Group..." -ForegroundColor Cyan

# Obter VPC padrão
$vpc_id = aws ec2 describe-vpcs --filters Name=is-default,Values=true --query 'Vpcs[0].VpcId' --output text --region $AWS_REGION

# Obter subnets
$subnets = aws ec2 describe-subnets --filters Name=vpc-id,Values=$vpc_id --query 'Subnets[0:2].SubnetId' --output text --region $AWS_REGION
$subnet_array = $subnets -split '\s+' | Where-Object { $_ -ne '' }

Write-Host "VPC: $vpc_id" -ForegroundColor Green
Write-Host "Subnets: $($subnet_array -join ', ')" -ForegroundColor Green

# Criar ou atualizar Security Group
$sg_name = "iscoolgpt-sg"
$sg_exists = aws ec2 describe-security-groups --filters Name=group-name,Values=$sg_name --region $AWS_REGION --query 'SecurityGroups[0].GroupId' --output text 2>$null

if ($sg_exists -and $sg_exists -ne "None") {
    Write-Host "✅ Security Group $sg_name já existe: $sg_exists" -ForegroundColor Green
    $sg_id = $sg_exists
} else {
    Write-Host "🔄 Criando Security Group..." -ForegroundColor Yellow
    
    $sg_id = aws ec2 create-security-group `
        --group-name $sg_name `
        --description "Security Group para IsCoolGPT" `
        --vpc-id $vpc_id `
        --region $AWS_REGION `
        --query 'GroupId' `
        --output text
    
    Write-Host "✅ Security Group criado: $sg_id" -ForegroundColor Green
}

# Adicionar regra de entrada para porta 3000
Write-Host "🔄 Configurando regra de entrada (porta 3000)..." -ForegroundColor Yellow

$rule_exists = aws ec2 describe-security-groups --group-ids $sg_id --region $AWS_REGION --query "SecurityGroups[0].IpPermissions[?FromPort==\`3000\`]" --output text 2>$null

if (-not $rule_exists) {
    aws ec2 authorize-security-group-ingress `
        --group-id $sg_id `
        --protocol tcp `
        --port 3000 `
        --cidr 0.0.0.0/0 `
        --region $AWS_REGION
    
    Write-Host "✅ Regra de entrada adicionada!" -ForegroundColor Green
} else {
    Write-Host "✅ Regra de entrada já existe!" -ForegroundColor Green
}

# ========================================
# 7. CRIAR ECS SERVICE
# ========================================
Write-Host "`n📋 ETAPA 6: Criando ECS Service..." -ForegroundColor Cyan

$service_exists = aws ecs describe-services --cluster $ECS_CLUSTER --services $ECS_SERVICE --region $AWS_REGION --query 'services[0].serviceName' --output text 2>$null

if ($service_exists -eq $ECS_SERVICE) {
    Write-Host "✅ Service $ECS_SERVICE já existe!" -ForegroundColor Green
} else {
    Write-Host "🔄 Criando service..." -ForegroundColor Yellow
    
    # Converter subnets para formato AWS CLI
    $subnet_str = ($subnet_array -join '","') 
    $subnet_str = "`"$subnet_str`""
    
    # Criar arquivo de configuração de rede
    $network_config = @{
        awsvpcConfiguration = @{
            subnets = $subnet_array
            securityGroups = @($sg_id)
            assignPublicIp = "ENABLED"
        }
    } | ConvertTo-Json -Depth 10
    
    $network_config | Out-File -FilePath "$env:TEMP\network-config.json" -Encoding UTF8
    
    aws ecs create-service `
        --cluster $ECS_CLUSTER `
        --service-name $ECS_SERVICE `
        --task-definition "${TASK_DEFINITION}:1" `
        --desired-count 1 `
        --launch-type FARGATE `
        --network-configuration file://$env:TEMP/network-config.json `
        --region $AWS_REGION

    Write-Host "✅ Service criado: $ECS_SERVICE" -ForegroundColor Green
    Start-Sleep -Seconds 3
}

# ========================================
# 8. CRIAR LOG GROUP (CloudWatch)
# ========================================
Write-Host "`n📋 ETAPA 7: Criando Log Group (CloudWatch)..." -ForegroundColor Cyan

$log_group = "/ecs/iscoolgpt"
$log_exists = aws logs describe-log-groups --log-group-name-prefix $log_group --region $AWS_REGION --query "logGroups[0].logGroupName" --output text 2>$null

if ($log_exists -eq $log_group) {
    Write-Host "✅ Log group já existe!" -ForegroundColor Green
} else {
    Write-Host "🔄 Criando log group..." -ForegroundColor Yellow
    
    aws logs create-log-group `
        --log-group-name $log_group `
        --region $AWS_REGION
    
    Write-Host "✅ Log group criado: $log_group" -ForegroundColor Green
}

# ========================================
# 9. CRIAR SECRET NO SECRETS MANAGER
# ========================================
Write-Host "`n📋 ETAPA 8: Criando Secret no Secrets Manager..." -ForegroundColor Cyan

$secret_name = "iscoolgpt/openrouter-key"
$secret_json = @{
    OPENROUTER_API_KEY = $OPENROUTER_API_KEY
} | ConvertTo-Json

$secret_exists = aws secretsmanager describe-secret --secret-id $secret_name --region $AWS_REGION --query 'Name' --output text 2>$null

if ($secret_exists -eq $secret_name) {
    Write-Host "✅ Secret já existe! Atualizando..." -ForegroundColor Green
    aws secretsmanager update-secret `
        --secret-id $secret_name `
        --secret-string $secret_json `
        --region $AWS_REGION
} else {
    Write-Host "🔄 Criando secret..." -ForegroundColor Yellow
    
    aws secretsmanager create-secret `
        --name $secret_name `
        --description "OpenRouter API Key para IsCoolGPT" `
        --secret-string $secret_json `
        --region $AWS_REGION
    
    Write-Host "✅ Secret criado!" -ForegroundColor Green
}

# ========================================
# 10. VERIFICAÇÃO FINAL
# ========================================
Write-Host "`n`n📋 ========== VERIFICAÇÃO FINAL ==========" -ForegroundColor Cyan

Write-Host "`n✅ Resumo da Configuração:" -ForegroundColor Green
Write-Host "  - Account ID: $AWS_ACCOUNT_ID"
Write-Host "  - Região: $AWS_REGION"
Write-Host "  - ECR Repository: $ecr_uri"
Write-Host "  - ECS Cluster: $ECS_CLUSTER"
Write-Host "  - ECS Service: $ECS_SERVICE"
Write-Host "  - Task Definition: $TASK_DEFINITION"
Write-Host "  - Security Group: $sg_id"
Write-Host "  - VPC: $vpc_id"

# Verificar task
Write-Host "`n🔄 Verificando task em execução..." -ForegroundColor Yellow
$tasks = aws ecs list-tasks --cluster $ECS_CLUSTER --region $AWS_REGION --query 'taskArns' --output text

if ($tasks) {
    Write-Host "✅ Tarefa em execução!" -ForegroundColor Green
    
    # Obter detalhes da task
    $task_details = aws ecs describe-tasks --cluster $ECS_CLUSTER --tasks $tasks --region $AWS_REGION --query 'tasks[0]' --output json | ConvertFrom-Json
    
    if ($task_details.attachments) {
        $eni_id = $task_details.attachments[0].details | Where-Object { $_.name -eq "networkInterfaceId" } | Select-Object -ExpandProperty value
        
        if ($eni_id) {
            $public_ip = aws ec2 describe-network-interfaces --network-interface-ids $eni_id --region $AWS_REGION --query 'NetworkInterfaces[0].Association.PublicIp' --output text
            Write-Host "  - IP Público: $public_ip" -ForegroundColor Green
            Write-Host "`n🌐 Acesse a API em: http://${public_ip}:3000" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "⏳ Nenhuma tarefa em execução ainda. Aguarde ~2 minutos." -ForegroundColor Yellow
}

Write-Host "`n✅ SETUP AWS CONCLUÍDO!" -ForegroundColor Green
Write-Host "`n📝 Próximos Passos:" -ForegroundColor Cyan
Write-Host "  1. Adicione os GitHub Secrets (veja instruções abaixo)"
Write-Host "  2. Faça push do código para 'main'"
Write-Host "  3. GitHub Actions fará o deploy automaticamente"

Write-Host "`n📝 GitHub Secrets a Adicionar:" -ForegroundColor Cyan
Write-Host "  Vá em: Settings → Secrets and variables → Actions"
Write-Host "  Adicione:" -ForegroundColor Yellow
Write-Host "    AWS_ACCESS_KEY_ID = (sua chave IAM)"
Write-Host "    AWS_SECRET_ACCESS_KEY = (sua chave IAM secreta)"
Write-Host "    OPENROUTER_API_KEY = $OPENROUTER_API_KEY"
