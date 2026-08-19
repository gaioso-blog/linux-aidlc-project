# Build Instructions — Task Manager API

## Upstream Artifacts

- `construction/task-manager-api/code-generation/code-generation-plan.md`
- `construction/task-manager-api/code-generation/unit-test-instructions.md`
- `construction/task-manager-api/code-generation/code-summary.md`

## Prerequisites

- Python 3.13+ (ambiente Lambda usa `python3.13`; ambiente local usa 3.13 ou 3.14)
- pip 24+
- AWS CLI configurado (para deploy; não necessário para testes locais)
- Terraform 1.6+ (para IaC)

## Environment Setup

```bash
# 1. Clonar e entrar no projeto
cd /path/to/linux-aidlc-project

# 2. Criar e ativar virtualenv (recomendado)
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependências de produção
pip install --prefer-binary -r requirements.txt

# 4. Instalar dependências de desenvolvimento
pip install --prefer-binary -r requirements-dev.txt

# 5. Configurar variáveis de ambiente (copiar o exemplo)
cp .env.example .env
# Editar .env com os valores reais do ambiente AWS
```

## Variáveis de Ambiente Necessárias

```bash
export TABLE_NAME_TASKS="task-manager-tasks-dev"
export TABLE_NAME_USERS="task-manager-users-dev"
export COGNITO_USER_POOL_ID="us-east-1_XXXXXXXXX"
export COGNITO_APP_CLIENT_ID="xxxxxxxxxxxxxxxxxxxxxxxxxx"
export SES_FROM_EMAIL="noreply@yourdomain.com"
export SES_REGION="us-east-1"
export AWS_DEFAULT_REGION="us-east-1"
export POWERTOOLS_SERVICE_NAME="task-manager"
export LOG_LEVEL="INFO"
```

## Build Verification

```bash
# Verificar imports sem erros
python3 -c "from src.handlers.tasks_handler import handler; print('OK')"
python3 -c "from src.handlers.report_handler import handler; print('OK')"
python3 -c "from src.handlers.users_handler import handler; print('OK')"

# Lint
ruff check src/ tests/

# Format check
black --check src/ tests/
```

## Troubleshooting

| Erro | Solução |
|------|---------|
| `pydantic-core` build failure | `pip install --prefer-binary pydantic` |
| `maturin not found` | `pip install maturin` antes de instalar pydantic |
| `ModuleNotFoundError: src` | Executar `pytest` da raiz do projeto (não de subdiretórios) |
| `aws-xray-sdk` missing | `pip install aws-xray-sdk` (dependência transitiva do powertools Tracer) |
