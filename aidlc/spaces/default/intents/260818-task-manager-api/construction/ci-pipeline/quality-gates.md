# Quality Gates — Task Manager API
<!-- confirmed -->

## Upstream Artifacts

- `construction/build-and-test/build-test-results.md` — resultados reais confirmados
- `construction/task-manager-api/code-generation/code-summary.md` — cobertura 86.9% (geração) → 85.42% (após fixes)

## Quality Gates Obrigatórios (Merge Blocker)

| Gate | Ferramenta | Threshold | Status Atual |
|------|-----------|-----------|-------------|
| Lint | ruff | 0 violações | ✅ Configurado |
| Format | black | Conformante | ✅ Configurado |
| Testes passando | pytest | 100% (0 falhas) | ✅ 66/66 |
| Cobertura de código | pytest-cov | ≥ 85% | ✅ 85.42% |

## Gates Opcionais (Warning Only)

| Gate | Ferramenta | Threshold | Ação |
|------|-----------|-----------|------|
| Security scan | bandit | Sem HIGH/CRITICAL | Recomendado para v2 |
| Dependency audit | pip-audit | Sem CVEs críticas | Recomendado para v2 |

## Enforcement

- **Branch protection** no repositório GitHub: CI obrigatório antes de merge para `main`
- **`--cov-fail-under=85`** no pytest: exit code 1 se cobertura < 85% → bloqueia CI
- **`black --check`**: exit code 1 se formatação divergir → bloqueia CI
- **`ruff check`**: exit code 1 se violações encontradas → bloqueia CI

## Evidência de Baseline

Os gates foram validados localmente no Build and Test:
- 66 testes passando, 0 falhando
- Cobertura: 85.42% (acima do threshold de 85%)
- Ambiente: Python 3.14.4 local (prod usa 3.13 — wheel disponível no Lambda)

## Exceções Documentadas

| Módulo | Cobertura | Justificativa |
|--------|-----------|---------------|
| `src/utils/auth.py` | 38% | JWKS fetch requer Cognito real — coberto por smoke test pós-deploy |
| `src/handlers/report_handler.py` | 63% | `_list_user_emails` requer Cognito real — coberto por smoke test pós-deploy |
| **Total** | **85.42%** | **Gate ≥85% atingido** |
