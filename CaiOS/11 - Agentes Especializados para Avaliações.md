# Agentes Especializados para Avaliações

## Objetivo

Esta nota define a separação operacional dos agentes para o fluxo de avaliações do Lector Live, de forma que pedidos futuros possam ser executados com mais rapidez, clareza e rastreabilidade.

## Estrutura recomendada

### 1. Agente KB / Curadoria

**Responsabilidade:** entender o contexto e preparar o pacote editorial da avaliação.

**Entradas:**
- tema do usuário;
- base Obsidian;
- skills Lector já existentes.

**Saídas esperadas:**
- título editorial da avaliação;
- descrição;
- cabeçalho em HTML simples;
- objetivo de aprendizagem;
- nota mínima sugerida;
- critérios de cobertura.

**Skill principal:**
- `lector-base-conhecimento-obsidian`
- apoio: `lector-kb-search`

---

### 2. Agente de Questões

**Responsabilidade:** criar ou selecionar questões adequadas.

**Entradas:**
- pacote editorial do agente de curadoria;
- critérios de cobertura;
- exemplos existentes no banco do Lector.

**Saídas esperadas:**
- lista de IDs das questões;
- tipo de cada questão;
- nome de cada questão;
- observação de cobertura.

**Skill principal:**
- `lector-criar-questoes-api`

---

### 3. Agente Montador de Avaliação

**Responsabilidade:** montar o payload final e criar a avaliação.

**Entradas:**
- título/descritivo/cabeçalho;
- IDs das questões já validados.

**Saídas esperadas:**
- payload final resumido;
- ID da avaliação criada;
- nome final persistido.

**Skill principal:**
- `lector-criar-avaliacoes-api`

---

### 4. Agente Validador

**Responsabilidade:** confirmar tecnicamente que o Lector persistiu e listou o recurso criado.

**Entradas:**
- ID da avaliação;
- nome esperado.

**Saídas esperadas:**
- HTTP status da leitura direta;
- nome final;
- quantidade de questões;
- nota mínima;
- status ativo;
- confirmação de presença na listagem recente.

**Skill principal:**
- `lector-validar-avaliacoes-api`

---

## Skills de orquestração

Para fluxo completo com visão geral, usar:

- `lector-avaliacoes-e-questoes`

Para execução mais rápida ponta a ponta, usar:

- `lector-criar-avaliacao-completa`

Para divisão em agentes, usar:

- `lector-agentes-avaliacoes`

## Templates já salvos

No skill `lector-agentes-avaliacoes`, foram criados templates para:

- `templates/agente-kb-curadoria.md`
- `templates/agente-questoes.md`
- `templates/agente-montagem-avaliacao.md`
- `templates/agente-validacao.md`

## Ordem operacional recomendada

1. Curadoria
2. Questões
3. Montagem da avaliação
4. Validação

## Critério de qualidade por agente

Cada agente deve devolver **artefatos verificáveis**:

- curadoria → título, descrição, cabeçalho, objetivos;
- questões → IDs reais;
- montagem → ID da avaliação criada;
- validação → status HTTP + presença na listagem.

## Caso validado que originou esta estrutura

### Tema

LGPD

### Resultado

- avaliação criada com ID `43125`
- avaliação validada por API
- avaliação validada pelo usuário no portal

Essa estrutura foi derivada de um fluxo que funcionou de verdade, não de um modelo teórico.
