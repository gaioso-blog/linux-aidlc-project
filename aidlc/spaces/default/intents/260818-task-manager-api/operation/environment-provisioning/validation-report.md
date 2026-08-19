# Validation Report — Environment Provisioning
<!-- confirmed -->

## Upstream Artifacts

- `operation/deployment-pipeline/cd-config.md`

## Resultado do Provisionamento

**Status:** ✅ SUCESSO — 66 recursos criados, 0 erros finais

### Erros Encontrados e Resolvidos

| Erro | Causa | Resolução |
|------|-------|-----------|
| `AWS_DEFAULT_REGION` reservado pelo Lambda | Variável de ambiente reservada passada explicitamente | Removida dos `environment_variables` em todos os módulos Lambda |
| API Gateway deployment sem integração | `depends_on` ausente no deployment | Adicionado `depends_on` nos módulos `tasks_any`, `task_id_any`, `users_any`, `me_any` |
| Sub-módulo `./method` não existia | Gerado pelo Code Generation sem criar o diretório | Criado `infra/modules/api_gateway/method/main.tf` |
| `versions.tf` conflito de provider | Provider duplicado na raiz de `infra/` e no ambiente | Removido `infra/versions.tf`, mantido apenas em `environments/dev/main.tf` |

## Validações Pós-Apply

| Check | Status |
|-------|--------|
| `terraform plan` após apply mostra 0 mudanças | ✅ Confirmado |
| API Gateway endpoint responde | A verificar no Deployment Execution |
| CloudFront distribuição ativa | ✅ `E2Q0LZ0GQBFYMB` — status Deployed |
| DynamoDB tables criadas | ✅ `task-manager-tasks-dev`, `task-manager-users-dev` |
| Lambda functions criadas | ✅ tasks, users, report |
| Cognito User Pool ativo | ✅ `us-east-1_RFVLogmXi` |
| EventBridge Scheduler ativo | ✅ `task-manager-weekly-report-dev` |

## Security Posture

- IAM roles com princípio de menor privilégio (uma role por Lambda)
- DynamoDB PITR habilitado (Point-in-Time Recovery)
- S3 bucket privado — acesso apenas via CloudFront OAC
- Cognito admin-only user creation (sem auto-registro)
- Sem hardcoded credentials no Terraform state

## Pendências

- Email SES `joaovitorgaioso@outlook.com` precisa ser verificado (link na caixa de entrada)
- Frontend ainda não foi carregado para o S3 (Deployment Execution)
- Primeiro usuário Cognito ainda não criado
