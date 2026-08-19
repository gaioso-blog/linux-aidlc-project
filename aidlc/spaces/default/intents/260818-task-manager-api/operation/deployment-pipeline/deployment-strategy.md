# Deployment Strategy — Task Manager API
<!-- confirmed -->

## Upstream Artifacts

- `construction/ci-pipeline/ci-config.md` — GitHub Actions CI configurado
- `construction/ci-pipeline/quality-gates.md` — gates: ruff + black + pytest ≥85%

## Estratégia

**Deploy direto (in-place)** via Terraform. Escolha adequada para:
- API serverless interna sem SLA externo
- ≤30 usuários — interrupção de segundos aceitável
- Equipe auto-organizada sem aprovação externa

## Ambientes

| Ambiente | Branch | Trigger | Aprovação |
|----------|--------|---------|-----------|
| `dev` | `main` | Automático após CI verde | Sem aprovação manual |
| (não há staging separado na v1) | — | — | — |

## Pipeline de Deploy (GitHub Actions + Terraform)

```
CI Job (ci.yml)
  ├── ruff + black + pytest ≥85%  [gate — bloqueia se falhar]
  └── coverage.xml upload

Deploy Job (deploy.yml — a criar)
  ├── Trigger: push para main (após CI verde)
  ├── Step 1: terraform init -backend-config=...
  ├── Step 2: terraform plan -out=tfplan
  ├── Step 3: terraform apply tfplan  [aplica infra + empacota Lambda]
  ├── Step 4: aws s3 sync frontend/ s3://BUCKET_NAME/
  ├── Step 5: aws cloudfront create-invalidation --distribution-id $CF_ID
  └── Step 6: smoke test (curl /v1/tasks → 200 ou 401)
```

## Segredos AWS no GitHub Actions

Os seguintes GitHub Secrets devem ser configurados no repositório:

| Secret | Descrição |
|--------|-----------|
| `AWS_ACCESS_KEY_ID` | Credencial IAM com permissão de deploy |
| `AWS_SECRET_ACCESS_KEY` | Chave secreta correspondente |
| `TF_STATE_BUCKET` | Nome do bucket S3 para Terraform state |
| `TF_STATE_KEY` | Chave no S3 para o state file |
| `CLOUDFRONT_DISTRIBUTION_ID` | ID da distribuição (após primeiro apply) |

## Permissões IAM para Deploy

A conta IAM de deploy precisa de permissões para:
- Lambda: `CreateFunction`, `UpdateFunctionCode`, `UpdateFunctionConfiguration`
- API Gateway: `CreateRestApi`, `PutIntegration`, `CreateDeployment`
- DynamoDB: `CreateTable`, `UpdateTable`
- Cognito: `CreateUserPool`, `CreateUserPoolClient`
- SES: `VerifyEmailIdentity`
- S3: `PutObject`, `ListBucket`, `GetBucketLocation`
- CloudFront: `CreateDistribution`, `CreateInvalidation`
- IAM: `CreateRole`, `AttachRolePolicy` (para roles Lambda)
- EventBridge: `CreateSchedule`

Recomendação: criar uma role dedicada de deploy com política customizada — não usar root ou AdministratorAccess.
