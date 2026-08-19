# Security Test Instructions — Task Manager API

## Scope (devsecops perspective)

Testes de segurança focados nos vetores de ataque relevantes para a v1: JWT manipulation, input injection, CORS, e rate limiting.

## Static Analysis (SAST)

```bash
# Bandit — análise de segurança estática Python
pip install bandit
bandit -r src/ -ll

# Ruff com regras de segurança
ruff check src/ --select S  # S = flake8-bandit rules
```

## Auth / JWT Testing

Cenários a validar manualmente (sem automação na v1):

1. **Token ausente:** `GET /v1/tasks` sem header `Authorization` → deve retornar 401
2. **Token inválido:** Header com string aleatória → deve retornar 401
3. **Token expirado:** JWT com `exp` no passado → deve retornar 401
4. **Token de outra região:** JWT com `iss` apontando para pool diferente → deve retornar 401
5. **Token válido:** JWT correto do Cognito → deve retornar 200

## Input Validation

Todos os inputs são validados via Pydantic v2 antes de qualquer processamento. Casos de borda:

```bash
# Payload com campos extras (deve ser ignorado ou rejeitado)
curl -X POST /v1/tasks -d '{"title": "Test", "sql_injection": "DROP TABLE tasks"}'

# Campo além do limite de tamanho
curl -X POST /v1/tasks -d '{"title": "'"$(python3 -c 'print("A"*201)')"'"}'
# Deve retornar 400 Bad Request
```

## Secrets Check

```bash
# Verificar que não há credenciais hardcoded
grep -rn "password\|secret\|api_key\|aws_access\|AKIA" src/ --include="*.py" | grep -v "#\|test"

# Detectar .env commitado acidentalmente
git log --all --full-history -- "**/.env"
```

## SES Sandbox

- **Ação imediata:** Solicitar saída do SES sandbox no dia 1 do deploy
- Sem a saída do sandbox, apenas emails verificados recebem notificações
- Aprovação AWS leva 24-48h

## CORS (API Gateway)

Verificar no console AWS após deploy:
- Origin permitida: domínio do CloudFront (`https://xxxx.cloudfront.net`)
- Headers: `Authorization`, `Content-Type`
- Methods: `GET, POST, PUT, DELETE, OPTIONS`
