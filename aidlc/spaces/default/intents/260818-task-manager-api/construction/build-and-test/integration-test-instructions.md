# Integration Test Instructions — Task Manager API

## Overview

Testes de integração validam as fronteiras entre a lógica de negócio e os serviços AWS (DynamoDB, SES). Usam `moto` para simular os serviços sem chamadas reais à AWS.

## Test Framework

- **Framework:** pytest
- **AWS Mock:** moto (`@mock_aws`)
- **Scope:** repository layer + service layer com dependências reais (não mockadas)

## Como Executar

```bash
# Todos os testes de integração
pytest tests/integration/ -v

# Com cobertura
pytest tests/integration/ --cov=src/repositories --cov=src/services -v

# Arquivo específico
pytest tests/integration/test_task_repository.py -v
pytest tests/integration/test_user_repository.py -v
```

## Estrutura dos Testes

```
tests/integration/
├── conftest.py              # Fixtures: aws_credentials, dynamodb_tasks_table, dynamodb_users_table
├── test_task_repository.py  # 6 testes: create, get, update, delete, list_all, list_by_assignee
└── test_user_repository.py  # 3 testes: save, get_by_id, list_all
```

## Setup das Fixtures

```python
# Usar sempre @mock_aws nos testes de integração
from moto import mock_aws

@pytest.fixture
def aws_credentials(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("TABLE_NAME_TASKS", "test-tasks-table")
    monkeypatch.setenv("TABLE_NAME_USERS", "test-users-table")
```

## Coverage Target

- **Repositories:** ≥ 85% de cobertura
- **Services (com deps reais):** cobertos pelos testes de repository + unit tests dos services

## Pontos de Atenção

- Cada teste cria seu próprio estado DynamoDB — sem compartilhamento de estado entre testes
- `moto` simula o DynamoDB localmente — sem custo, sem AWS real necessária
- Para testar SES: `@mock_aws` também intercepta chamadas SES
