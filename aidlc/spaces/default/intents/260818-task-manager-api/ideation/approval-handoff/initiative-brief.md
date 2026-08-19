# Initiative Brief — Task Manager API (v1)
<!-- confirmed: Looks correct - prosseguir para o portao de aprovacao -->

## Problema e Intent

A equipe interna de 20-30 arquitetos e desenvolvedores usa o Trello para gestão de tarefas, mas a ferramenta não oferece notificações confiáveis, relatórios automáticos, nem customização real. Resultado: 20-30 notificações perdidas por semana e até 5 dias gastos manualmente para compilar um relatório de progresso.

**Objetivo:** Entregar uma API serverless de gestão de tarefas com frontend funcional, autenticação, notificações e relatório semanal automático — rodando na AWS — em 1-2 dias.

Fontes: `ideation/intent-capture/intent-statement.md`, `ideation/intent-capture/stakeholder-map.md`, `vision.md`, `tech-env.md`

## Escopo da v1

**In Scope:**
- CRUD completo de tarefas (título, descrição, status, prioridade, responsável, due_date, estimativa de esforço)
- Autenticação via Amazon Cognito (provisionamento manual pelo admin)
- Notificações por email (SES) ao atribuir tarefa
- Relatório semanal automático toda sexta (EventBridge + SES): tarefas por status por pessoa + total backlog
- Frontend funcional (S3+CloudFront) — interface CRUD similar ao Trello
- IaC com Terraform, CI/CD com GitHub Actions

**Out of Scope:**
- App mobile, integrações externas, dashboard em tempo real, notificações push, webhooks

## Validação de Feasibility

- **Stack:** Python 3.13 + AWS Lambda + API Gateway + DynamoDB + Cognito + SES + EventBridge + S3+CloudFront + Terraform — equipe experiente com a stack
- **Custo:** Negligível para ~30 usuários internos no modelo serverless pay-per-use
- **Compliance:** Nenhum requisito especial — uso interno
- **Tech-env:** Completo — bibliotecas, padrões de código, exemplos canônicos e pipeline CI definidos em `tech-env.md`

## Riscos e Mitigações

| Risco | Severidade | Mitigação | Status |
|-------|-----------|-----------|--------|
| SES sandbox — aprovação de saída leva 24-48h | Alto | Solicitar saída do sandbox **imediatamente no dia 1** | Reconhecido — ação imediata necessária |
| Timeline de 1-2 dias | Médio | Escopo v1 enxuto e bem definido; equipe experiente | Mitigado por design |

## Stakeholders

| Stakeholder | Papel | Interesse |
|-------------|-------|-----------|
| Equipe dev/arquitetos (20-30) | Usuários finais | Ferramenta funcional, notificações confiáveis |
| Admin técnico | Decisor operacional | Provisionamento de usuários, infra estável |
| Liderança técnica | Influenciador | Visibilidade do progresso via relatório semanal |

## Plano de Construção

**Scope:** `task-manager-api` (custom) — 11 etapas, Standard depth

**Etapas restantes após aprovação:**
1. Code Generation — Lambda handlers (tasks, users, reports), DynamoDB, SES, EventBridge, Terraform, frontend
2. Build and Test — pytest, moto, cobertura ≥ 85%
3. CI Pipeline — GitHub Actions
4. Deployment Pipeline — pipeline de deploy completo
5. Environment Provisioning — Terraform apply na conta dedicada (us-east-1)
6. Deployment Execution — deploy na AWS + smoke test

## Métricas de Sucesso

| Métrica | Baseline | Target |
|---------|----------|--------|
| Tempo para relatório semanal | 5 dias | < 1 minuto |
| Notificações perdidas/semana | 20-30 | 0 |
| Adoção da equipe | 0% | 100% em 2 semanas |

## Recomendação

**GO** — todos os stakeholders alinhados, escopo aprovado, riscos reconhecidos e mitigados, stack completamente definida. Iniciar Code Generation imediatamente.

## Assumptions & Open Questions

- [assumption] Frontend tech (HTML/JS/framework) a ser definida em Code Generation
- [assumption] Saída do SES sandbox será solicitada no início da construção
- [assumption] Região us-east-1, conta AWS dedicada
