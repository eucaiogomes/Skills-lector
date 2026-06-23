# Job Diário RH — Riscos Psicossociais e Saúde Mental

Data: 2026-06-21 21:30

## Resultado

Foi executado o job autônomo diário para criar um treinamento completo de RH. Como não havia credencial/sessão Lector disponível no ambiente, a publicação por API foi bloqueada em `serviceQueue/info/9` com `403 USER_NOT_LOGGED_IN`. Foram criados e validados os artefatos locais necessários para publicação manual/assistida quando houver cookie válido.

## Título editorial

`Riscos Psicossociais e Saúde Mental no Trabalho`

Critérios atendidos:

- título sem `SCORM`, `API`, `teste` ou timestamp;
- tema claro e publicável para catálogo;
- recorte atual para RH no Brasil;
- foco didático prático: prevenção, indicadores e liderança.

## Fontes pesquisadas

- Gartner — principais prioridades de RH para 2026: IA, redesenho humano-máquina, liderança e cultura.
- GPTW Brasil — tendências de gestão de pessoas 2026: saúde mental como modelo técnico/preventivo e riscos psicossociais impulsionados pela NR-01.
- Alelo — tendências de RH 2026: saúde mental, bem-estar, experiência do colaborador e liderança humanizada.
- Valor Econômico / Valor International — adoção de IA no RH brasileiro e uso para sinais de sobrecarga/burnout.
- MIT Sloan Management Review Brasil — IA reposicionando RH como motor estratégico.
- Mundo RH / ABRH — IA, vínculo humano, confiança e culturas saudáveis.

## Tendências sintetizadas

1. IA no RH vira rotina em recrutamento, onboarding, clima, performance e decisões sensíveis.
2. Saúde mental e riscos psicossociais deixam de ser ações pontuais e viram política preventiva.
3. Liderança precisa equilibrar performance, comunicação e resiliência emocional.
4. Employee experience passa a focar jornadas críticas e escuta contínua.
5. People analytics exige governança e interpretação humana.
6. Trabalho humano-máquina exige redesenho de papéis e aprendizagem contínua.
7. Cultura, pertencimento e segurança psicológica ganham valor quanto mais a tecnologia avança.

## Artefatos locais criados

Base local:

```text
C:\tmp\riscos_psicossociais_saude_mental_trabalho_daily_20260621
```

Arquivos principais:

```text
C:\tmp\riscos_psicossociais_saude_mental_trabalho_daily_20260621\brief_treinamento.md
C:\tmp\riscos_psicossociais_saude_mental_trabalho_daily_20260621\riscos_psicossociais_saude_mental_trabalho_scorm.zip
C:\tmp\riscos_psicossociais_saude_mental_trabalho_daily_20260621\images\riscos_psicossociais_saude_mental_trabalho_cover.png
C:\tmp\riscos_psicossociais_saude_mental_trabalho_daily_20260621\images\riscos_psicossociais_saude_mental_trabalho_banner.png
C:\tmp\riscos_psicossociais_saude_mental_trabalho_daily_20260621\images\riscos_psicossociais_saude_mental_trabalho_square.png
C:\tmp\riscos_psicossociais_saude_mental_trabalho_daily_20260621\payloads\question_payloads.json
C:\tmp\riscos_psicossociais_saude_mental_trabalho_daily_20260621\payloads\evaluation_payload_pending_question_ids.json
C:\tmp\riscos_psicossociais_saude_mental_trabalho_daily_20260621\payloads\course_payload_pending_publish.json
```

## Validações realizadas

- KB Lector consultada com `lector-kb-search`.
- Pesquisa externa feita com Agent Reach / Exa; `agent-reach doctor` executado.
- SCORM validado com script da skill `lector-criar-conteudos-scorm`:
  - `SCORM_OK`
  - `imsmanifest.xml` na raiz;
  - `index.html`, `style.css`, `scorm_api.js` presentes;
  - `schemaversion` 1.2;
  - `adlcp:scormtype="sco"`.
- HTML verificado localmente por inspeção automatizada:
  - `initScorm();` presente;
  - `completeScorm(100)` presente;
  - `function answer(ok)` presente;
  - `function finishCourse()` presente;
  - elemento `feedback` presente.
- Capa verificada visualmente: layout profissional, texto legível, tema compatível com RH/saúde mental.
- Arquivos de imagem gerados:
  - cover/banner: 1600x900;
  - square: 900x900.
- Tentativa segura de validação de sessão Lector sem credencial retornou:
  - `403 USER_NOT_LOGGED_IN`.

## Publicação Lector

Não publicada nesta execução por ausência de credencial/sessão válida.

IDs reais desta execução:

```text
courseId: não criado
version: não criado
scormPackageId: não importado
resourceId: não criado
evaluationId: não criado
classId: não criado
thumbset: não enviado
```

## Próximo passo quando houver sessão válida

1. Criar as questões com `POST /lector-web-service/quiz/question/9` usando `question_payloads.json`.
2. Criar avaliação ativa com `POST /lector-web-service/quiz/evaluation/9`, substituindo placeholders pelos IDs reais das questões.
3. Importar SCORM com `POST /lector-web-service/scorm/importAsync`.
4. Poll em `GET /lector-web-service/scorm/importStatus/{scormPackageId}`.
5. Criar curso com `saveCourse/9?useVersion=false`, usando `SCOResource`, `EvaluationResource` e turma gratuita.
6. Subir capa com `courses/thumbset/{courseId}/{version}`.
7. Validar curso, recurso, avaliação e turma por API.

## Observação de segurança

Nenhum cookie, token ou credencial foi salvo nesta nota ou nos artefatos.
