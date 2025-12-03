#!/usr/bin/env python3
"""
Script de Setup AWS para IsCoolGPT usando boto3
"""
import json
import time
import sys
from typing import Optional

try:
    import boto3
except ImportError:
    print("❌ boto3não instalado. Instalando...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3"])
    import boto3

# ========================================
# CONFIGURAR VARIÁVEIS
# ========================================

AWS_ACCOUNT_ID = "176977333713"  # ← COLOQUE SEU ACCOUNT ID
AWS_REGION = "sa-east-1"
ECR_REPOSITORY = "iscoolgpt"
ECS_CLUSTER = "iscoolgpt-cluster2"
ECS_SERVICE = "iscoolgpt-service"
TASK_DEFINITION = "iscoolgpt-task"
OPENROUTER_API_KEY = "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"  # ← COLOQUE SUA CHAVE

# Inicializar clientes AWS
iam = boto3.client('iam', region_name=AWS_REGION)
ecr = boto3.client('ecr', region_name=AWS_REGION)
ecs = boto3.client('ecs', region_name=AWS_REGION)
ec2 = boto3.client('ec2', region_name=AWS_REGION)
logs = boto3.client('logs', region_name=AWS_REGION)
secrets_manager = boto3.client('secretsmanager', region_name=AWS_REGION)

print("\n" + "="*50)
print("🚀 SETUP AWS - IsCoolGPT")
print("="*50)

# ========================================
# 1. CRIAR ROLE IAM
# ========================================
print("\n📋 ETAPA 1: Criando Role IAM (ecsTaskExecutionRole)...")

try:
    iam.get_role(RoleName='ecsTaskExecutionRole')
    print("✅ Role ecsTaskExecutionRole já existe!")
except iam.exceptions.NoSuchEntityException:
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
except ecr.exceptions.RepositoryNotFoundException:
    print("🔄 Criando repositório ECR...")
    
    response = ecr.create_repository(
        repositoryName=ECR_REPOSITORY,
        imageScanningConfiguration={'scanOnPush': True},
        imageTagMutability='MUTABLE'
    )
    
    ecr_uri = response['repository']['repositoryUri']
    print(f"✅ Repositório criado: {ecr_uri}")

# ========================================
# 3. CRIAR CLUSTER ECS
# ========================================
print("\n📋 ETAPA 3: Criando Cluster ECS...")

try:
    ecs.describe_clusters(clusters=[ECS_CLUSTER])
    print(f"✅ Cluster {ECS_CLUSTER} já existe!")
except:
    print("🔄 Criando cluster...")
    
    ecs.create_cluster(
        clusterName=ECS_CLUSTER,
        clusterSettings=[
            {
                'name': 'containerInsights',
                'value': 'disabled'
            }
        ]
    )
    
    print(f"✅ Cluster criado: {ECS_CLUSTER}")

# ========================================
# 4. CRIAR LOG GROUP
# ========================================
print("\n📋 ETAPA 4: Criando Log Group (CloudWatch)...")

log_group = "/ecs/iscoolgpt"
try:
    logs.describe_log_groups(logGroupNamePrefix=log_group)
    print("✅ Log group já existe!")
except:
    print("🔄 Criando log group...")
    
    logs.create_log_group(logGroupName=log_group)
    print(f"✅ Log group criado: {log_group}")

# ========================================
# 5. CRIAR SECRET
# ========================================
print("\n📋 ETAPA 5: Criando Secret no Secrets Manager...")

secret_name = "iscoolgpt/openrouter-key"
try:
    secrets_manager.describe_secret(SecretId=secret_name)
    print("✅ Secret já existe! Atualizando...")
    secrets_manager.update_secret(
        SecretId=secret_name,
        SecretString=json.dumps({"OPENROUTER_API_KEY": OPENROUTER_API_KEY})
    )
except secrets_manager.exceptions.ResourceNotFoundException:
    print("🔄 Criando secret...")
    
    secrets_manager.create_secret(
        Name=secret_name,
        Description="OpenRouter API Key para IsCoolGPT",
        SecretString=json.dumps({"OPENROUTER_API_KEY": OPENROUTER_API_KEY})
    )
    
    print("✅ Secret criado!")

# ========================================
# 6. CRIAR TASK DEFINITION
# ========================================
print("\n📋 ETAPA 6: Criando Task Definition...")

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
                {'name': 'APP_URL', 'value': 'http://localhost:3000'}
            ],
            'secrets': [
                {
                    'name': 'OPENROUTER_API_KEY',
                    'valueFrom': f'arn:aws:secretsmanager:{AWS_REGION}:{AWS_ACCOUNT_ID}:secret:iscoolgpt/openrouter-key'
                }
            ],
            'logConfiguration': {
                'logDriver': 'awslogs',
                'options': {
                    'awslogs-group': log_group,
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
    print(f"   Revisão: {response['taskDefinition']['revision']}")
except:
    print("🔄 Registrando task definition...")
    
    response = ecs.register_task_definition(**task_def)
    print(f"✅ Task Definition criada: {TASK_DEFINITION}:{response['taskDefinition']['revision']}")

# ========================================
# 7. OBTER VPC E SUBNETS
# ========================================
print("\n📋 ETAPA 7: Obtendo VPC e Subnets...")

vpcs = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
vpc_id = vpcs['Vpcs'][0]['VpcId']
print(f"✅ VPC: {vpc_id}")

subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
subnet_ids = [s['SubnetId'] for s in subnets['Subnets'][:2]]
print(f"✅ Subnets: {', '.join(subnet_ids)}")

# ========================================
# 8. CRIAR SECURITY GROUP
# ========================================
print("\n📋 ETAPA 8: Criando Security Group...")

sg_name = "iscoolgpt-sg"
sg_id = None

sgs = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [sg_name]}])
if sgs['SecurityGroups']:
    sg_id = sgs['SecurityGroups'][0]['GroupId']
    print(f"✅ Security Group já existe: {sg_id}")
