# Deployment Pipeline Questions — Task Manager API

## Sources
- Upstream: `construction/ci-pipeline/ci-config.md`, `construction/ci-pipeline/quality-gates.md`
- Stack definida em `tech-env.md`: Terraform, Lambda, S3+CloudFront

## Q1. Deployment Strategy

Para uma API serverless interna com 20-30 usuários, qual estratégia de deploy é adequada?

A. Deploy direto (in-place) — Terraform aplica as mudanças diretamente no ambiente
B. Blue/Green — dois ambientes, troca de tráfego instantânea
C. Canary — roll out gradual de porcentagem
X. Outro (especificar)

[Answer]: A. Deploy direto (in-place) — Terraform aplica as mudanças diretamente no ambiente

## Q2. Approval antes de deploy em produção

Conforme `org.md ## Deployment`: production deploys gate on a separate manual approval.

[Answer]: A. Sim — tech lead deve aprovar manualmente antes do deploy em produção (workflow protection rule)

## Q3. Rollback Strategy

[Answer]: A. Redeploy da versão anterior via Terraform (re-run do pipeline com a versão anterior tagueada)

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
