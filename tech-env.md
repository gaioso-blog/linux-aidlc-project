# tech-env.md — API Serverless de Gestão de Tarefas

> Documento de ambiente técnico para uso pelo AI-DLC durante Construction.
> Baseado em: `vision.md` (PRF aprovado).

---

## 1. Resumo Técnico do Projeto

| Aspecto             | Decisão                                         |
|---------------------|-------------------------------------------------|
| Nome                | Task Manager API                                |
| Tipo                | Greenfield                                      |
| Cloud               | AWS                                             |
| Modelo de deploy    | Serverless (AWS Lambda)                         |
| Tamanho do time     | 20–30 desenvolvedores/arquitetos                |
| Uso                 | Interno — sem usuários externos                 |
| Timeline v1         | 1 mês                                           |
| Compliance          | Nenhum requisito especial                       |

---

## 2. Linguagens e Package Manager

| Item              | Decisão                         |
|-------------------|---------------------------------|
| Linguagem         | Python 3.13                     |
| Package manager   | pip + `requirements.txt`        |
| Runtime Lambda    | `python3.13`                    |

**Proibido:**
- Python < 3.13 em código novo
- `setup.py` como mecanismo de build (usar `requirements.txt` diretamente)

---

## 3. Frameworks e Bibliotecas

### Obrigatórias

| Biblioteca              | Uso                                              |
|-------------------------|--------------------------------------------------|
| `aws-lambda-powertools` | Roteamento interno, logging estruturado, tracer  |
| `boto3`                 | SDK AWS (DynamoDB, SES, Cognito, etc.)           |
| `pydantic` (v2)         | Validação e serialização de modelos de dados     |
| `pytest`                | Framework de testes                              |
| `pytest-cov`            | Cobertura de código                              |
| `moto`                  | Mock de serviços AWS em testes de integração     |

### Permitidas (conforme necessidade)

| Biblioteca        | Uso                                              |
|-------------------|--------------------------------------------------|
| `python-jose`     | Validação de tokens JWT (Cognito)                |
| `httpx`           | Cliente HTTP em testes de integração             |
| `freezegun`       | Controle de tempo em testes                      |

### Proibidas

| Biblioteca        | Motivo                                                      |
|-------------------|-------------------------------------------------------------|
| `Flask`, `FastAPI`, `Django` | Overhead de cold start — usar `aws-lambda-powertools` Router |
| `SQLAlchemy`, qualquer ORM  | Projeto usa DynamoDB (NoSQL); sem ORM relacional            |
| `requests`        | Usar `httpx` ou `boto3` conforme o caso                     |
| Qualquer framework web WSGI/ASGI | Incompatível com modelo Lambda serverless puro  |

---

## 4. Cloud e Infraestrutura

### Serviços aprovados (v1)

| Serviço                  | Uso                                            |
|--------------------------|------------------------------------------------|
| AWS Lambda               | Compute principal (Python 3.13)                |
| API Gateway (REST)       | Exposição da API                               |
| DynamoDB                 | Banco de dados principal                       |
| Amazon Cognito           | Autenticação e gestão de usuários              |
| Amazon SES               | Envio de emails (notificações + relatórios)    |
| EventBridge Scheduler    | Agendamento do relatório semanal (sextas)      |
| S3                       | Frontend estático + Terraform state backend    |
| CloudFront               | CDN para o frontend                            |
| IAM                      | Políticas e roles para Lambda                  |
| CloudWatch Logs          | Logs de execução Lambda                        |

### Serviços fora de escopo (v1)

- SNS push notifications
- SQS / Kinesis (sem filas ou streams na v1)
- RDS / Aurora (DynamoDB é o único banco)
- App Runner, ECS, EKS (sem containers)
- AWS WAF (sem requisito de segurança avançada na v1)

### Regiões

- `us-east-1`
### Conta AWS

- conta dedicada 

---

## 5. Padrões de Arquitetura e API

### Arquitetura

- **Serverless-first**: toda lógica em Lambda; sem servidores gerenciados
- Um handler Lambda por domínio (ex: `tasks_handler`, `users_handler`, `reports_handler`)
- Roteamento interno via `aws-lambda-powertools` Router — múltiplas rotas num mesmo handler
- Cold start é prioridade: dependências mínimas, sem frameworks pesados

### Padrão de API REST

| Item            | Convenção                                                      |
|-----------------|----------------------------------------------------------------|
| Versionamento   | Path-based: `/v1/tasks`, `/v1/users`                          |
| Nomenclatura    | Snake_case nos campos JSON; plural nos recursos (`/tasks`)     |
| Autenticação    | JWT Cognito via `Authorization: Bearer <token>` header         |
| Erros           | Corpo padronizado: `{"error": "message", "code": "ERROR_CODE"}` |
| HTTP status     | 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error |

