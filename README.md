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
pytest tests/ --cov=src --cov-fail-under=85 -v
```

---

## Rodando os testes

```bash
# Todos os testes com cobertura
pytest tests/ --cov=src --cov-fail-under=85 --cov-report=term-missing

# Somente unit tests
pytest tests/unit/ -v --no-cov

# Somente integration tests (requerem moto)
pytest tests/integration/ -v --no-cov

# Um arquivo específico
pytest tests/unit/test_task_service.py -v --no-cov
```

---

## Deploy

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
aws s3 sync frontend/ s3://$(terraform output -raw bucket_name)/ --delete
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