else:
    print("🔄 Criando security group...")
    
    response = ec2.create_security_group(
        GroupName=sg_name,
        Description="Security Group para IsCoolGPT",
        VpcId=vpc_id
    )
    
    sg_id = response['GroupId']
    print(f"✅ Security Group criado: {sg_id}")

# Adicionar regra de entrada para porta 3000
print("🔄 Configurando regra de entrada (porta 3000)...")
try:
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 3000,
                'ToPort': 3000,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )
    print("✅ Regra de entrada adicionada!")
except Exception as e:
    if 'InvalidPermission.Duplicate' in str(e):
        print("✅ Regra de entrada já existe!")
    else:
        raise

# ========================================
# 9. CRIAR ECS SERVICE
# ========================================
print("\n📋 ETAPA 9: Criando ECS Service...")

try:
    response = ecs.describe_services(
        cluster=ECS_CLUSTER,
        services=[ECS_SERVICE]
    )
    if response['services']:
        print(f"✅ Service {ECS_SERVICE} já existe!")
except:
    pass

# Verificar se service existe
try:
    response = ecs.describe_services(
        cluster=ECS_CLUSTER,
        services=[ECS_SERVICE]
    )
    if response['services'] and response['services'][0]['status'] != 'INACTIVE':
        print(f"✅ Service {ECS_SERVICE} já existe e está ativo!")
    else:
        raise Exception("Service não existe")
except:
    print("🔄 Criando service...")
    
    response = ecs.create_service(
        cluster=ECS_CLUSTER,
        serviceName=ECS_SERVICE,
        taskDefinition=f'{TASK_DEFINITION}:1',
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
    
    print(f"✅ Service criado: {ECS_SERVICE}")
    time.sleep(3)

# ========================================
# 10. VERIFICAÇÃO FINAL
# ========================================
print("\n\n" + "="*50)
print("✅ VERIFICAÇÃO FINAL")
print("="*50)

print(f"\n✅ Resumo da Configuração:")
print(f"  - Account ID: {AWS_ACCOUNT_ID}")
print(f"  - Região: {AWS_REGION}")
print(f"  - ECR Repository: {ecr_uri}")
print(f"  - ECS Cluster: {ECS_CLUSTER}")
print(f"  - ECS Service: {ECS_SERVICE}")
print(f"  - Task Definition: {TASK_DEFINITION}")
print(f"  - Security Group: {sg_id}")
print(f"  - VPC: {vpc_id}")

# Verificar tasks em execução
print(f"\n🔄 Verificando tasks em execução...")
try:
    response = ecs.list_tasks(cluster=ECS_CLUSTER)
    if response['taskArns']:
        print("✅ Tarefa em execução!")
        
        # Obter IP público
        tasks = ecs.describe_tasks(
            cluster=ECS_CLUSTER,
            tasks=response['taskArns']
        )
        
        if tasks['tasks']:
            task = tasks['tasks'][0]
            if 'attachments' in task and task['attachments']:
                for attachment in task['attachments']:
                    if attachment['type'] == 'ElasticNetworkInterface':
                        for detail in attachment['details']:
                            if detail['name'] == 'networkInterfaceId':
                                eni_id = detail['value']
                                
                                # Obter IP público do ENI
                                enis = ec2.describe_network_interfaces(NetworkInterfaceIds=[eni_id])
                                if enis['NetworkInterfaces'] and 'Association' in enis['NetworkInterfaces'][0]:
                                    public_ip = enis['NetworkInterfaces'][0]['Association'].get('PublicIp')
                                    if public_ip:
                                        print(f"  - IP Público: {public_ip}")
                                        print(f"\n🌐 Acesse a API em: http://{public_ip}:3000")
    else:
        print("⏳ Nenhuma tarefa em execução ainda. Aguarde ~2 minutos.")
except Exception as e:
    print(f"⏳ Tasks ainda não disponíveis: {str(e)}")

print("\n✅ SETUP AWS CONCLUÍDO!")
print("\n📝 Próximos Passos:")
print("  1. Adicione os GitHub Secrets (veja instruções abaixo)")
print("  2. Construa a imagem Docker: docker build -t iscoolgpt .")
print("  3. Faça push para ECR (use: aws ecr get-login-password | docker login...)")
print("  4. Faça push do código para 'main' e GitHub Actions fará o deploy")

print("\n📝 GitHub Secrets a Adicionar (Settings → Secrets and variables → Actions):")
print(f"  AWS_ACCESS_KEY_ID = (sua chave IAM)")
print(f"  AWS_SECRET_ACCESS_KEY = (sua chave IAM secreta)")
print(f"  OPENROUTER_API_KEY = {OPENROUTER_API_KEY}")

print("\n" + "="*50)
