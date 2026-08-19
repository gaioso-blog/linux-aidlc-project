# PRF — API Serverless de Gestão de Tarefas (Todo List)

## Problem (Problema)

### Today Statement

Hoje, arquitetos e desenvolvedores da equipe (20-30 pessoas) precisam gerenciar suas tarefas usando o Trello, que não oferece notificações personalizadas, customização visual real, nem relatórios semanais de progresso. A equipe precisa de uma ferramenta própria que se adapte ao seu fluxo de trabalho e forneça visibilidade sobre o avanço das atividades.

### How Might We

Como podemos criar uma ferramenta de gestão de tarefas própria que ofereça notificações personalizáveis, customização visual completa e relatórios semanais automáticos de progresso para a equipe de 20-30 devs/arquitetos?

### North Star

Entregar uma API serverless de gestão de tarefas com autenticação em **1 mês**, para reduzir o tempo de geração de relatórios semanais de **5 dias para minutos** (automático) e eliminar as **20-30 notificações perdidas por semana**, garantindo que a equipe tenha visibilidade total do progresso das atividades.

---

## Requirements (Requisitos)

### Target Users

- 20-30 arquitetos e desenvolvedores de uma mesma empresa
- Uso interno, sem usuários externos

### Use Case

**Nome:** API Serverless de Gestão de Tarefas com Autenticação

**Justificativa:** Equipe já tem experiência com serverless AWS, custo baixíssimo para ~30 usuários, e permite controle total sobre customizações que o Trello não oferece.

**Alternativas descartadas:**
- Continuar no Trello com Power-Ups — não atende as customizações desejadas
- Migrar para outra ferramenta SaaS — mesmo problema de falta de controle

### Success Vision

A equipe utiliza sua própria ferramenta de tarefas. Quando uma tarefa é criada e atribuída, o responsável recebe imediatamente um email com o link direto. Toda sexta-feira, um relatório automático chega por email mostrando quem está em dia, quem precisa de apoio, quem está avançado, e como o time está em relação ao backlog — sem ninguém gastar tempo compilando dados. Nenhuma atribuição passa despercebida, e a liderança técnica tem visibilidade real do progresso sem precisar perguntar.

### Success Metrics

| Métrica | Baseline (hoje) | Target | Como medir |
|---------|-----------------|--------|------------|
| Tempo para gerar relatório semanal | 5 dias (manual) | < 1 minuto (automático) | Relatório dispara automaticamente na sexta via EventBridge |
| Notificações perdidas por semana | 20-30 | 0 | Pesquisa quinzenal com o time |
| Adoção pela equipe | 0% | 100% em 2 semanas pós-lançamento | Contagem de usuários ativos |

### In Scope (v1)

- CRUD completo de tarefas (criar, ler, atualizar, deletar)
- Autenticação de usuários (Cognito)
- Atribuição de tarefas a membros da equipe
- Notificações por email ao atribuir tarefa (SES)
- Relatório semanal automático por email (EventBridge Scheduler + SES)
- Temas visuais customizáveis no frontend
- Frontend hospedado em S3 + CloudFront

### Out of Scope (v1)

- App mobile nativo
- Integrações com Slack ou outras ferramentas
- Dashboard em tempo real
- Notificações push
- Webhooks para sistemas externos

### Constraints

- Sem requisitos especiais de compliance ou segurança
- A equipe decide e executa (sem aprovações externas)

---

## Forward Plan (Plano)

### Technical Context

| Aspecto | Decisão |
|---------|---------|
| Tipo do projeto | Greenfield |
| Linguagem | Python |
| Compute | AWS Lambda |
| API | API Gateway (REST) |
| Database | DynamoDB |
| Autenticação | Amazon Cognito |
| Email | Amazon SES |
| Agendamento | EventBridge Scheduler |
| Frontend hosting | S3 + CloudFront |
| IaC | Terraform |
| Compliance | Nenhum requisito especial |

### Architecture Overview

```
[Frontend (S3 + CloudFront)]
        |
[API Gateway (REST)]
        |
[AWS Lambda (Python)]
        |
   +---------+---------+
   |         |         |
[DynamoDB] [SES]  [Cognito]
                      |
            [EventBridge Scheduler]
                      |
              [Lambda Relatório]
                      |
                    [SES]
```

### Risks

| Risco | Mitigação |
|-------|-----------|
| Limites do SES (sandbox) | Solicitar saída do sandbox no dia 1 do projeto — aprovação leva 24-48h |
| Timeline de 1 mês | Escopo da v1 enxuto e bem definido; equipe experiente com a stack |

### Stakeholders

- A própria equipe de arquitetos/devs (auto-organizada, sem aprovações externas)

### Open Questions

- Definir estrutura exata dos campos de uma tarefa (título, descrição, prioridade, status, datas?)
- Definir quais informações compõem o relatório semanal (formato, métricas, comparativo com semana anterior?)
- Definir quais opções de customização de tema estarão disponíveis na v1

---

## Technical Context Addendum

> A equipe deve finalizar um `tech-env.md` cobrindo: stack completa, bibliotecas permitidas/proibidas, padrões de código (ex: exemplo de endpoint Lambda, exemplo de teste, exemplo de módulo Terraform). Este PRF serve como ponto de partida para esse documento.

---

*Documento gerado via Working Backwards session — pronto para uso como input do AI-DLC.*