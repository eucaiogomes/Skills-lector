# Linha do Tempo da Sessão

## Objetivo geral

Construir um fluxo operacional para criar treinamentos completos no Lector Live, no portal 9, usando o Hermes Agent como executor e registrando o aprendizado em skills e nesta base de conhecimento.

## Informações fixas validadas

- Portal Lector: `9`
- Autor padrão: Caio Gomes
- ID do usuário autor: `999208`
- Ambiente usado nas execuções validadas: `https://www.lector.live`
- Endpoint principal de criação de treinamento:
  - `POST /lector-web-service/courses/saveCourse/9?useVersion=false`

> Observação: cookies e tokens reais não devem ser salvos em nota, skill ou memória.

## Sequência do que foi construído

### 1. Criação de treinamentos via API

Foi validado que o payload simplificado da documentação pode falhar com `500 Erro salvando treinamento`.

O payload real precisa se aproximar do formato enviado pela interface web, incluindo campos como:

- `useVersioning: true`
- `thumbs`
- `category: {}`
- `workload: {}`
- `gamification: null`
- `resources` completos
- `useMaxSubscriptions: false`
- `useTermsOfUse: false`
- `hideContentNavigation: true`
- `daysBeforeSendClassExpirationMessage: 1`
- `termsOfUse: {}`
- `userOwner` completo

Skill consolidada:

- `lector-portal-9-criar-treinamentos`

### 2. SCORM correto no Lector

Foi descoberto que SCORM não deve ser tratado como `DocumentResource`.

Fluxo correto:

1. Criar ZIP SCORM 1.2 com `imsmanifest.xml` na raiz.
2. Enviar para `POST /lector-web-service/scorm/importAsync`.
3. Consultar `GET /lector-web-service/scorm/importStatus/{scormPackageId}`.
4. Usar o recurso retornado como base para `@class: SCOResource`, `type: SCO`, `scormPackageId` e `scoItem`.

Skills consolidadas:

- `lector-upload-documentos-scorms`
- `lector-criar-conteudos-scorm`

### 3. Criação de turma gratuita

Foi validado que a turma deve ser enviada em dois lugares do payload:

- `course.classes`
- `classes` como wrapper `{courseClass, permissions, removedPermissions, viewBlockings}`

Curso validado com turma gratuita:

- Curso: `1481254`
- Turma: `129403`
- Status: gratuita, sem aprovação, assinável

Skill criada:

- `lector-criar-turmas`

### 4. Curadoria de nomes

Foi identificado que nomes como este são ruins:

```text
Atendimento Suporte - Boas Práticas SCORM 1781968215124
```

Problemas:

- contém timestamp;
- contém detalhe técnico `SCORM`;
- parece teste automatizado;
- não comunica bem o valor do treinamento.

Padrão definido:

- usar nome editorial humano;
- não usar timestamp no título;
- não usar `SCORM`, `API`, `teste`, `corrigido`, `final` sem necessidade.

Exemplo bom:

```text
Boas Práticas para Atendimento de Suporte
```

Skill criada:

- `lector-curadoria-nomes-treinamentos`

### 5. Criação de treinamento completo de lógica de programação

Foi criado um treinamento completo com título curado, conteúdo SCORM, turma gratuita, imagem de capa e upload da capa para o Lector.

Dados validados:

- Curso: `1481255`
- Título: `Lógica de Programação: Fundamentos Essenciais`
- Versão: `1`
- SCORM package: `9882`
- Recurso: `SCOResource`, ID `10091611`
- Turma: `129404`
- Nome da turma: `Turma Gratuita - Lógica de Programação: Fundamentos Essenciais`
- Capa local: `C:\Users\gcaio\logica_programacao_fundamentos_essenciais_capa.png`
- SCORM local: `C:\Users\gcaio\logica_programacao_fundamentos_essenciais_scorm.zip`

### 6. Imagens de capa

O gerador externo de imagem estava indisponível no ambiente, então foi criado fallback local com Python/Pillow.

Endpoint de upload de capa validado:

```text
POST /lector-web-service/courses/thumbset/{courseId}/{version}
```

Campos validados:

- `square`
- `banner`
- `cover`
- `squareRemoved=false`
- `bannerRemoved=false`
- `coverRemoved=false`

Execução validada:

- Curso: `1481255`
- Versão: `1`
- Status: `200`

Skill criada:

- `lector-criar-imagens-capa`


### 7. Criação de treinamento completo sobre mingau de milho

Criado em: 2026-06-20 13:03:40 Hora oficial do Brasil

Foi criado um treinamento completo com conteúdo culinário, SCORM, turma gratuita e imagem de capa.

Dados validados:

