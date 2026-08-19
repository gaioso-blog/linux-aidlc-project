# Intent Capture — Questions

## Sources

- [desc] Initial description: "API serverless de gestão de gestão de tarefas rodando na AWS com Terraform e CI/CD pipeline completo. vision.md e tech-env.md já prontos."
- [scope] Workflow-selected scope: `task-manager-api`.
- [memory:M1] `aidlc/spaces/default/memory/org.md#Way of Working`: "We use trunk-based development. All work merges to main via short-lived feature branches (typically resolved within 1-2 days)."
- [memory:M2] `aidlc/spaces/default/memory/org.md#Testing Posture`: "We treat tests as a first-class deliverable in every Bolt."

---

## Q1. Confirmação de escopo e fronteira do produto

O `vision.md` define o escopo da v1 como API serverless com CRUD de tarefas, autenticação Cognito, notificações SES e relatório semanal via EventBridge. Este workflow cobre exatamente esse escopo — sem mobile, sem Slack, sem dashboard em tempo real.

Isso está correto?

A. Sim, o escopo do `vision.md` está correto e completo para esta corrida
B. Quero ajustar o escopo — há algo a adicionar ou remover
C. Quero focar em apenas parte do escopo nesta corrida (ex: só a API, sem frontend)
X. Outro (especificar)

[Answer]: A. Sim, o escopo do `vision.md` está correto e completo para esta corrida. Observação: o frontend é necessário (S3+CloudFront) para acesso ao CRUD de tarefas com funcionalidades similares ao Trello.

---

## Q2. Usuários e acesso inicial

O `vision.md` menciona 20-30 arquitetos e desenvolvedores da mesma empresa. Como esses usuários serão provisionados no Cognito na v1?

A. Criação manual de usuários pelo admin no console AWS (sem auto-registro)
B. Auto-registro com email corporativo (domínio da empresa)
C. SSO/SAML federado com o diretório da empresa (ex: Azure AD, Okta)
D. Importação em lote via script (lista de emails pré-definida)
X. Outro (especificar)

[Answer]: A. Criação manual de usuários pelo admin no console AWS (sem auto-registro)

---

## Q3. Campos de uma tarefa

O `vision.md` deixa em aberto a estrutura exata dos campos. Para a v1, uma tarefa deve ter:

A. Campos básicos: título, descrição, status (pending/in_progress/done), prioridade (low/medium/high), responsável (assignee), data de criação, data de atualização
B. Campos básicos + data de vencimento (due_date)
C. Campos básicos + data de vencimento + estimativa de esforço (story points ou horas)
D. Campos básicos + tags/labels personalizáveis
X. Outro (especificar — liste os campos desejados)

[Answer]: C. Campos básicos + data de vencimento + estimativa de esforço (story points ou horas)

---

## Q4. Relatório semanal — conteúdo

O `vision.md` descreve o relatório de sexta: quem está em dia, quem precisa de apoio, quem está avançado, e status do backlog. Quais métricas devem constar?

A. Tarefas por status por pessoa (pending, in_progress, done) + total do backlog
B. Opção A + tarefas atrasadas (vencidas sem conclusão)
C. Opção B + comparativo com semana anterior (variação de tarefas concluídas)
D. Apenas um resumo executivo: total concluído, total pendente, total atrasado — sem breakdown por pessoa
X. Outro (especificar)

[Answer]: A. Tarefas por status por pessoa (pending, in_progress, done) + total do backlog

---

## Q5. Frontend — escopo desta corrida

O `vision.md` inclui "temas visuais customizáveis no frontend" e "S3 + CloudFront". Para o prazo de 1-2 dias, como tratamos o frontend?

A. Frontend fora desta corrida — entregamos só a API + infra; o frontend fica para depois
B. Frontend estático mínimo (HTML/JS puro) já hospedado no S3+CloudFront, sem temas ainda
C. Frontend React/Vue básico com suporte a temas (light/dark) hospedado no S3+CloudFront
X. Outro (especificar)

[Answer]: X. Frontend funcional hospedado no S3+CloudFront com CRUD de tarefas completo (similar ao Trello), parte obrigatória do escopo v1.

---

## Assumption Confirmation

[Answer]: A. Accept assumptions

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
