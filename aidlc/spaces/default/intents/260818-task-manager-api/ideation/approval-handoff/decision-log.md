# Decision Log — Ideation Phase
<!-- confirmed -->

## Decisões Tomadas

| # | Data | Decisão | Justificativa | Quem |
|---|------|---------|--------------|------|
| D1 | 2026-08-18 | Stack: Python 3.13 + AWS Lambda + API Gateway + DynamoDB + Cognito + SES + EventBridge + S3+CloudFront + Terraform | Equipe experiente com serverless AWS; custo mínimo para ~30 usuários; controle total sobre customizações | Equipe (via vision.md + tech-env.md) |
| D2 | 2026-08-18 | Escopo custom `task-manager-api` — 11 de 33 etapas | vision.md + tech-env.md já cobrem design, practices e requirements; intent ambiguity e structural uncertainty LOW | Plano aprovado pelo usuário |
| D3 | 2026-08-18 | Provisionamento de usuários Cognito: manual pelo admin | Sem necessidade de auto-registro para equipe interna de 20-30 pessoas | Q2 — intent-capture |
| D4 | 2026-08-18 | Campos de tarefa: básicos + due_date + estimativa de esforço (story points/horas) | Permite rastreamento de progresso e capacidade necessário para o relatório semanal | Q3 — intent-capture |
| D5 | 2026-08-18 | Relatório semanal: tarefas por status por pessoa + total backlog | Nível de detalhe suficiente para visibilidade sem overhead de comparativos semanais na v1 | Q4 — intent-capture |
| D6 | 2026-08-18 | Frontend obrigatório e funcional (similar ao Trello) hospedado em S3+CloudFront | Sem frontend funcional, o produto não é utilizável — CRUD de tarefas requer interface | Q1/Q5 — intent-capture |
| D7 | 2026-08-18 | Go/no-go: GO para Code Generation | Todos os stakeholders alinhados, riscos reconhecidos, stack definida | Q3 — approval-handoff |

## Decisões Adiadas

| # | Decisão | Motivo do adiamento | Prazo |
|---|---------|---------------------|-------|
| DA1 | Tecnologia do frontend (HTML/JS puro, React, Vue) | Definida em Code Generation com base no scope e timeline | Code Generation |
| DA2 | Unidade de estimativa de esforço (story points vs. horas) | Campo numérico aceita qualquer unidade — convenção da equipe | Code Generation |

## Assumptions & Open Questions

- [assumption] Saída do SES sandbox será solicitada no dia 1 da construção
- [assumption] Conta AWS dedicada em us-east-1 disponível para provisionar infraestrutura
