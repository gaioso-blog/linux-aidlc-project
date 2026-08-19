# CI Configuration — Task Manager API
<!-- confirmed: Looks correct -->

## Upstream Artifacts

- `construction/task-manager-api/code-generation/code-summary.md` — stack e estrutura do projeto
- `construction/build-and-test/build-and-test-summary.md` — assessment de readiness e comandos de teste
- `construction/build-and-test/build-test-results.md` — resultados reais: 66/66 testes, 85.42% cobertura

## CI Tool

**GitHub Actions** — conforme `tech-env.md` e já implementado em `.github/workflows/ci.yml`.

## Pipeline File

**Arquivo:** `.github/workflows/ci.yml`

**Triggers:**
- `push` em `main`
- `pull_request` em `main`

**Runner:** `ubuntu-latest` com Python 3.13 (cache pip habilitado)

## Pipeline Steps

| # | Step | Ferramenta | Critério de Aprovação |
|---|------|-----------|----------------------|
| 1 | Checkout | `actions/checkout@v4` | Exit code 0 |
| 2 | Setup Python 3.13 | `actions/setup-python@v5` | Exit code 0 |
| 3 | Instalar dependências | `pip install -r requirements.txt -r requirements-dev.txt` | Exit code 0 |
| 4 | Lint | `ruff check src/ tests/` | 0 violações |
| 5 | Format check | `black --check src/ tests/` | Código conformante |
| 6 | Testes + cobertura | `pytest tests/ --cov=src --cov-fail-under=85` | 100% pass, ≥85% cobertura |
| 7 | Upload coverage | `actions/upload-artifact@v4` | Sempre executa (`if: always()`) |

## Variáveis de Ambiente no CI

Todas as variáveis sensíveis usam valores de teste seguros (sem credenciais AWS reais):

```yaml
TABLE_NAME_TASKS: tasks-table
TABLE_NAME_USERS: users-table
COGNITO_USER_POOL_ID: us-east-1_test
COGNITO_APP_CLIENT_ID: test-client-id
SES_FROM_EMAIL: noreply@test.com
AWS_ACCESS_KEY_ID: testing          # moto intercepta chamadas
AWS_SECRET_ACCESS_KEY: testing      # moto intercepta chamadas
```

## Branch Strategy

Trunk-based development (conforme `org.md ## Way of Working`):
- Feature branches: curtas (≤ 1-2 dias), merge para `main` via PR
- Squash merge para manter histórico limpo em `main`
- CI obrigatório antes de merge (branch protection rule)

## Artefatos Gerados pelo CI

- `coverage.xml` — relatório de cobertura (upload como GitHub Actions artifact)
- Nenhum artefato de build binário na v1 (Lambda code é deploiado via Terraform)
