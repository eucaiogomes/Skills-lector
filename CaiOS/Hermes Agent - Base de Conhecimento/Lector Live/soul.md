# soul.md

## Papel deste arquivo

Este arquivo resume a alma operacional dos agentes Lector e destaca os aprendizados mais recentes.

A versão canônica e detalhada continua em:

- [[06 - Soul do Agente]]

## Aprendizado novo — avaliações e questões

O fluxo de avaliações do Lector agora está separado em skills e agentes especializados:

### Skills

- `lector-criar-questoes-api`
- `lector-criar-avaliacoes-api`
- `lector-validar-avaliacoes-api`
- `lector-agentes-avaliacoes`
- `lector-avaliacoes-e-questoes` (guarda-chuva)
- `lector-criar-avaliacao-completa` (ponta a ponta)

### Agentes

- KB / Curadoria
- Questões
- Montagem da avaliação
- Validação

## Como deve funcionar da próxima vez

1. consultar a base Obsidian;
2. consultar a Soul do Agente;
3. definir título editorial e objetivo;
4. criar ou selecionar questões;
5. montar a avaliação;
6. validar por GET e por listagem;
7. devolver ID, status e resumo real ao usuário;
8. registrar qualquer novo aprendizado.

## Regras fixas

- não salvar credenciais;
- não inventar sucesso sem validação real;
- não usar título genérico de teste em entregas de produção;
- cada erro novo deve virar documentação e skill reutilizável.
