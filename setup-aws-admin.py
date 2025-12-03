#!/usr/bin/env python3
"""
Script de Setup AWS para IsCoolGPT - Versão Admin
Use com credenciais de ADMINISTRADOR
"""
import json
import time
import sys
import os
from typing import Optional

try:
    import boto3
except ImportError:
    print("❌ boto3 não instalado. Instalando...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3"])
    import boto3

# ========================================
# CONFIGURAR VARIÁVEIS
# ========================================

AWS_ACCOUNT_ID = "176977333713"  # ← COLOQUE SEU ACCOUNT ID
AWS_REGION = "sa-east-1"
ECR_REPOSITORY = "iscoolgpt"
ECS_CLUSTER = "iscoolgpt-cluster"
ECS_SERVICE = "iscoolgpt-service"
TASK_DEFINITION = "iscoolgpt-task"

print("\n" + "="*60)
print("🚀 SETUP AWS - IsCoolGPT (VERSÃO ADMIN)")
print("="*60)

print("\n⚠️  Este script precisa de credenciais de ADMINISTRADOR!")
print("Opções:")
print("1. Usar credenciais do console AWS")
print("2. Usar credenciais salvas no ~/.aws/credentials")
print("\nDigite as credenciais de ADMINISTRADOR (não github-actions-deploy):")

access_key = input("\n🔑 AWS Access Key ID (deixe em branco para usar configuração padrão): ").strip()
secret_key = input("🔑 AWS Secret Access Key: ").strip()

# Criar cliente com credenciais específicas ou usar padrão
if access_key and secret_key:
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=AWS_REGION
    )
else:
    print("✅ Usando credenciais padrão do ~/.aws/credentials")
    session = boto3.Session(region_name=AWS_REGION)

iam = session.client('iam')
ecr = session.client('ecr', region_name=AWS_REGION)
ecs = session.client('ecs', region_name=AWS_REGION)
ec2 = session.client('ec2', region_name=AWS_REGION)
logs = session.client('logs', region_name=AWS_REGION)
secrets_manager = session.client('secretsmanager', region_name=AWS_REGION)

# ========================================
# 1. CRIAR ROLE IAM
# ========================================
print("\n📋 ETAPA 1: Criando Role IAM (ecsTaskExecutionRole)...")

try:
    iam.get_role(RoleName='ecsTaskExecutionRole')
    print("✅ Role ecsTaskExecutionRole já existe!")
except Exception as e:
    print("🔄 Criando role...")
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ecs-tasks.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    iam.create_role(
        RoleName='ecsTaskExecutionRole',
        AssumeRolePolicyDocument=json.dumps(trust_policy)
    )
    
    iam.attach_role_policy(
        RoleName='ecsTaskExecutionRole',
        PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy'
    )
    
    print("✅ Role criada com sucesso!")
    time.sleep(2)

# ========================================
# 2. CRIAR REPOSITÓRIO ECR
# ========================================
print("\n📋 ETAPA 2: Criando Repositório ECR...")

ecr_uri = None
try:
    response = ecr.describe_repositories(repositoryNames=[ECR_REPOSITORY])
    ecr_uri = response['repositories'][0]['repositoryUri']
    print(f"✅ Repositório {ECR_REPOSITORY} já existe!")
    print(f"   URI: {ecr_uri}")
except Exception as e:
    print("🔄 Criando repositório ECR...")
    
    response = ecr.create_repository(
        repositoryName=ECR_REPOSITORY,
        imageScanningConfiguration={'scanOnPush': True},
        imageTagMutability='MUTABLE'
    )
    
    ecr_uri = response['repository']['repositoryUri']
    print(f"✅ Repositório criado: {ecr_uri}")
    time.sleep(1)

# ========================================
# 3. CRIAR ECS CLUSTER
# ========================================
print("\n📋 ETAPA 3: Criando ECS Cluster...")

try:
    ecs.describe_clusters(clusters=[ECS_CLUSTER])
    print(f"✅ Cluster {ECS_CLUSTER} já existe!")
except Exception as e:
    print("🔄 Criando cluster...")
    ecs.create_cluster(clusterName=ECS_CLUSTER)
    print(f"✅ Cluster {ECS_CLUSTER} criado!")
    time.sleep(1)

# ========================================
# 4. CRIAR LOG GROUP
# ========================================
print("\n📋 ETAPA 4: Criando Log Group (CloudWatch)...")

log_group_name = f"/ecs/{TASK_DEFINITION}"
try:
    logs.describe_log_groups(logGroupNamePrefix=log_group_name)
    print(f"✅ Log Group {log_group_name} já existe!")
except Exception as e:
    print("🔄 Criando log group...")
    logs.create_log_group(logGroupName=log_group_name)
    print(f"✅ Log Group criado: {log_group_name}")
    time.sleep(1)

# ========================================
# 5. GUARDAR OPENROUTER API KEY NO SECRETS MANAGER
# ========================================
print("\n📋 ETAPA 5: Guardando OpenRouter API Key...")

openrouter_key = os.getenv('OPENROUTER_API_KEY', '')
if not openrouter_key:
    openrouter_key = input("🔑 Digite sua chave OpenRouter API (sk-or-v1-...): ").strip()

try:
    secrets_manager.describe_secret(SecretId='openrouter-api-key')
    print("✅ Secret openrouter-api-key já existe!")
except Exception as e:
    print("🔄 Criando secret...")
    secrets_manager.create_secret(
        Name='openrouter-api-key',
        SecretString=openrouter_key
    )
    print("✅ Secret criado!")
    time.sleep(1)

