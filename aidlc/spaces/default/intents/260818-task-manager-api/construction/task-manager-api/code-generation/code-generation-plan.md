# Code Generation Plan — Task Manager API

## Unit

`task-manager-api` — API serverless de gestão de tarefas com frontend funcional, rodando na AWS.

## Scope Summary

**Derived from:** `vision.md`, `tech-env.md`, `ideation/intent-capture/intent-statement.md`

- CRUD completo de tarefas (título, descrição, status, prioridade, responsável, due_date, estimativa de esforço)
- Autenticação via Amazon Cognito (JWT) — provisionamento manual pelo admin
- Notificações por email ao atribuir tarefa (Amazon SES)
- Relatório semanal automático toda sexta (EventBridge Scheduler + SES): tarefas por status por pessoa + total backlog
- Frontend funcional (S3+CloudFront) — interface CRUD similar ao Trello
- IaC com Terraform (terraform-aws-modules, backend S3)
- CI/CD com GitHub Actions

**Stack:** Python 3.13, aws-lambda-powertools, pydantic v2, boto3, pytest, moto, pytest-cov

## Testing Contract

```json
{
  "version": 1,
  "methodology": "test-after",
  "source": "org",
  "ordering": "implement each applicable testable layer, then write and run",
  "scope": "task-manager-api",
  "test_strategy": "standard",
  "project_type": "greenfield",
  "applicable_notes": [
    {
      "layer": "org",
      "text": "We treat tests as a first-class deliverable in every Bolt. The specific\nmethodology (TDD, BDD, ATDD, or classic test-after) is affirmed at\npractices-discovery and recorded in `team.md` under this heading with explicit\n`Methodology` and `Ordering` fields; Code Generation resolves those fields\nindependently from coverage, tooling, and scope notes.\n\nWhen no posture has been affirmed, our default per scope is:\n- **Methodology**: test-after\n- **Ordering**: implement each applicable testable layer, then write and run\n  that layer's tests.\n- `mvp`, `enterprise`, `feature`, `infra` add an 80% line-coverage floor and\n  CI execution before merge.\n- `bugfix`, `security-patch` add a targeted regression for the specific\n  bug/vulnerability and require the existing suite to remain green.\n- `poc`, `refactor`, `workshop` add no extra new-test floor and require the\n  existing suite to remain green.\n\nThe active `Test Strategy` still applies in every scope and determines test\nvolume/types. Scope floors are additive; they never reduce or replace the\nselected strategy.\n\nAffirm a stricter posture in `team.md` if the team commits to one."
    },
    {
      "layer": "team",
      "text": "<!-- Affirmed durante practices-discovery. Não afirmado ainda — usando default org.md. -->"
    },
    {
      "layer": "project",
      "text": "<!-- Project-specific specialisation. -->"
    }
  ],
  "obligations": {
    "strategy": "standard",
    "strategy_volume": [
      "Five to eight tests per component.",
      "Unit tests plus integration tests for key boundaries.",
      "Add E2E, performance, or security tests when requirements demand them."
    ],
    "scope_floor": [
      "Keep the existing test suite green.",
      "This scope adds no extra new-test floor beyond the selected test strategy."
    ],
    "combination_rule": "Apply every selected-strategy obligation and every scope-floor obligation; neither replaces the other, and a targeted scope regression may add the narrowest necessary test type beyond the strategy default."
  },
  "plan_profile": {
    "methodology": "test-after",
    "runner_step": "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
    "runner_ready_before_first_test": true,
    "testable_layers": [
      "Data model / database behavior",
      "Repository / data access",
      "Business logic",
      "API / endpoint",
      "Frontend behavior"
    ],
    "steps": [
      "Project structure and production configuration skeleton.",
      "Bootstrap the minimal test runner/configuration and record the exact unit-scoped command.",
      "Data model / database behavior - implement.",
      "Data model / database behavior - write and run its tests after implementation.",
      "Repository / data access - implement.",
      "Repository / data access - write and run its tests after implementation.",
      "Business logic - implement.",
      "Business logic - write and run its tests after implementation.",
      "API / endpoint - implement.",
      "API / endpoint - write and run its tests after implementation.",
      "Frontend behavior - implement.",
      "Frontend behavior - write and run its tests after implementation.",
      "Environment/build configuration.",
      "Documentation and traceability."
    ]
  },
  "input_sha256": "sha256:77710da8e6da381463e233507f125271a1428969cabdbc2cbeb7448894d6a726",
  "contract_sha256": "sha256:a5f2021a94ecdb2d8b937aed5bd6d19366a0a3a968fedfb13d1a69e60796e344"
}
```

## Implementation Steps

### Step 1 — Project structure and production configuration skeleton

- [x] Create workspace directory structure per `tech-env.md`:
  ```
  src/handlers/, src/services/, src/repositories/, src/models/, src/utils/
  tests/unit/, tests/integration/
  infra/modules/, infra/environments/
  frontend/
  ```
- [x] Create `requirements.txt` (aws-lambda-powertools, boto3, pydantic)
- [x] Create `requirements-dev.txt` (pytest, pytest-cov, moto, httpx, freezegun)
- [x] Create `pyproject.toml` with Black + Ruff config
- [x] Create `.gitignore`

### Step 2 — Bootstrap test runner

- [x] Create `pytest.ini` / `pyproject.toml` pytest config with coverage settings
- [x] Verify exact unit-scoped command: `pytest tests/ --cov=src --cov-fail-under=85`
- [x] Create `tests/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`

### Step 3 — Data models (implement)

