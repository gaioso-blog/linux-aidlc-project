# Health Check Report — Task Manager API (dev)
<!-- v-final -->

## Upstream Artifacts

- `operation/environment-provisioning/environment-inventory.md`
- `operation/deployment-execution/smoke-test-results.md`

## Status Geral

✅ **SISTEMA OPERACIONAL** — API e frontend no ar

## Checklist de Saúde

| Componente | Status | URL/ID |
|------------|--------|--------|
| API Gateway | ✅ Ativo | `https://55mmgn9541.execute-api.us-east-1.amazonaws.com/dev` |
| Lambda tasks | ✅ Deployado | `task-manager-tasks-dev` |
| Lambda users | ✅ Deployado | `task-manager-users-dev` |
| Lambda report | ✅ Deployado | `task-manager-report-dev` |
| DynamoDB tasks | ✅ Ativo | `task-manager-tasks-dev` |
| DynamoDB users | ✅ Ativo | `task-manager-users-dev` |
| Cognito User Pool | ✅ Ativo | `us-east-1_RFVLogmXi` |
| SES identity | ⚠️ Pendente verificação | `joaovitorgaioso@outlook.com` — verificar caixa de entrada |
| EventBridge Scheduler | ✅ Ativo | Sextas 09:00 America/Sao_Paulo |
| S3 Frontend | ✅ Com conteúdo | `task-manager-frontend-dev-455697799121` |
| CloudFront | ✅ Ativo | `https://d2nfh2e0o8hl2q.cloudfront.net` |

## Próximos Passos para Operação

1. **Verificar email SES** — clicar no link na caixa de `joaovitorgaioso@outlook.com`
2. **Criar primeiro usuário Cognito:**
   - AWS Console → Cognito → `us-east-1_RFVLogmXi` → Users → Create user
   - Email: email do usuário, senha temporária
3. **Acessar o frontend:** `https://d2nfh2e0o8hl2q.cloudfront.net`
4. **Testar fluxo completo:** login → criar tarefa → atribuir → verificar notificação email

## Configurar GitHub Secrets para CD Automático

Para ativar o `deploy.yml` no GitHub Actions:

```
AWS_ACCESS_KEY_ID        = <credencial IAM de deploy>
AWS_SECRET_ACCESS_KEY    = <chave correspondente>
TF_STATE_BUCKET          = state-aidlc-terraform
TF_STATE_KEY             = task-manager/dev/terraform.tfstate
CLOUDFRONT_DISTRIBUTION_ID = E2Q0LZ0GQBFYMB
```
