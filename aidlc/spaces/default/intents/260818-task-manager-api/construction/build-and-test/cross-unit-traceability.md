# Cross-Unit Traceability — Task Manager API

## Scope

Esta etapa tem uma única unit (`task-manager-api`). O cross-unit traceability cobre todos os requisitos do PRF (`vision.md`) e os artefatos de Code Generation.

## Rastreabilidade Requisito → Código → Teste

| Requisito | Status | Implementação | Testes |
|-----------|--------|---------------|--------|
| CRUD de tarefas (criar) | ✅ OK | `src/handlers/tasks_handler.py:create_task`, `src/services/task_service.py:create_task` | `tests/unit/test_tasks_handler.py`, `tests/unit/test_task_service.py` |
| CRUD de tarefas (ler) | ✅ OK | `src/handlers/tasks_handler.py:get_task`, `src/services/task_service.py:get_task` | `tests/unit/test_tasks_handler.py` |
| CRUD de tarefas (listar) | ✅ OK | `src/handlers/tasks_handler.py:list_tasks`, `src/services/task_service.py:list_tasks` | `tests/unit/test_task_service.py` |
| CRUD de tarefas (atualizar) | ✅ OK | `src/handlers/tasks_handler.py:update_task`, `src/services/task_service.py:update_task` | `tests/unit/test_task_service.py` |
| CRUD de tarefas (deletar) | ✅ OK | `src/handlers/tasks_handler.py:delete_task`, `src/services/task_service.py:delete_task` | `tests/unit/test_task_service.py` |
| Campos: title, description, status, priority, assignee_id, due_date, effort_estimate | ✅ OK | `src/models/task.py:Task` | `tests/unit/test_models.py` |
| Autenticação Cognito JWT | ✅ OK | `src/utils/auth.py`, `src/handlers/tasks_handler.py:_require_auth` | `tests/unit/test_tasks_handler.py` (mock) |
| Atribuição de tarefas | ✅ OK | `src/services/task_service.py:assign_task` | `tests/unit/test_task_service.py` |
| Notificação SES ao atribuir | ✅ OK | `src/services/notification_service.py:send_assignment_email` | `tests/unit/test_notification_service.py` |
| Relatório semanal EventBridge | ✅ OK | `src/handlers/report_handler.py`, `infra/modules/eventbridge/main.tf` | `tests/unit/test_report_handler.py` |
| Relatório: tarefas por status por pessoa | ✅ OK | `src/services/report_service.py:generate_weekly_report` | `tests/unit/test_report_service.py` |
| Frontend SPA Kanban | ✅ OK | `frontend/index.html`, `frontend/app.js`, `frontend/styles.css` | `tests/frontend_smoke_test.md` (manual) |
| Frontend: drag-and-drop | ✅ OK | `frontend/app.js:TaskBoard` (HTML5 DnD API) | Manual |
| Frontend: Cognito auth (PKCE) | ✅ OK | `frontend/app.js:CognitoAuth` | Manual |
| Frontend: temas light/dark | ✅ OK | `frontend/app.js:ThemeManager`, `frontend/styles.css` | Manual |
| IaC Lambda | ✅ OK | `infra/modules/lambda/main.tf` | N/A (infra) |
| IaC API Gateway | ✅ OK | `infra/modules/api_gateway/main.tf` | N/A (infra) |
| IaC DynamoDB | ✅ OK | `infra/modules/dynamodb/main.tf` | N/A (infra) |
| IaC Cognito | ✅ OK | `infra/modules/cognito/main.tf` | N/A (infra) |
| IaC SES | ✅ OK | `infra/modules/ses/main.tf` | N/A (infra) |
| IaC S3 + CloudFront frontend | ✅ OK | `infra/modules/frontend/main.tf` | N/A (infra) |
| CI GitHub Actions | ✅ OK | `.github/workflows/ci.yml` | N/A (pipeline) |

## Veredicto

✅ **PASS** — todos os requisitos do PRF v1 têm implementação rastreável e cobertura de teste (manual para frontend, automatizada para API).

## Itens Pendentes (não bloqueadores)

- `auth.py`: cobertura de integração real requer endpoint Cognito (smoke test pós-deploy)
- `report_handler.py`: `_list_user_emails` via paginador Cognito — teste de integração pós-deploy
- Frontend: 28 cenários de smoke test documentados em `tests/frontend_smoke_test.md` para execução manual pós-deploy