---

## 6. Segurança

| Item                  | Decisão                                                         |
|-----------------------|-----------------------------------------------------------------|
| Auth                  | Amazon Cognito User Pool + JWT                                  |
| Autorização           | Validação do JWT no handler via `aws-lambda-powertools` Authorizer ou middleware customizado |
| Secrets               | AWS SSM Parameter Store (sem hardcode de credenciais)           |
| IAM                   | Princípio de menor privilégio — cada Lambda tem role própria    |
| SES                   | Solicitar saída do sandbox no dia 1 (aprovação 24–48h)          |
| Compliance            | Nenhum requisito especial (uso interno)                         |
| OWASP                 | Validação de input via Pydantic em todas as entradas externas   |

---

## 7. Testes

| Item                   | Decisão                                          |
|------------------------|--------------------------------------------------|
| Framework              | `pytest`                                         |
| Cobertura mínima       | 85%                                              |
| Tipos obrigatórios     | Unit + Integration                               |
| Mock AWS               | `moto` para simular DynamoDB, SES, etc.          |
| CI                     | GitHub Actions — testes devem passar antes do merge |
| Gate de merge          | `pytest --cov` com cobertura >= 85% obrigatória  |

---

## 8. IaC — Terraform

| Item                   | Decisão                                             |
|------------------------|-----------------------------------------------------|
| Ferramenta             | Terraform                                           |
| Módulos                | `terraform-aws-modules` (registry público da AWS)  |
| Backend                | S3 (remote state) — sem DynamoDB lock na v1 (TBD)  |
| Estrutura              | Módulos por serviço: `modules/lambda`, `modules/api-gateway`, `modules/dynamodb`, etc. |
| Ambiente               | Variáveis de ambiente via `terraform.tfvars` por ambiente |

---

## 9. Exemplos de Código Canônicos

> Estes exemplos são a referência para geração de código no AI-DLC. Todo código novo deve seguir estes padrões.

### 9.1 Handler Lambda com roteamento (aws-lambda-powertools)

```python
# src/handlers/tasks_handler.py
import json
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime, timezone

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()


class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    assignee_id: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")


class TaskResponse(BaseModel):
    task_id: str
    title: str
    description: Optional[str]
    assignee_id: Optional[str]
    priority: str
    status: str
    created_at: str
    updated_at: str


@app.post("/v1/tasks")
@tracer.capture_method
def create_task():
    body = TaskCreateRequest(**app.current_event.json_body)
    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    task = {
        "task_id": task_id,
        "title": body.title,
        "description": body.description,
        "assignee_id": body.assignee_id,
        "priority": body.priority,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
    }

    # TODO: persist to DynamoDB via repository layer
    logger.info("Task created", task_id=task_id, title=body.title)

    return TaskResponse(**task).model_dump(), 201


@app.get("/v1/tasks/<task_id>")
@tracer.capture_method
def get_task(task_id: str):
    # TODO: fetch from DynamoDB via repository layer
    logger.info("Fetching task", task_id=task_id)
    raise NotImplementedError("get_task not yet implemented")


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
```

### 9.2 Função de domínio (service layer)

```python
# src/services/task_service.py
import boto3
from boto3.dynamodb.conditions import Key
from typing import Optional
from src.models.task import Task


class TaskService:
    def __init__(self, table_name: str, dynamodb_resource=None):
        self._dynamodb = dynamodb_resource or boto3.resource("dynamodb")
        self._table = self._dynamodb.Table(table_name)

    def get_task(self, task_id: str) -> Optional[Task]:
        response = self._table.get_item(Key={"task_id": task_id})
        item = response.get("Item")
        if not item:
            return None
        return Task(**item)

    def save_task(self, task: Task) -> None:
        self._table.put_item(Item=task.model_dump())
```

### 9.3 Teste unitário

```python
# tests/unit/test_task_service.py
import pytest
from unittest.mock import MagicMock, patch
from src.services.task_service import TaskService
from src.models.task import Task
from datetime import datetime, timezone


@pytest.fixture
def mock_table():
    return MagicMock()


@pytest.fixture
def task_service(mock_table):
    service = TaskService(table_name="tasks-table")
    service._table = mock_table
    return service


def test_get_task_returns_task_when_found(task_service, mock_table):
    task_id = "abc-123"
    mock_table.get_item.return_value = {
        "Item": {
            "task_id": task_id,
            "title": "Review PR",
            "description": None,
            "assignee_id": "user-1",
            "priority": "high",
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    }

    result = task_service.get_task(task_id)

    assert result is not None
    assert result.task_id == task_id
    mock_table.get_item.assert_called_once_with(Key={"task_id": task_id})


def test_get_task_returns_none_when_not_found(task_service, mock_table):
    mock_table.get_item.return_value = {}

    result = task_service.get_task("nonexistent-id")

    assert result is None
```

