# Task Manager API

API serverless de gestão de tarefas para uso interno da equipe (20–30 devs/arquitetos).

## Stack

| Componente | Tecnologia |
|------------|------------|
| Linguagem | Python 3.13 |
| Compute | AWS Lambda |
| API | API Gateway REST |
| Database | DynamoDB |
| Auth | Amazon Cognito |
| Email | Amazon SES |
| Agendamento | EventBridge Scheduler |
| Frontend | S3 + CloudFront |
| IaC | Terraform |
| CI | GitHub Actions |

---

## Pré-requisitos

- Python 3.13+
- pip
- Terraform >= 1.6
- AWS CLI configurado com credenciais de uma conta dedicada
- Conta AWS com SES fora do sandbox (solicite via Support antes do deploy)

---

## Setup local

```bash
# 1. Clone o repositório
git clone <repo-url>
cd task-manager

# 2. Instale as dependências
pip install -r requirements.txt -r requirements-dev.txt

# 3. Configure as variáveis de ambiente
cp .env.example .env.local
# edite .env.local com seus valores

# 4. Rode os testes
pytest tests/ --cov=src --cov-fail-under=80 -v
```

---

## Rodando os testes

```bash
# Todos os testes com cobertura
pytest tests/ --cov=src --cov-fail-under=80 --cov-report=term-missing

# Somente unit tests
pytest tests/unit/ -v --no-cov

# Somente integration tests (requerem moto)
pytest tests/integration/ -v --no-cov

# Um arquivo específico
pytest tests/unit/test_task_service.py -v --no-cov
```

---

## CI/CD

Fluxo trunk-based. Ninguém aplica Terraform da máquina local depois do bootstrap
inicial — o pipeline é o único caminho para `dev`.

```
push em feature/**          PR aprovado + merge em main
        │                              │
        ▼                              ▼
  ci.yml                          deploy.yml
  ├── test                        ├── test
  │   ruff + black + pytest       │   ruff + black + pytest
  ├── terraform-plan              └── deploy
  │   validate + plan (read-only)     build lambda.zip
  └── open-pr                          terraform apply
      abre PR para main                s3 sync + CloudFront invalidation
                                       smoke test
```

### `ci.yml` — validação

Dispara em push para `feature/**`, `fix/**`, `chore/**` e em PRs para `main`.

| Job | Roda quando | O que faz |
|-----|-------------|-----------|
| `test` | sempre | `ruff check`, `black --check`, `pytest` com cobertura mínima de 80% |
| `terraform-plan` | após `test` | `terraform validate` + `plan`. Nunca aplica. O plan vai para o job summary e para o artifact `terraform-plan` |
| `open-pr` | só em push | Abre PR para `main` se ainda não existir; se existir, só comenta que o CI voltou a ficar verde |

O `plan` roda no **push da feature**, não no evento de PR. Isso é
intencional: PR criado com `GITHUB_TOKEN` não dispara workflows, então
esperar o evento de PR faria o plan nunca rodar no PR automático.

### `deploy.yml` — entrega

Dispara **somente** em push para `main`, isto é, no merge do PR. Repete os
testes como gate, empacota a Lambda com wheels `manylinux2014_x86_64` para
`cp313`, aplica o Terraform, injeta os outputs reais no `index.html`,
sincroniza o S3 e invalida o CloudFront. Termina com um smoke test que exige
`200` ou `401` em `GET /v1/tasks` (`401` é resposta válida: prova que o
authorizer do Cognito está ativo).

### Configuração necessária no repositório

Secrets em **Settings → Secrets and variables → Actions**:

| Secret | Valor |
|--------|-------|
| `AWS_ACCESS_KEY_ID` | credencial com permissão de apply |
| `AWS_SECRET_ACCESS_KEY` | — |
| `TF_STATE_BUCKET` | bucket do state remoto |

Em **Settings → Actions → General → Workflow permissions**:

- `Read and write permissions`
- `Allow GitHub Actions to create and approve pull requests` — sem isso o job
  `open-pr` falha com `403`

---

## Deploy manual

Necessário apenas no **bootstrap** de um ambiente novo, antes de o pipeline
assumir. Em operação normal, use o fluxo de CI/CD acima.

### 1. Preparar o ambiente

