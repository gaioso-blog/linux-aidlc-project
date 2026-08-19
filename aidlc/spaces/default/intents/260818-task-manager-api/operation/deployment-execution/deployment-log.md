# Deployment Log — Task Manager API (dev)
<!-- v-final: deploy completo, email funcionando, CORS resolvido -->

## Upstream Artifacts

- `operation/deployment-pipeline/cd-config.md`
- `operation/deployment-pipeline/deployment-strategy.md`
- `operation/environment-provisioning/environment-inventory.md`
- `construction/build-and-test/build-test-results.md`

## Deploy Executado

**Data:** 2026-08-19
**Ambiente:** dev (us-east-1)
**Estratégia:** Deploy direto

## Passos Executados

| # | Passo | Status | Detalhe |
|---|-------|--------|---------|
| 1 | Atualizar `frontend/index.html` com configs Cognito/API | ✅ | APP_CONFIG preenchido com valores reais |
| 2 | `aws s3 sync frontend/ s3://task-manager-frontend-dev-455697799121/` | ✅ | 3 arquivos enviados (index.html, app.js, styles.css) |
| 3 | `aws cloudfront create-invalidation` | ✅ | ID: I51GBYNCLPJN818GRBTHDYRUFY |
| 4 | Smoke tests API | ✅ | Todos os endpoints respondem corretamente |

## Configuração Final do Frontend

```javascript
window.APP_CONFIG = {
  API_BASE_URL: "https://55mmgn9541.execute-api.us-east-1.amazonaws.com/dev",
  COGNITO_DOMAIN: "https://task-manager-dev.auth.us-east-1.amazoncognito.com",
  COGNITO_CLIENT_ID: "2hspqeq5h1k6tts5hdpmm2nvnf",
  REDIRECT_URI: window.location.origin + "/",
};
```

## URLs de Acesso

| Recurso | URL |
|---------|-----|
| Frontend | `https://d2nfh2e0o8hl2q.cloudfront.net` |
| API | `https://55mmgn9541.execute-api.us-east-1.amazonaws.com/dev` |
| Cognito Login | `https://task-manager-dev.auth.us-east-1.amazoncognito.com/login?client_id=2hspqeq5h1k6tts5hdpmm2nvnf&response_type=code&scope=openid+email+profile&redirect_uri=https://d2nfh2e0o8hl2q.cloudfront.net/` |
