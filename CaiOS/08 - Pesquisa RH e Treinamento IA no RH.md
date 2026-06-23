# Pesquisa RH e Treinamento IA no RH

Atualizado em: 2026-06-20 18:24:15

## Objetivo

Registrar o fluxo validado para pesquisar assuntos em alta para o público de RH e transformar o resultado em um treinamento completo no Lector Live, com SCORM, turma gratuita e capa.

## Tema criado

```text
IA no RH: Trabalho Humano-Máquina e Liderança Estratégica
```

## Por que este tema foi escolhido

A pesquisa de tendências apontou convergência entre fontes internacionais e brasileiras sobre a transformação do RH em 2026. Os temas mais recorrentes foram:

1. IA aplicada ao RH e transformação do modelo operacional.
2. Redesenho do trabalho na era humano-máquina.
3. People analytics e talent intelligence.
4. Employee experience e EVP.
5. Upskilling e reskilling.
6. Liderança para mudança contínua.
7. Saúde mental, riscos psicossociais e prevenção.

## Fontes consultadas

- Gartner — tendências e prioridades de RH para 2026.
- Mercer — Global Talent Trends 2026.
- SHRM — State of AI in HR 2026.
- ADP — tendências de RH, tecnologia, pessoas e compliance.
- Brandon Hall Group — HR Outlook 2026.
- GPTW Brasil — Tendências de Gestão de Pessoas 2026.
- Você RH / Caju — IA, saúde mental e mudanças culturais no RH.

## Estrutura didática criada no SCORM

O SCORM foi criado com:

- abertura e promessa do treinamento;
- objetivos de aprendizagem;
- explicação do motivo do tema estar em alta;
- módulos sobre IA, redesenho do trabalho, skills, employee experience, saúde mental e liderança;
- cenário prático para RH;
- checklist de aplicação;
- quiz final;
- botão de conclusão com `completeScorm(100)`.

## Artefatos locais

```text
C:\Users\gcaio\agent-tools\lector-training-build\rh-ia-trabalho-humano-maquina-2026
```

SCORM validado:

```text
C:\Users\gcaio\agent-tools\lector-training-build\ia_no_rh_trabalho_humano_maquina_lideranca_estrategica_scorm.zip
```

Capa e variações:

```text
ia_no_rh_trabalho_humano_maquina_lideranca_estrategica_capa.png
ia_no_rh_trabalho_humano_maquina_lideranca_estrategica_cover.png
ia_no_rh_trabalho_humano_maquina_lideranca_estrategica_banner.png
ia_no_rh_trabalho_humano_maquina_lideranca_estrategica_square.png
```

## Validações locais realizadas

- ZIP contém `imsmanifest.xml`, `index.html`, `style.css` e `scorm_api.js`.
- `imsmanifest.xml` validado como SCORM 1.2.
- `adlcp:scormtype="sco"` presente no recurso.
- HTML abriu localmente no navegador.
- Funções `answer(true)` e `finishCourse()` testadas no browser.
- Feedback final confirmado: `Treinamento concluído e progresso registrado.`

## Publicação validada no Lector

Ambiente:

```text
https://www.lector.live
```

Portal:

```text
9
```

Resultado:

```text
courseId: 1481257
version: 1
title: IA no RH: Trabalho Humano-Máquina e Liderança Estratégica
scormPackageId: 9884
resourceId: 10091613
resource @class: SCOResource
classId: 129406
class free: true
thumbset status: 200
```

## Aprendizados operacionais

1. Pesquisa de tendências deve acontecer antes da criação do conteúdo quando o tema é aberto.
2. Para RH, o melhor treinamento não é só sobre “IA”, mas sobre como o RH redesenha trabalho, desenvolve competências, cuida da experiência e prepara líderes.
3. O título precisa ser editorial, sem `SCORM`, timestamp ou termos técnicos.
4. A validação local do SCORM deve acontecer antes de qualquer upload.
5. Ao testar HTML no browser, se o clique automatizado não refletir o feedback, testar também as funções JS diretamente no console antes de concluir que o conteúdo está quebrado.
6. Para scripts longos de publicação, evitar heredoc inline muito extenso. Preferir script salvo sem credenciais e passar credencial apenas por variável de ambiente temporária.
7. A resposta do `thumbset` com status `200` valida o upload, mesmo que o `GET /courses/{id}` não retorne imediatamente chaves de thumb preenchidas.
8. Cookies/tokens devem ser usados apenas em tempo de execução e nunca registrados nesta base.

## Fluxo recomendado para próximos treinamentos baseados em pesquisa

1. Pesquisar tendências com Agent Reach / web.
2. Sintetizar 5–7 temas fortes para o público-alvo.
3. Escolher um tema com valor prático e recorte claro.
4. Curar título editorial.
5. Criar SCORM com estrutura didática completa.
6. Gerar capa coerente com o público e tema.
7. Validar localmente ZIP, manifest, HTML, JS e capa.
8. Validar sessão Lector sem salvar credencial.
9. Importar SCORM e obter `SCOResource`.
10. Criar curso com turma gratuita.
11. Enviar capa pelo `thumbset`.
12. Validar curso, recurso e turma por API.
13. Atualizar Obsidian e skills com aprendizados novos.

## Skills relacionadas

- `agent-reach`
- `lector-kb-search`
- `lector-curadoria-nomes-treinamentos`
- `lector-criar-conteudos-scorm`
- `lector-upload-documentos-scorms`
- `lector-portal-9-criar-treinamentos`
- `lector-criar-turmas`
- `lector-criar-imagens-capa`
