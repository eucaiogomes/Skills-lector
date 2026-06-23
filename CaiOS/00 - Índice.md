# Base de Conhecimento — Lector Live e Hermes Agent

Criado em: 2026-06-20 12:37:07 Hora oficial do Brasil

Esta pasta concentra o conhecimento operacional construído com o Hermes Agent para criar treinamentos no Lector Live, incluindo SCORM, turmas gratuitas, curadoria de nomes, imagens de capa, avaliações, questões e a personalidade operacional dos agentes.

## Como usar esta base

Antes de criar um novo treinamento ou avaliação no Lector, consultar esta base junto com as skills Hermes relacionadas.

Fluxo recomendado:

1. [[06 - Soul do Agente]] — postura e princípios de trabalho.
2. [[02 - Playbook Criar Treinamento Lector]] — fluxo completo de criação.
3. [[10 - Avaliações e Questões via API]] — criação e validação de questões e avaliações.
4. [[11 - Agentes Especializados para Avaliações]] — divisão por agentes e responsabilidades.
5. [[03 - SCORM e Conteúdo Didático]] — criação e importação de conteúdo SCORM.
6. [[05 - Imagens de Capa]] — criação e upload de capa.
7. [[04 - Turmas Gratuitas]] — criação e validação de turma gratuita.
8. [[07 - Agent Reach para Hermes]] — capacidades de busca/leitura adicionadas ao Hermes via Agent Reach.
9. [[08 - Pesquisa RH e Treinamento IA no RH]] — exemplo validado de pesquisa de tendências + SCORM.
10. [[09 - Treinamento com Vídeo e Hyperframes]] — fluxo de vídeo com narração usando Hyperframes (DocumentResource + .lmp4).
11. [[01 - Linha do Tempo da Sessão]] — histórico do que foi validado nesta sessão.
12. [[soul]] — resumo curto e operacional da alma do agente.

## Skill de execução mais rápida para avaliações

- `lector-criar-avaliacao-completa` — skill ponta a ponta para quando o usuário pedir uma avaliação completa e você quiser executar o fluxo inteiro sem redesenhar a lógica.

## Skills Hermes criadas/atualizadas nesta sessão

- `lector-portal-9-criar-treinamentos`
- `lector-upload-documentos-scorms`
- `lector-criar-turmas`
- `lector-curadoria-nomes-treinamentos`
- `lector-criar-conteudos-scorm`
- `lector-criar-imagens-capa`
- `lector-kb-search`
- `agent-reach`
- `lector-pesquisar-tendencias-criar-treinamento`
- `lector-criar-treinamento-video-hyperframes`
- `lector-avaliacoes-e-questoes`
- `lector-criar-questoes-api`
- `lector-criar-avaliacoes-api`
- `lector-validar-avaliacoes-api`
- `lector-agentes-avaliacoes`
- `lector-criar-avaliacao-completa`

## Padrão de qualidade definido

- Treinamentos devem ter nome editorial claro, sem timestamp no título.
- Conteúdo SCORM deve ter estrutura didática real, não só uma página simples.
- Turma gratuita deve ser criada e validada pelos endpoints de turma.
- Capa deve ser profissional, alinhada ao tema e enviada pelo `thumbset`.
- Avaliações devem ser validadas por criação, leitura direta e listagem.
- Questões devem ser validadas por leitura posterior quando forem criadas.
- Tokens/cookies nunca devem ser salvos nesta base.
- Quando o tema for aberto ou estratégico, pesquisar tendências antes de criar o conteúdo.
- Scripts de publicação podem ser salvos sem credenciais; credenciais devem entrar só por variável temporária em tempo de execução.
