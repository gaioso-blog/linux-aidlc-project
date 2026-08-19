# Frontend Smoke Test — Task Manager SPA

> Testes manuais a serem executados após o deploy. Execute em modo anônimo para garantir estado limpo.

## Pré-requisitos
- Deploy concluído (S3 + CloudFront)
- Cognito User Pool configurado com ao menos 1 usuário de teste
- API Gateway apontando para as Lambdas corretas
- `window.APP_CONFIG` em `index.html` com as URLs corretas

---

## 1. Autenticação

| # | Cenário | Passos | Resultado esperado |
|---|---------|--------|--------------------|
| A-01 | Fluxo de login | Acesse a URL do CloudFront sem estar logado | Redirecionado para Cognito Hosted UI |
| A-02 | Login bem-sucedido | Informe credenciais válidas | Redirecionado de volta ao app, board visível, nome do usuário na topbar |
| A-03 | Logout | Clique em "Sair" | Redirecionado para Cognito logout, localStorage limpo |
| A-04 | Token expirado | Manipule `expires_at` no localStorage para o passado, recarregue | Redirecionado para login |

---

## 2. Board Kanban

| # | Cenário | Passos | Resultado esperado |
|---|---------|--------|--------------------|
| B-01 | Carregamento inicial | Após login | 3 colunas (Pendente, Em Andamento, Concluído) visíveis; contadores corretos |
| B-02 | Board vazio | Sem tarefas cadastradas | Colunas vazias, sem erro |
| B-03 | Cards exibidos | Tarefas existentes no DynamoDB | Cards aparecem na coluna correta com título, prioridade, responsável, prazo |
| B-04 | Badge de prioridade | Tarefa com prioridade "high" | Badge vermelho com texto "Alta" |

---

## 3. Criar Tarefa

| # | Cenário | Passos | Resultado esperado |
|---|---------|--------|--------------------|
| C-01 | Abrir modal | Clique em "+ Nova Tarefa" | Modal abre com título "Nova Tarefa", campos em branco |
| C-02 | Validação de título | Clique em "Salvar" sem preencher título | Mensagem de erro no campo título, foco no campo |
| C-03 | Criar tarefa mínima | Preencha apenas título, clique Salvar | Tarefa criada na coluna "Pendente", modal fecha, board atualiza |
| C-04 | Criar tarefa completa | Preencha todos os campos, clique Salvar | Tarefa criada com todos os dados visíveis no card |
| C-05 | Fechar modal — botão X | Clique no X | Modal fecha sem criar tarefa |
| C-06 | Fechar modal — Cancelar | Clique em Cancelar | Modal fecha sem criar tarefa |
| C-07 | Fechar modal — Escape | Pressione Escape | Modal fecha sem criar tarefa |
| C-08 | Fechar modal — backdrop | Clique fora do modal | Modal fecha sem criar tarefa |

---

## 4. Editar Tarefa

| # | Cenário | Passos | Resultado esperado |
|---|---------|--------|--------------------|
| E-01 | Abrir modal de edição | Clique em um card | Modal abre com dados da tarefa pré-preenchidos |
| E-02 | Alterar status | Mude status para "Em Andamento", Salvar | Tarefa move para coluna correta após fechar modal |
| E-03 | Alterar responsável | Mude assignee, Salvar | Card atualizado com novo responsável |
| E-04 | Limpar campo opcional | Remova due_date, Salvar | Card atualizado sem a data |

---

## 5. Drag-and-Drop

| # | Cenário | Passos | Resultado esperado |
|---|---------|--------|--------------------|
| D-01 | Mover para outra coluna | Arraste um card de "Pendente" para "Em Andamento" | Card aparece em "Em Andamento" após drop; contadores atualizados |
| D-02 | Visual durante drag | Segure o drag sobre uma coluna | Coluna destino recebe borda pontilhada azul |
| D-03 | Cancelar drag (tecla Escape) | Inicie drag, pressione Escape | Card retorna à posição original |

---

## 6. Temas

| # | Cenário | Passos | Resultado esperado |
|---|---------|--------|--------------------|
| T-01 | Alternar para dark mode | Clique no ícone 🌙 | Interface muda para tema escuro, ícone vira ☀️ |
| T-02 | Alternar de volta | Clique em ☀️ | Interface volta ao tema claro |
| T-03 | Persistência de tema | Mude para dark, recarregue a página | Tema dark mantido |

---

## 7. Responsividade

| # | Cenário | Passos | Resultado esperado |
|---|---------|--------|--------------------|
| R-01 | Mobile (375px) | Abra DevTools, defina 375px | Colunas empilhadas verticalmente; layout funcional |
| R-02 | Tablet (768px) | Defina 768px | Transição entre mobile e desktop |
| R-03 | Desktop (1280px+) | Resolução padrão | 3 colunas lado a lado |

---

## 8. Tratamento de Erros

| # | Cenário | Passos | Resultado esperado |
|---|---------|--------|--------------------|
| ER-01 | API indisponível | Desligue a Lambda, tente carregar | Error banner vermelho com mensagem de falha |
| ER-02 | Fechar error banner | Clique no ✕ do banner | Banner desaparece |

---

*Documento de testes manuais — v1. Sem framework automatizado de testes de frontend nesta versão.*