# ========================================
# 6. CRIAR SECURITY GROUP
# ========================================
print("\n📋 ETAPA 6: Criando Security Group...")

sg_name = "iscoolgpt-sg"
sg_id = None

try:
    response = ec2.describe_security_groups(GroupNames=[sg_name])
    sg_id = response['SecurityGroups'][0]['GroupId']
    print(f"✅ Security Group {sg_name} já existe!")
except Exception as e:
    print("🔄 Criando security group...")
    
    # Obter VPC padrão
    vpcs = ec2.describe_vpcs(Filters=[{'Name': 'is-default', 'Values': ['true']}])
    vpc_id = vpcs['Vpcs'][0]['VpcId'] if vpcs['Vpcs'] else None
    
    if vpc_id:
        response = ec2.create_security_group(
            GroupName=sg_name,
            Description='Security Group para IsCoolGPT ECS',
            VpcId=vpc_id
        )
        sg_id = response['GroupId']
        
        # Permitir porta 3000 de qualquer lugar
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 3000,
                    'ToPort': 3000,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTP 3000'}]
                }
            ]
        )
        
        print(f"✅ Security Group criado: {sg_id}")
    else:
        print("⚠️  Não encontrada VPC padrão")
    
    time.sleep(1)

# ========================================
# 7. CRIAR TASK DEFINITION
# ========================================
print("\n📋 ETAPA 7: Criando Task Definition...")

task_def = {
    'family': TASK_DEFINITION,
    'networkMode': 'awsvpc',
    'requiresCompatibilities': ['FARGATE'],
    'cpu': '256',
    'memory': '512',
    'executionRoleArn': f'arn:aws:iam::{AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole',
    'containerDefinitions': [
        {
            'name': 'iscoolgpt-app',
            'image': f'{ecr_uri}:latest',
            'portMappings': [
                {
                    'containerPort': 3000,
                    'hostPort': 3000,
                    'protocol': 'tcp'
                }
            ],
            'environment': [
                {'name': 'PORT', 'value': '3000'},
                {'name': 'PYTHONUNBUFFERED', 'value': '1'},
                {'name': 'LLM_PROVIDER', 'value': 'openrouter'}
            ],
            'secrets': [
                {
                    'name': 'OPENROUTER_API_KEY',
                    'valueFrom': f'arn:aws:secretsmanager:{AWS_REGION}:{AWS_ACCOUNT_ID}:secret:openrouter-api-key:key::'
                }
            ],
            'logConfiguration': {
                'logDriver': 'awslogs',
                'options': {
                    'awslogs-group': log_group_name,
                    'awslogs-region': AWS_REGION,
                    'awslogs-stream-prefix': 'ecs'
                }
            }
        }
    ]
}

try:
    response = ecs.describe_task_definition(taskDefinition=TASK_DEFINITION)
    print(f"✅ Task Definition {TASK_DEFINITION} já existe!")
except Exception as e:
    print("🔄 Criando task definition...")
    ecs.register_task_definition(**task_def)
    print(f"✅ Task Definition criada!")
    time.sleep(1)

# ========================================
# 8. CRIAR ECS SERVICE
# ========================================
print("\n📋 ETAPA 8: Criando ECS Service...")

try:
    ecs.describe_services(cluster=ECS_CLUSTER, services=[ECS_SERVICE])
    print(f"✅ Service {ECS_SERVICE} já existe!")
except Exception as e:
    print("🔄 Criando service...")
    
    # Obter subnets
    subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [sg_id.split('-')[0]]}])['Subnets']
    subnet_ids = [subnet['SubnetId'] for subnet in subnets[:2]]
    
    if subnet_ids and sg_id:
        ecs.create_service(
            cluster=ECS_CLUSTER,
            serviceName=ECS_SERVICE,
            taskDefinition=TASK_DEFINITION,
            desiredCount=1,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': subnet_ids,
                    'securityGroups': [sg_id],
                    'assignPublicIp': 'ENABLED'
                }
            }
        )
        print(f"✅ Service {ECS_SERVICE} criado!")
    else:
        print("⚠️  Falha ao obter subnets/security group")
    
    time.sleep(2)

# ========================================
# RESUMO
# ========================================
print("\n" + "="*60)
print("✅ SETUP CONCLUÍDO!")
print("="*60)

print(f"\n📋 Resumo da Configuração:")
print(f"   Region: {AWS_REGION}")
print(f"   Account ID: {AWS_ACCOUNT_ID}")
print(f"   ECR Repository: {ECR_REPOSITORY}")
print(f"   ECR URI: {ecr_uri}")
print(f"   ECS Cluster: {ECS_CLUSTER}")
print(f"   ECS Service: {ECS_SERVICE}")
print(f"   Task Definition: {TASK_DEFINITION}")
print(f"   Log Group: {log_group_name}")

print("\n📝 Próximos Passos:")
print("   1. ✅ Build e push da imagem Docker para ECR:")
print("      $ docker build -t iscoolgpt .")
print("      $ aws ecr get-login-password --region sa-east-1 | docker login --username AWS --password-stdin 176977333713.dkr.ecr.sa-east-1.amazonaws.com")
print(f"      $ docker tag iscoolgpt:latest {ecr_uri}:latest")
print(f"      $ docker push {ecr_uri}:latest")
print("\n   2. ✅ GitHub Actions fará deploy automaticamente")
print(f"\n   3. ✅ Verificar URL da API (será mostrada nos logs do GitHub Actions)")

print("\n🎉 Pronto para usar!\n")
