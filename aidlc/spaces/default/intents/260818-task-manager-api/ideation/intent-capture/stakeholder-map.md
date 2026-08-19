# Stakeholder Map — Task Manager API
<!-- confirmed: Looks correct -->

## Stakeholders

| Stakeholder | Interesse principal | Autoridade | Fonte |
|-------------|--------------------|-----------:|-------|
| Equipe de devs/arquitetos (20-30 pessoas) | Ferramenta funcional de gestão de tarefas; visibilidade do próprio progresso; notificações confiáveis | Usuários finais — validam a adoção | [desc] [Q1] |
| Admin técnico (membro da equipe) | Provisionar usuários no Cognito; manter a infra rodando | Decisor operacional da ferramenta | [Q2] |
| Liderança técnica | Visibilidade do progresso do time sem precisar perguntar; relatório semanal automático | Beneficiário principal do relatório; influencia priorização | [desc] |

## Decision-Makers vs. Influencers

| Papel | Tipo | Observação | Fonte |
|-------|------|-----------|-------|
| Equipe auto-organizada | Decisor coletivo | Sem aprovações externas; a equipe decide e executa | [desc] |
| Admin técnico | Decisor operacional | Controla acesso e infra | [Q2] |
| Liderança técnica | Influenciador | Define o que entra no relatório semanal e valida adoção | [desc] |

## Communication Requirements

| Audiência | Canal | Cadência | Fonte |
|-----------|-------|----------|-------|
| Responsável por tarefa atribuída | Email via SES | Imediato na atribuição | [desc] |
| Toda a equipe | Email via SES (relatório semanal) | Toda sexta-feira automático via EventBridge | [desc] [Q4] |
| Admin técnico | Console AWS | Sob demanda (provisionamento de usuários) | [Q2] |

## Assumptions & Open Questions

- [assumption] Não há stakeholders externos (clientes, parceiros, reguladores) — uso estritamente interno.
- [assumption] A liderança técnica é parte da equipe de 20-30 pessoas e também usa a ferramenta como usuário final.
- [assumption] O endereço de email dos membros é o mesmo cadastrado no Cognito pelo admin, e é para esse endereço que as notificações SES serão enviadas.
