# Smoke Test Results — Task Manager API (dev)
<!-- v-final -->

## Upstream Artifacts

- `construction/build-and-test/build-test-results.md` — baseline de 66 testes, 85.42% cobertura
- `operation/environment-provisioning/environment-inventory.md` — endpoints de referência

## API Smoke Tests

**Data:** 2026-08-19
**API URL:** `https://55mmgn9541.execute-api.us-east-1.amazonaws.com/dev`

| Endpoint | Método | Auth | HTTP Status | Esperado | Resultado |
|----------|--------|------|-------------|----------|-----------|
| `/v1/tasks` | GET | Nenhuma | 401 | 401 | ✅ PASS |
| `/v1/users` | GET | Nenhuma | 401 | 401 | ✅ PASS |
| `/v1/tasks` | POST | Nenhuma | 401 | 401 | ✅ PASS |
| `/v1/invalid` | GET | Nenhuma | 403 | 403/404 | ✅ PASS |

**Conclusão:** Cognito authorizer ativo e funcionando — rejeita requests sem JWT.

## Frontend Smoke Tests

**URL:** `https://d2nfh2e0o8hl2q.cloudfront.net`

| Check | Status | Detalhe |
|-------|--------|---------|
| CloudFront distribuição ativa | ✅ | Status: Deployed |
| Arquivos S3 enviados | ✅ | index.html, app.js, styles.css |
| CloudFront invalidation | ✅ | ID: I51GBYNCLPJN818GRBTHDYRUFY |
| APP_CONFIG com valores reais | ✅ | API URL, Cognito domain, client ID configurados |

## Testes Manuais Pendentes (pós-criação de usuário)

Para executar após criar o primeiro usuário no Cognito:

```bash
# 1. Acessar a URL de login do Cognito
https://task-manager-dev.auth.us-east-1.amazoncognito.com/login?client_id=2hspqeq5h1k6tts5hdpmm2nvnf&response_type=code&scope=openid+email+profile&redirect_uri=https://d2nfh2e0o8hl2q.cloudfront.net/

# 2. Após login, testar a API com o JWT obtido
TOKEN="seu-jwt-aqui"
curl -H "Authorization: Bearer $TOKEN" \
  "https://55mmgn9541.execute-api.us-east-1.amazonaws.com/dev/v1/tasks"
# Esperado: 200 com lista vazia []

# 3. Criar uma tarefa
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Primeira tarefa","priority":"high"}' \
  "https://55mmgn9541.execute-api.us-east-1.amazonaws.com/dev/v1/tasks"
# Esperado: 201 com tarefa criada
```