```bash
cd infra/environments/dev

# Edite terraform.tfvars com seus valores reais
# Especialmente: ses_email e cognito_domain_prefix (deve ser globalmente único)
```

### 2. Inicializar e aplicar

```bash
terraform init
terraform plan
terraform apply
```

### 3. Após o apply

O Terraform irá exibir os outputs:

```
api_url           = "https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev"
frontend_url      = "https://xxxxxxxxxx.cloudfront.net"
cognito_domain    = "https://task-manager-dev.auth.us-east-1.amazoncognito.com"
cognito_client_id = "your-client-id"
```

### 4. Atualizar o frontend

Edite `frontend/index.html` — bloco `window.APP_CONFIG`:

```javascript
window.APP_CONFIG = {
  API_BASE_URL: "https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev",
  COGNITO_DOMAIN: "https://task-manager-dev.auth.us-east-1.amazoncognito.com",
  COGNITO_CLIENT_ID: "your-client-id",
  REDIRECT_URI: "https://xxxxxxxxxx.cloudfront.net/",
};
```

### 5. Publicar o frontend

```bash
aws s3 sync frontend/ s3://$(terraform output -raw frontend_bucket)/ --delete
aws cloudfront create-invalidation \
  --distribution-id $(terraform output -raw cloudfront_distribution_id) \
  --paths "/*"
```

### 6. Criar usuários no Cognito

```bash
aws cognito-idp admin-create-user \
  --user-pool-id <user-pool-id> \
  --username alice@example.com \
  --user-attributes Name=email,Value=alice@example.com Name=name,Value="Alice" \
  --temporary-password "Temp@2025!"
```

---

## Estrutura do projeto

```
.
├── src/
│   ├── handlers/          # Lambda entrypoints
│   ├── services/          # Business logic
│   ├── repositories/      # DynamoDB data access
│   ├── models/            # Pydantic models
│   └── utils/             # Auth, config, helpers
├── tests/
│   ├── unit/              # Testes com mocks
│   └── integration/       # Testes com moto (DynamoDB mock)
├── infra/
│   ├── modules/           # Módulos Terraform reutilizáveis
│   └── environments/dev/  # Ambiente de desenvolvimento
├── frontend/              # SPA HTML/CSS/JS
├── .github/workflows/     # GitHub Actions CI
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

---

## API Reference

Base URL: `https://<api-gateway-id>.execute-api.us-east-1.amazonaws.com/dev`

Todos os endpoints requerem `Authorization: Bearer <cognito-jwt>`.

### Tasks

| Método | Path | Descrição |
|--------|------|-----------|
| `POST` | `/v1/tasks` | Criar tarefa |
| `GET` | `/v1/tasks` | Listar tarefas (`?status=pending&assignee_id=...`) |
| `GET` | `/v1/tasks/{task_id}` | Obter tarefa |
| `PUT` | `/v1/tasks/{task_id}` | Atualizar tarefa |
| `DELETE` | `/v1/tasks/{task_id}` | Deletar tarefa |

### Users

| Método | Path | Descrição |
|--------|------|-----------|
| `GET` | `/v1/users` | Listar usuários do Cognito |
| `GET` | `/v1/users/me` | Perfil do usuário atual |

### Formato de erro

```json
{
  "statusCode": 404,
  "message": "Task not found: abc-123"
}
```

---

## Campos de uma tarefa

| Campo | Tipo | Obrigatório | Valores |
|-------|------|-------------|---------|
| `task_id` | string (UUID) | gerado | — |
| `title` | string (1–200) | sim | — |
| `description` | string (max 2000) | não | — |
| `status` | enum | não (default: pending) | `pending`, `in_progress`, `done` |
| `priority` | enum | não (default: medium) | `low`, `medium`, `high` |
| `assignee_id` | string | não | Cognito sub |
| `due_date` | string | não | `YYYY-MM-DD` |
| `effort_estimate` | float (≥ 0) | não | horas |
| `created_at` | ISO 8601 | gerado | — |
| `updated_at` | ISO 8601 | gerado | — |

---

## Relatório semanal

O relatório é disparado automaticamente toda **sexta-feira às 09:00 (horário de Brasília)** via EventBridge Scheduler.

Para disparar manualmente:

```bash
aws lambda invoke \
  --function-name task-manager-report-dev \
  --payload '{}' \
  /tmp/response.json
```
