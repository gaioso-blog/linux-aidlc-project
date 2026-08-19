# Rollback Runbook — Task Manager API
<!-- confirmed -->

## Upstream Artifacts

- `construction/ci-pipeline/quality-gates.md` — gates de qualidade que devem ser respeitados no rollback
- `construction/ci-pipeline/ci-config.md` — pipeline CI/CD de referência

## Estratégia de Rollback

**Redeploy da versão anterior via Git + Terraform.**

Como o estado da aplicação está no DynamoDB (não no código), um rollback de código não afeta dados existentes.

## Procedimento de Rollback de Código Lambda

```bash
# 1. Identificar o commit que causou o problema
git log --oneline -10

# 2. Criar branch de rollback a partir do commit anterior
git checkout -b rollback/hotfix <COMMIT_HASH_ANTERIOR>

# 3. Criar PR para main OU fazer redeploy manual direto
# Opção A: Via PR (seguro — passa pelo CI)
git push origin rollback/hotfix
# Abrir PR → CI passa → merge → CD deploya automaticamente

# Opção B: Deploy manual emergencial
cd infra/environments/dev
git checkout <COMMIT_HASH_ANTERIOR>
terraform plan
terraform apply
```

## Rollback de Frontend (S3)

```bash
# Fazer checkout da versão anterior do frontend
git checkout <COMMIT_HASH_ANTERIOR> -- frontend/

# Re-sincronizar com S3
aws s3 sync frontend/ s3://BUCKET_NAME/ --delete

# Invalidar cache CloudFront
aws cloudfront create-invalidation \
  --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
  --paths "/*"
```

## Rollback de Infraestrutura (Terraform)

Terraform mantém o state — não há rollback automático de infra. Se um `terraform apply` destruiu recursos incorretamente:

```bash
# Verificar o state atual
terraform state list

# Para recursos críticos: usar terraform import para re-importar
# ou restaurar o state file do backup S3
aws s3 cp s3://TF-STATE-BUCKET/task-manager/dev/terraform.tfstate.backup ./terraform.tfstate
```

## Rollback de DynamoDB

Os dados no DynamoDB **não são afetados por rollback de código**. Se uma operação de dados corrompeu registros:

- DynamoDB Point-in-Time Recovery (PITR) deve estar habilitado — verificar nos módulos Terraform
- Restaurar para um ponto no tempo: AWS Console → DynamoDB → Tabela → Backups

## Critérios para Rollback

| Critério | Ação |
|----------|------|
| API retorna 5xx em >10% das requests | Rollback imediato |
| Testes de smoke falhando pós-deploy | Rollback imediato |
| Lambda com timeout excessivo (>25s) | Investigar antes de rollback |
| Frontend não carrega | Rollback de frontend apenas |

## Contato de Escalação

- Equipe auto-organizada — sem SLA externo
- Tempo de rollback esperado: 5-10 minutos via procedimento manual