- Curso: `1481256`
- Título: `Mingau de Milho Cremoso: Preparo Completo`
- Versão: `1`
- SCORM package: `9883`
- Recurso: `SCOResource`, ID `10091612`
- Turma: `129405`
- Nome da turma: `Turma Gratuita - Mingau de Milho Cremoso: Preparo Completo`
- Capa local: `C:\Users\gcaio\mingau_milho_cremoso_preparo_completo_capa.png`
- SCORM local: `C:\Users\gcaio\mingau_milho_cremoso_preparo_completo_scorm.zip`
- Upload de capa pelo `thumbset`: status `200`

Conteúdo do SCORM:

- escolha de ingredientes;
- mise en place;
- preparo da base de milho;
- cozimento e controle do ponto;
- correção de textura;
- higiene e conservação;
- variações e apresentação;
- checklist prático;
- quiz final.

### 8. Pesquisa de tendências de RH e treinamento sobre IA no RH

Criado em: 2026-06-20 18:24:15

Foi criada uma rotina completa para pesquisar assuntos em alta para o público de RH e transformar o resultado em treinamento no Lector Live.

Tema escolhido:

```text
IA no RH: Trabalho Humano-Máquina e Liderança Estratégica
```

Fontes usadas na curadoria:

- Gartner;
- Mercer;
- SHRM;
- ADP;
- Brandon Hall Group;
- GPTW Brasil;
- Você RH / Caju.

Dados validados:

- Curso: `1481257`
- Título: `IA no RH: Trabalho Humano-Máquina e Liderança Estratégica`
- Versão: `1`
- SCORM package: `9884`
- Recurso: `SCOResource`, ID `10091613`
- Turma: `129406`
- Nome da turma: `Turma Gratuita - IA no RH: Trabalho Humano-Máquina e Liderança Estratégica`
- Upload de capa pelo `thumbset`: status `200`
- Nota detalhada: [[08 - Pesquisa RH e Treinamento IA no RH]]

Aprendizados:

- Para temas abertos, pesquisar tendências antes de produzir o conteúdo.
- O recorte de RH ficou mais forte ao combinar IA, trabalho humano-máquina, liderança, employee experience, people analytics, skills e saúde mental.
- Validar HTML/SCORM localmente antes do upload reduz risco de publicar conteúdo quebrado.
- Para scripts longos de publicação, salvar script sem credencial e passar cookie/token só por variável temporária de execução.
- O `GET /courses/{id}` pode não retornar imediatamente chaves de thumb preenchidas; o `thumbset` com status `200` é a validação direta do upload de capa.


### 9. Treinamentos com Vídeo usando Hyperframes (2026-06-20)

Fluxo validado para criar treinamentos em vídeo com narração:

- Usar Hyperframes para composição HTML determinística.
- Gerar narração separada (TTS) e muxar com ffmpeg.
- Upload como documento com extensão `.mp4.lmp4`.
- No curso: usar `DocumentResource` (não SCOResource).
- Criar curso + turma gratuita + capa normalmente.

Exemplo real:
- Título: LGPD em 2026: Governança, IA e Privacidade na Prática
- courseId: 1481259
- Duração do vídeo: 83 segundos
- Recurso: DocumentResource
- Capa: enviada com sucesso (thumbset 200)

Skill criada: `lector-criar-treinamento-video-hyperframes`

Diferença chave em relação ao SCORM: o Lector trata vídeos locais como documentos de vídeo, não como pacotes SCO.

### 10. Job diário RH — riscos psicossociais e saúde mental (2026-06-21)

Foi executado o job autônomo diário de RH para pesquisar tendências e preparar um treinamento completo.

Tema escolhido:

```text
Riscos Psicossociais e Saúde Mental no Trabalho
```

Motivo do recorte:

- tema atual para RH no Brasil por causa da agenda preventiva e NR-01;
- alta aplicabilidade didática para liderança e RH;
- conecta saúde mental, indicadores, cultura e prevenção;
- evita repetir diretamente o treinamento anterior sobre IA no RH.

Artefatos locais criados:

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

Validações:

- KB Lector consultada antes da criação.
- Pesquisa externa feita via Agent Reach/Exa.
- SCORM validado com `SCORM_OK`.
- HTML contém `initScorm()`, `completeScorm(100)`, função de quiz e função de conclusão.
- Capa profissional gerada localmente com Pillow e variações `cover`, `banner`, `square`.
- Publicação não executada porque `GET /serviceQueue/info/9` sem cookie retornou `403 USER_NOT_LOGGED_IN`.

Nota detalhada: [[12 - Job Diário RH - Riscos Psicossociais e Saúde Mental]]
