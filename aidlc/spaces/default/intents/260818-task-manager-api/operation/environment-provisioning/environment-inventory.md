# Environment Inventory — Task Manager API (dev)
<!-- confirmed -->

## Upstream Artifacts

- `operation/deployment-pipeline/cd-config.md` — CD pipeline config

## Provisionamento

**Data:** 2026-08-19
**Conta AWS:** dedicada
**Região:** us-east-1
**Terraform state:** `s3://state-aidlc-terraform/task-manager/dev/terraform.tfstate`
**Recursos criados:** 66

## Endpoints e Recursos Principais

| Recurso | Identificador / URL |
|---------|-------------------|
| **API Gateway** | `https://55mmgn9541.execute-api.us-east-1.amazonaws.com/dev` |
| **Frontend (CloudFront)** | `https://d2nfh2e0o8hl2q.cloudfront.net` |
| **Cognito Hosted UI** | `https://task-manager-dev.auth.us-east-1.amazoncognito.com` |
| **Cognito User Pool ID** | `us-east-1_RFVLogmXi` |
| **Cognito App Client ID** | `2hspqeq5h1k6tts5hdpmm2nvnf` |
| **DynamoDB Tasks** | `task-manager-tasks-dev` |
| **DynamoDB Users** | `task-manager-users-dev` |
| **S3 Frontend Bucket** | `task-manager-frontend-dev-455697799121` |
| **CloudFront Distribution** | `E2Q0LZ0GQBFYMB` |
| **EventBridge Scheduler** | `task-manager-weekly-report-dev` (sextas 09:00 America/Sao_Paulo) |
| **SES Identity** | `joaovitorgaioso@outlook.com` |

## Status dos Recursos

| Serviço | Status |
|---------|--------|
| Lambda tasks | ✅ `task-manager-tasks-dev` |
| Lambda users | ✅ `task-manager-users-dev` |
| Lambda report | ✅ `task-manager-report-dev` |
| API Gateway | ✅ Stage `dev` ativo |
| DynamoDB | ✅ Ambas as tabelas criadas com PITR |
| Cognito | ✅ User Pool + App Client + Hosted UI |
| SES | ✅ Identity criada — verificar caixa de entrada para link de verificação |
| EventBridge | ✅ Scheduler ativo |
| S3 + CloudFront | ✅ Distribuição ativa (aguarda upload do frontend) |

## Ações Pós-Provisionamento Necessárias

1. ⚠️ **Verificar email SES** — clicar no link enviado para `joaovitorgaioso@outlook.com`
2. **Atualizar `frontend/app.js`** com as configurações reais do Cognito:
   - `COGNITO_USER_POOL_ID`: `us-east-1_RFVLogmXi`
   - `COGNITO_CLIENT_ID`: `2hspqeq5h1k6tts5hdpmm2nvnf`
   - `COGNITO_DOMAIN`: `https://task-manager-dev.auth.us-east-1.amazoncognito.com`
   - `API_BASE_URL`: `https://55mmgn9541.execute-api.us-east-1.amazonaws.com/dev`
3. **Upload do frontend** para o S3 (Deployment Execution)
4. **Criar primeiro usuário** no Cognito via console AWS (Admin → Create user)
