# Avaliações e Questões via API — Lector Live

## Objetivo

Esta nota registra o fluxo operacional validado para criar, listar e validar **questões** e **avaliações** no Lector Live via API autenticada por cookies de sessão.

Ela complementa as skills Hermes especializadas e concentra o que foi aprendido no caso real da avaliação de LGPD.

## O que foi validado de verdade

### Questões

#### Leitura de questão existente

Endpoint funcional:

```text
GET /lector-web-service/quiz/question/{question_id}
```

Exemplo real validado:

- questão `138045`
- HTTP `200`
- nome: `LGPD 2026 - Teste Base legal`

#### Rota inválida para leitura

A rota abaixo **não deve ser usada** para leitura:

```text
GET /lector-web-service/quiz/question/9/{question_id}
```

Retorno observado:

- HTTP `405 Method Not Allowed`

#### Criação de questão

Endpoint observado para criação:

```text
POST /lector-web-service/quiz/question/9
```

Tipos vistos na prática:

- `SimpleChoiceQuestion`
- `MultiChoiceQuestion`
- `TrueFalseQuestion`
- `DiscursiveQuestion`
- `AssociativeQuestion`
- `ScaleQuestion`
- `LikertQuestion`
- `ClassificativeQuestion`
- `ClozeQuestion`
- `SimpleTextQuestion`

## Avaliações

### Criação de avaliação

Endpoint funcional:

```text
POST /lector-web-service/quiz/evaluation/9
```

Tipo validado:

```text
BasicEvaluation
```

### Validação direta da avaliação criada

```text
GET /lector-web-service/quiz/evaluation/{evaluation_id}
```

Campos mínimos para conferir:

- `name.pt_BR`
- `minPercentage`
- `questions` (quantidade)
- `active`

### Validação por listagem

Endpoint histórico:

```text
POST /lector-web-service/report/evaluationsList?categoryId=0
```

Fallback validado quando o endpoint de relatório retornar `500`:

```text
GET /lector-web-service/quiz/evaluation/list/9?limit=20&titlePart={termo}&type=0
```

Essa etapa confirma se a avaliação realmente aparece na listagem recente do portal. Observação: o fallback pode retornar a avaliação sem expandir `questions`; confirme a quantidade real por `GET /quiz/evaluation/{id}`.

## Caso real validado — LGPD

### Avaliação criada

- ID: `43125`
- Nome: `LGPD na prática: governança, dados pessoais e resposta a incidentes`
- Tipo: `BasicEvaluation`
- Questões: `10`
- Nota mínima: `75`
- Ativa: `true`

### Questões vinculadas

- `138045`
- `138046`
- `138047`
- `138048`
- `138049`
- `138050`
- `138051`
- `138052`
- `138053`
- `138054`

### Validações executadas

- criação da avaliação com retorno HTTP `200`
- leitura posterior da avaliação com HTTP `200`
- presença confirmada na listagem recente de avaliações
- teste manual do usuário no portal com retorno positivo: **"deu tudo certo"**

## Estrutura prática do payload de avaliação

Campos usados com sucesso:

- `@class: BasicEvaluation`
- `type: BasicEvaluation`
- `account.id: 9`
- `name.pt_BR`
- `description.pt_BR`
- `header.pt_BR`
- `questions`
- `categories: []`
- `questionsPerPage: 1`
- `active: true`
- `minPercentage: 75`
- `tags`
- `thumbImage: "######"`
- `dimensions: []`
- `thumbs.square/banner/cover: null`
- `suggestions: []`

## Skills criadas para esse fluxo

- `lector-criar-questoes-api`
- `lector-criar-avaliacoes-api`
- `lector-validar-avaliacoes-api`
- `lector-agentes-avaliacoes`
- `lector-avaliacoes-e-questoes` (guarda-chuva)

## Ordem recomendada daqui para frente

1. consultar a base Obsidian e a Soul do Agente;
2. definir título editorial, descrição e objetivo da avaliação;
3. criar ou selecionar questões;
4. montar a avaliação;
5. validar por leitura direta;
6. validar por listagem;
7. registrar qualquer novo aprendizado.

## Regras fixas

- nunca salvar cookies, tokens ou dados sensíveis em notas ou skills;
- nunca confiar só no POST de criação;
- sempre devolver IDs reais ao usuário;
- usar nome editorial, sem cara de teste, quando o pedido já for de produção.
