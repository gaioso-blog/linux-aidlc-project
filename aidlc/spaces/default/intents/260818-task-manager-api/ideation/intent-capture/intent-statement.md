# Intent Statement — Task Manager API
<!-- confirmed: Looks correct -->

## Problem Statement

Hoje a equipe de 20-30 arquitetos e desenvolvedores usa o Trello para gerenciar tarefas, mas a ferramenta não oferece notificações personalizadas, relatórios semanais automáticos, nem customização visual real. Tarefas atribuídas passam despercebidas (20-30 notificações perdidas por semana) e gerar um relatório de progresso consome até 5 dias de trabalho manual. [desc] [Q1]

## Target Customer

Equipe interna de 20-30 arquitetos e desenvolvedores de uma mesma empresa. Não há usuários externos. O uso é exclusivamente interno, sem requisitos de compliance. [desc] [Q2]

**Dor principal:** visibilidade fragmentada do progresso das tarefas e ausência de automação para notificações e relatórios de acompanhamento. [desc]

## Success Metrics

| Métrica | Baseline | Target | Critério de medição |
|---------|----------|--------|---------------------|
| Tempo para gerar relatório semanal | 5 dias (manual) | < 1 minuto | Relatório automático via EventBridge toda sexta |
| Notificações perdidas por semana | 20-30 | 0 | Pesquisa quinzenal com o time |
| Adoção pela equipe | 0% | 100% em 2 semanas pós-lançamento | Contagem de usuários ativos |

[desc]

## Initiative Trigger

A equipe já tem experiência com serverless AWS e custo operacional baixíssimo para ~30 usuários. O Trello e alternativas SaaS não oferecem controle suficiente sobre customizações. A decisão de construir a própria ferramenta foi tomada internamente, sem pressão regulatória ou de mercado externo. [desc]

## Scope — v1

**In Scope:** [Q1]
- CRUD completo de tarefas (criar, ler, atualizar, deletar)
- Campos de tarefa: título, descrição, status (pending/in_progress/done), prioridade (low/medium/high), responsável (assignee), data de criação, data de atualização, data de vencimento (due_date), estimativa de esforço (story points ou horas) [Q3]
- Autenticação de usuários via Amazon Cognito — provisionamento manual pelo admin no console AWS [Q2]
- Atribuição de tarefas a membros da equipe
- Notificações por email ao atribuir tarefa (Amazon SES)
- Relatório semanal automático toda sexta (EventBridge Scheduler + SES): tarefas por status por pessoa (pending, in_progress, done) + total do backlog [Q4]
- Frontend funcional hospedado em S3+CloudFront com interface de CRUD de tarefas similar ao Trello [Q5]
- Temas visuais customizáveis no frontend

**Out of Scope (v1):**
- App mobile nativo
- Integrações com Slack ou outras ferramentas
- Dashboard em tempo real
- Notificações push
- Webhooks para sistemas externos
- Auto-registro de usuários (provisionamento sempre via admin) [Q2]

## Initial Scope Signal

- **Workflow-selected scope:** `task-manager-api` [scope]
- **User-confirmed product boundary:** API serverless de gestão de tarefas com frontend funcional (S3+CloudFront), autenticação Cognito, notificações SES e relatório semanal — uso interno para equipe de 20-30 pessoas. [Q1] [Q5]

## Assumptions & Open Questions

- [assumption] O frontend será desenvolvido com tecnologia web padrão (HTML/CSS/JS ou framework leve) hospedado no S3+CloudFront — tecnologia exata a ser definida em Code Generation.
- [assumption] "Story points ou horas" como estimativa de esforço: o campo aceita valor numérico com uma unidade configurável pelo usuário ou pela organização — a definição exata da unidade fica para o design de dados.
- [assumption] O relatório semanal será enviado por email para todos os membros da equipe cadastrados no Cognito.


## Review

**Verdict:** READY
**Reviewer:** aidlc-product-lead-agent
**Date:** 2026-08-18T20:57:40Z
**Iteration:** 1

### Findings

| # | Severity | Local | Finding | Recomendação |
|---|----------|-------|---------|--------------|
| 1 | Major | Success Metrics — linha "Adoção pela equipe" | A métrica "100% em 2 semanas" carrega `[desc]`, mas a fonte registrada em `[desc]` é a descrição inicial do projeto, que não contém essa métrica. O `vision.md` (de onde provavelmente vem esse dado) não está no Sources register, portanto a claim não é resolvível contra nenhuma fonte permitida. | Mover para `## Assumptions & Open Questions` com `[assumption]` até que a métrica seja confirmada via pergunta follow-up, ou registrar `vision.md` como fonte adicional se ele for tratado como entrada oficial do stage. |
| 2 | Major | Scope — "Frontend funcional... similar ao Trello" | A resposta ao Q5 usa a opção X com a descrição "similar ao Trello", que é uma afirmação de produto com expectativa de fidelidade sem critério testável. O que conta como "similar ao Trello"? Boards? Drag-and-drop de cards? Colunas de kanban? Sem um escopo de funcionalidade mínima do frontend definido, os próximos stages de design e code generation trabalharão com uma âncora vaga, o que gera risco alto de retrabalho. | Adicionar em `## Assumptions & Open Questions` uma assumption explícita listando as features de interface mínimas que caracterizam "similar ao Trello" para fins desta v1 (ex: lista de tarefas com filtros por status/responsável, drag-and-drop, sem timeline/calendar). A definição exata pode ser fechada em Rough Mockups, mas o limite mínimo precisa estar registrado aqui. |
| 3 | Minor | Scope — seção Out of Scope | As 5 primeiras linhas da seção Out of Scope (mobile nativo, integrações Slack, dashboard em tempo real, notificações push, webhooks) não carregam tag de fonte. A regra de grounding do stage exige tag em todo bloco substantivo. | Adicionar `[Q1]` a cada linha de Out of Scope que foi excluída pela resposta ao Q1 (o escopo confirmado em Q1 exclui implicitamente essas features; a tag formaliza o rastreio). |
| 4 | Minor | Scope In — "Temas visuais customizáveis no frontend" | Essa linha aparece em In Scope sem tag de fonte. A resposta Q5-X não menciona temas. O `vision.md` menciona temas, mas não está no Sources register. | Mover para `## Assumptions & Open Questions` com `[assumption]` até confirmação, ou remover da lista de in scope se não foi explicitamente confirmado pelo usuário neste workflow. |

### Summary

Os artefatos estão bem estruturados, todas as seções obrigatórias estão presentes, e a esmagadora maioria dos claims tem rastreabilidade correta. Os dois findings Major não bloqueiam o início do próximo stage — são gaps que, se não endereçados aqui, vão reaparecer como perguntas no design e na geração de código. A aprovação com esses findings registrados é defensável; o humano no gate deve decidir se quer fechar a definição do frontend antes de avançar ou aceitar o risco de retrabalho.
