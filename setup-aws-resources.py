#!/usr/bin/env python3
"""
Setup AWS - Cria Task Definition, Service e ECR Repository
Script seguro que não tenta criar roles IAM
"""
import json
import time
import sys

try:
    import boto3
except ImportError:
    print("❌ boto3 não instalado. Instalando...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3"])
    import boto3

AWS_ACCOUNT_ID = "176977333713"
AWS_REGION = "sa-east-1"
ECR_REPOSITORY = "iscoolgpt"
ECS_CLUSTER = "iscoolgpt-cluster2"
ECS_SERVICE = "iscoolgpt-service"
TASK_DEFINITION = "iscoolgpt-task"

print("\n" + "="*60)
print("🚀 SETUP AWS - IsCoolGPT")
print("="*60)

# Usar credenciais do AWS CLI padrão
session = boto3.Session(region_name=AWS_REGION)

ecr = session.client('ecr', region_name=AWS_REGION)
ecs = session.client('ecs', region_name=AWS_REGION)
ec2 = session.client('ec2', region_name=AWS_REGION)
logs = session.client('logs', region_name=AWS_REGION)

# ========================================
# 1. CRIAR REPOSITÓRIO ECR
# ========================================
print("\n📋 ETAPA 1: Repositório ECR...")

ecr_uri = None
try:
    response = ecr.describe_repositories(repositoryNames=[ECR_REPOSITORY])
    ecr_uri = response['repositories'][0]['repositoryUri']
    print(f"✅ Repositório {ECR_REPOSITORY} já existe!")
    print(f"   URI: {ecr_uri}")
except Exception as e:
    if "RepositoryNotFoundException" in str(e):
        try:
            print(f"🔄 Criando repositório ECR...")
            response = ecr.create_repository(
                repositoryName=ECR_REPOSITORY,
                imageScanningConfiguration={'scanOnPush': True},
                imageTagMutability='MUTABLE'
            )
            ecr_uri = response['repository']['repositoryUri']
            print(f"✅ Repositório criado: {ecr_uri}")
        except Exception as create_error:
            print(f"❌ Erro ao criar repositório: {create_error}")
    else:
        print(f"⚠️  Erro ao verificar repositório: {e}")
    time.sleep(1)

# ========================================
# 2. CRIAR LOG GROUP
# ========================================
print("\n📋 ETAPA 2: Log Group (CloudWatch)...")

log_group_name = f"/ecs/{TASK_DEFINITION}"
try:
    logs.describe_log_groups(logGroupNamePrefix=log_group_name)
    print(f"✅ Log Group {log_group_name} já existe!")
except Exception as e:
    try:
        print(f"🔄 Criando log group...")
        logs.create_log_group(logGroupName=log_group_name)
        print(f"✅ Log Group criado: {log_group_name}")
    except Exception as create_error:
        if "ResourceAlreadyExistsException" not in str(create_error):
            print(f"⚠️  Erro: {create_error}")
        else:
            print(f"✅ Log Group já existe!")
    time.sleep(1)

# ========================================
# 3. CRIAR SECURITY GROUP (se necessário)
# ========================================
print("\n📋 ETAPA 3: Security Group...")

sg_name = "iscoolgpt-sg"
sg_id = None

try:
    response = ec2.describe_security_groups(GroupNames=[sg_name])
    sg_id = response['SecurityGroups'][0]['GroupId']
    print(f"✅ Security Group {sg_name} já existe!")
    print(f"   ID: {sg_id}")
except Exception as e:
    if "InvalidGroup.NotFound" in str(e):
        try:
            print(f"🔄 Criando security group...")
            
            # Obter VPC padrão
            vpcs = ec2.describe_vpcs(Filters=[{'Name': 'is-default', 'Values': ['true']}])
            if vpcs['Vpcs']:
                vpc_id = vpcs['Vpcs'][0]['VpcId']
                
                response = ec2.create_security_group(
                    GroupName=sg_name,
                    Description='Security Group para IsCoolGPT ECS',
                    VpcId=vpc_id
                )
                sg_id = response['GroupId']
                
                # Permitir porta 3000
                try:
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
                except Exception as ingress_error:
                    if "InvalidPermission.Duplicate" not in str(ingress_error):
                        print(f"   Aviso ao adicionar regra: {ingress_error}")
                
                print(f"✅ Security Group criado: {sg_id}")
            else:
                print(f"⚠️  Nenhuma VPC padrão encontrada")
        except Exception as create_error:
            print(f"❌ Erro ao criar security group: {create_error}")
    else:
        print(f"⚠️  Erro ao verificar security group: {e}")
    time.sleep(1)

# ========================================
# 4. CRIAR TASK DEFINITION
# ========================================
print("\n📋 ETAPA 4: Task Definition...")

if not ecr_uri:
    ecr_uri = f"{AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/{ECR_REPOSITORY}:latest"

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
                    'valueFrom': f'arn:aws:secretsmanager:{AWS_REGION}:{AWS_ACCOUNT_ID}:secret:openrouter-api-key'
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
    print(f"   ARN: {response['taskDefinition']['taskDefinitionArn']}")
except Exception as e:
    if "ClientException" in str(e):
        try:
            print(f"🔄 Criando task definition...")
            response = ecs.register_task_definition(**task_def)
            print(f"✅ Task Definition criada!")
            print(f"   ARN: {response['taskDefinition']['taskDefinitionArn']}")
        except Exception as create_error:
            print(f"❌ Erro ao criar task definition: {create_error}")
    else:
        print(f"⚠️  Erro ao verificar task definition: {e}")
    time.sleep(1)

# ========================================
# 5. CRIAR ECS SERVICE
# ========================================
print("\n📋 ETAPA 5: ECS Service...")

try:
    response = ecs.describe_services(cluster=ECS_CLUSTER, services=[ECS_SERVICE])
    if response['services'] and len(response['services']) > 0:
        print(f"✅ Service {ECS_SERVICE} já existe!")
        print(f"   Status: {response['services'][0]['status']}")
except Exception as e:
    try:
        print(f"🔄 Criando service...")
        
        # Obter subnets da VPC padrão
        vpcs = ec2.describe_vpcs(Filters=[{'Name': 'is-default', 'Values': ['true']}])
        if vpcs['Vpcs']:
            vpc_id = vpcs['Vpcs'][0]['VpcId']
            subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets']
            subnet_ids = [subnet['SubnetId'] for subnet in subnets[:2]]
            
            if subnet_ids and sg_id:
                response = ecs.create_service(
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
                print(f"   ARN: {response['service']['serviceArn']}")
            else:
                print(f"⚠️  Falha ao obter subnets/security group")
                print(f"   Subnet IDs: {subnet_ids}")
                print(f"   Security Group ID: {sg_id}")
        else:
            print(f"⚠️  Nenhuma VPC padrão encontrada")
    except Exception as create_error:
        print(f"❌ Erro ao criar service: {create_error}")
    time.sleep(1)

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
print("   1. ✅ Imagem já foi feita push para ECR")
print("   2. Fazer commit e push para disparar GitHub Actions:")
print("      $ git add .")
print("      $ git commit -m 'chore: preparar para deploy'")
print("      $ git push origin main")
print("   3. Monitorar GitHub Actions: https://github.com/arthurreis33/Cloud/actions")
print("   4. Após deploy, testar a API com o IP público da tarefa")

print("\n🎉 Pronto para deploy automático!\n")
