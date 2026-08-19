# Unit Test Instructions — Task Manager API

## Test Framework

- **Framework:** pytest 8.x
- **Coverage:** pytest-cov
- **AWS Mocking:** moto (mock_aws decorator)
- **HTTP client:** httpx (para testes de integração)
- **Time control:** freezegun

## How to Run Tests

### Exact unit-scoped command (antes do primeiro ciclo de testes):

```bash
# Instalar dependências
pip install -r requirements.txt -r requirements-dev.txt

# Rodar todos os testes desta unit com cobertura
pytest tests/ --cov=src --cov-fail-under=85 --cov-report=term-missing -v

# Rodar apenas unit tests
pytest tests/unit/ -v

# Rodar apenas integration tests
pytest tests/integration/ -v

# Rodar um arquivo específico
pytest tests/unit/test_task_service.py -v
```

## Coverage Target

- **Mínimo:** 85% de cobertura de linhas (configurado no CI)
- **Abordagem:** Standard strategy — 5-8 testes por componente

## Test Structure

```
tests/
├── unit/                          # Testes unitários com mocks
│   ├── test_models.py             # Validação Pydantic (5-8 testes)
│   ├── test_task_service.py       # TaskService com mocks (5-8 testes)
│   ├── test_notification_service.py  # NotificationService (3-5 testes)
│   ├── test_report_service.py     # ReportService (3-5 testes)
│   ├── test_tasks_handler.py      # Lambda handler tasks (6-8 testes)
│   ├── test_users_handler.py      # Lambda handler users (3-5 testes)
│   └── test_report_handler.py     # Lambda handler report (3-5 testes)
└── integration/                   # Testes de integração com moto
    ├── test_task_repository.py    # TaskRepository + DynamoDB mock (5-8 testes)
    └── test_user_repository.py    # UserRepository + DynamoDB mock (3-5 testes)
```

## Mocking Strategy

### AWS Services (moto)

```python
import pytest
import boto3
from moto import mock_aws

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
```

### Unit Test Mocking

```python
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_task_repo():
    return MagicMock()

@pytest.fixture
def task_service(mock_task_repo):
    service = TaskService()
    service._repository = mock_task_repo
    return service
```

## Environment Variables for Tests

```bash
export TABLE_NAME_TASKS="tasks-table"
export TABLE_NAME_USERS="users-table"
export COGNITO_USER_POOL_ID="us-east-1_test"
export SES_FROM_EMAIL="noreply@test.com"
export AWS_DEFAULT_REGION="us-east-1"
```

## Test Data Management

- Fixtures do pytest para criar dados de teste consistentes
- `freezegun` para controlar timestamps em testes que dependem de `datetime.now()`
- Cada teste de integração usa o decorator `@mock_aws` para isolar o estado AWS