### 9.4 Teste de integração (com moto)

```python
# tests/integration/test_task_service_integration.py
import pytest
import boto3
from moto import mock_aws
from src.services.task_service import TaskService
from src.models.task import Task
from datetime import datetime, timezone


@pytest.fixture
def aws_credentials(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture
def dynamodb_table(aws_credentials):
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="tasks-table",
            KeySchema=[{"AttributeName": "task_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "task_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield table


@mock_aws
def test_save_and_retrieve_task(dynamodb_table, aws_credentials):
    service = TaskService(table_name="tasks-table")
    now = datetime.now(timezone.utc).isoformat()

    task = Task(
        task_id="test-task-1",
        title="Build API",
        description="Implement endpoints",
        assignee_id="user-42",
        priority="high",
        status="pending",
        created_at=now,
        updated_at=now,
    )

    service.save_task(task)
    retrieved = service.get_task("test-task-1")

    assert retrieved is not None
    assert retrieved.title == "Build API"
    assert retrieved.priority == "high"
```

### 9.5 Módulo Terraform (exemplo: Lambda)

```hcl
# modules/lambda/main.tf
module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 7.0"

  function_name = "${var.project_name}-${var.function_name}-${var.environment}"
  description   = var.description
  handler       = var.handler
  runtime       = "python3.13"
  timeout       = var.timeout
  memory_size   = var.memory_size

  source_path = var.source_path

  environment_variables = var.environment_variables

  attach_policy_statements = true
  policy_statements        = var.policy_statements

  tags = local.common_tags
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
```

```hcl
# modules/lambda/variables.tf
variable "project_name" {
  type        = string
  description = "Nome do projeto"
}

variable "function_name" {
  type        = string
  description = "Nome identificador da função Lambda"
}

variable "environment" {
  type        = string
  description = "Ambiente de deploy (dev, staging, prod)"
}

variable "description" {
  type    = string
  default = ""
}

variable "handler" {
  type    = string
  default = "handler.handler"
}

variable "timeout" {
  type    = number
  default = 30
}

variable "memory_size" {
  type    = number
  default = 256
}

variable "source_path" {
  type        = string
  description = "Caminho para o código fonte da Lambda"
}

variable "environment_variables" {
  type    = map(string)
  default = {}
}

variable "policy_statements" {
  type    = any
  default = {}
}
```

---

## 10. Estrutura de Diretórios Recomendada

```
.
├── src/
│   ├── handlers/          # Entrypoints Lambda (um por domínio)
│   ├── services/          # Lógica de negócio
│   ├── repositories/      # Acesso a dados (DynamoDB)
│   ├── models/            # Modelos Pydantic
│   └── utils/             # Helpers (email, logging, etc.)
├── tests/
│   ├── unit/              # Testes unitários
│   └── integration/       # Testes de integração com moto
├── infra/
│   ├── modules/           # Módulos Terraform reutilizáveis
│   └── environments/      # tfvars por ambiente
├── requirements.txt
├── requirements-dev.txt   # pytest, moto, pytest-cov, etc.
├── .github/
│   └── workflows/
│       └── ci.yml         # GitHub Actions — lint + test
└── tech-env.md
```

---

## 11. CI/CD — GitHub Actions

```yaml
# .github/workflows/ci.yml (referência mínima)
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov=src --cov-fail-under=85 --cov-report=term-missing
```

---

## Open Questions (a resolver antes de Construction)

| # | Pergunta | Dono |
|---|----------|------|
| 1 | Campos exatos de uma tarefa: título, descrição, prioridade, status, datas de criação/vencimento? | Equipe |
| 2 | Formato do relatório semanal: quais métricas, comparativo com semana anterior? | Equipe |
| 3 | Região AWS e estrutura de contas (dedicada ou compartilhada)? | Equipe |
| 4 | DynamoDB lock para Terraform state (S3 apenas ou adicionar DynamoDB lock table)? | Equipe |
| 5 | Quais opções de tema visual estarão disponíveis na v1 do frontend? | Equipe |

---

*Documento gerado via `/tech-env` skill — AI-DLC input para Construction.*