- [x] `src/models/task.py` — Pydantic Task model (todos os campos: task_id, title, description, status, priority, assignee_id, due_date, effort_estimate, created_at, updated_at)
- [x] `src/models/user.py` — Pydantic User model (user_id, email, name)

### Step 4 — Data models (tests)

- [x] `tests/unit/test_models.py` — 5-8 testes de validação Pydantic (campos obrigatórios, valores inválidos, serialização)

### Step 5 — Repository layer (implement)

- [x] `src/repositories/task_repository.py` — TaskRepository com DynamoDB (get, put, update, delete, list_by_assignee, list_all)
- [x] `src/repositories/user_repository.py` — UserRepository (get_by_id, list_all)

### Step 6 — Repository layer (tests)

- [x] `tests/integration/test_task_repository.py` — 5-8 testes com moto mock_aws (CRUD + queries)
- [x] `tests/integration/test_user_repository.py` — 3-5 testes com moto

### Step 7 — Business logic / services (implement)

- [x] `src/services/task_service.py` — TaskService (create_task, get_task, update_task, delete_task, assign_task, list_tasks)
- [x] `src/services/notification_service.py` — NotificationService (send_assignment_email via SES)
- [x] `src/services/report_service.py` — ReportService (generate_weekly_report: tarefas por status por pessoa + total backlog)

### Step 8 — Business logic (tests)

- [x] `tests/unit/test_task_service.py` — 5-8 testes unitários com mocks (assign_task triggers notification, create_task persists)
- [x] `tests/unit/test_notification_service.py` — 3-5 testes (email format, SES mock)
- [x] `tests/unit/test_report_service.py` — 3-5 testes (report aggregation logic)

### Step 9 — API handlers (implement)

- [x] `src/handlers/tasks_handler.py` — Lambda handler com APIGatewayRestResolver:
  - `POST /v1/tasks` — criar tarefa
  - `GET /v1/tasks` — listar tarefas (filtros: status, assignee)
  - `GET /v1/tasks/{task_id}` — obter tarefa
  - `PUT /v1/tasks/{task_id}` — atualizar tarefa
  - `DELETE /v1/tasks/{task_id}` — deletar tarefa
- [x] `src/handlers/users_handler.py` — Lambda handler:
  - `GET /v1/users` — listar usuários do Cognito
  - `GET /v1/users/me` — perfil do usuário atual
- [x] `src/handlers/report_handler.py` — Lambda handler para EventBridge:
  - Handler para relatório semanal automático

### Step 10 — API handlers (tests)

- [x] `tests/unit/test_tasks_handler.py` — 6-8 testes com APIGatewayRestResolver (happy path + 400/401/404)
- [x] `tests/unit/test_users_handler.py` — 3-5 testes
- [x] `tests/unit/test_report_handler.py` — 3-5 testes

### Step 11 — Frontend (implement)

- [x] `frontend/index.html` — SPA com HTML/CSS/JavaScript vanilla
  - Board view com colunas: Pending | In Progress | Done
  - Cards de tarefa com título, prioridade, responsável, due_date
  - Modal para criar/editar tarefa (todos os campos)
  - Drag-and-drop de cards entre colunas
  - Autenticação via Cognito Hosted UI (OAuth2/JWT)
  - Light/dark theme toggle
- [x] `frontend/app.js` — Lógica de aplicação (API calls, autenticação, DOM manipulation)
- [x] `frontend/styles.css` — Estilos com suporte a temas

### Step 12 — Frontend (tests)

- [x] Testes manuais de smoke test documentados em `tests/frontend_smoke_test.md`
  (sem framework de testes de frontend nesta v1 — validação em Build & Test)

### Step 13 — Infrastructure (Terraform)

- [x] `infra/modules/lambda/main.tf` + `variables.tf` + `outputs.tf` — módulo Lambda (terraform-aws-modules/lambda/aws ~> 7.0)
- [x] `infra/modules/api_gateway/main.tf` — módulo API Gateway REST
- [x] `infra/modules/dynamodb/main.tf` — tabela Tasks + tabela Users
- [x] `infra/modules/cognito/main.tf` — User Pool + App Client
- [x] `infra/modules/ses/main.tf` — SES email identity
- [x] `infra/modules/eventbridge/main.tf` — Scheduler para relatório semanal (cron sexta 09:00)
- [x] `infra/modules/frontend/main.tf` — S3 bucket + CloudFront distribution
- [x] `infra/environments/dev/main.tf` — ambiente de dev (chamada dos módulos)
- [x] `infra/environments/dev/terraform.tfvars` — variáveis do ambiente
- [x] `infra/backend.tf` — remote state em S3
- [x] `infra/versions.tf` — versões do Terraform e providers

### Step 14 — CI/CD

- [x] `.github/workflows/ci.yml` — GitHub Actions: checkout, setup Python 3.13, pip install, pytest --cov ≥85%, ruff check, black --check

### Step 15 — Environment configuration

- [x] `.env.example` — variáveis de ambiente necessárias (TABLE_NAME, COGNITO_USER_POOL_ID, SES_FROM_EMAIL, etc.)
- [x] `src/utils/config.py` — leitura de variáveis de ambiente via os.environ

### Step 16 — Documentation and traceability

- [x] `README.md` — setup, deploy, uso
- [x] Criar `code-summary.md` e `traceability.json`

## Plan Approval

[Approval Fingerprint]: sha256:6aa04d3f7dcc4b866350bff9dc0bfa86a3f5d55b68db0fa55f3abcb7909c699a

- Approve Plan
- Request Changes

[Answer]:
