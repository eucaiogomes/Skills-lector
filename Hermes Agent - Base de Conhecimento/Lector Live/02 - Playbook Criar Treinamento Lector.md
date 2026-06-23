# Playbook — Criar Treinamento Completo no Lector Live

## Objetivo

Criar um treinamento completo no Lector Live, portal 9, com nome editorial bem curado, conteúdo SCORM, turma gratuita, imagem de capa e validação por API.

## Ordem operacional recomendada

1. Curar o nome do treinamento.
2. Se o tema for amplo/estratégico, pesquisar tendências e escolher um recorte atual para o público.
3. Criar o conteúdo SCORM.
4. Validar o SCORM localmente: ZIP, manifest, HTML, JS e conclusão.
5. Gerar a imagem de capa.
6. Importar o SCORM no Lector.
7. Criar o treinamento com `SCOResource`.
8. Criar turma gratuita no mesmo payload.
9. Subir capa pelo `thumbset`.
10. Validar curso, recurso, turma e capa.
11. Atualizar Obsidian/skills com aprendizados.

## Skills Hermes a carregar

- `lector-curadoria-nomes-treinamentos`
- `lector-criar-conteudos-scorm`
- `lector-upload-documentos-scorms`
- `lector-portal-9-criar-treinamentos`
- `lector-criar-turmas`
- `lector-criar-imagens-capa`
- `lector-kb-search`
- `agent-reach` quando houver pesquisa externa de tendências

## Nome do treinamento

Regra: não usar timestamp, `SCORM`, `API`, `teste`, `final`, `novo` ou termos técnicos no título visível.

Exemplo ruim:

```text
Atendimento Suporte - Boas Práticas SCORM 1781968215124
```

Exemplo bom:

```text
Boas Práticas para Atendimento de Suporte
```

## Endpoint principal

```text
POST https://www.lector.live/lector-web-service/courses/saveCourse/9?useVersion=false
```

## Autenticação

Usar cookie atual do navegador, mas nunca salvar cookie real nesta base.

Quando automatizar a publicação, prefira salvar scripts sem credenciais e passar a credencial somente por variável temporária de execução.

Validar sessão antes:

```text
GET /lector-web-service/serviceQueue/info/9
```

## Criação do curso

O payload deve conter:

- `course.title.pt_BR` com nome editorial;
- `course.description.pt_BR` coerente com o curso;
- `course.syllabus.pt_BR` com tópicos reais;
- `course.resources` com `SCOResource` para SCORM;
- `course.classes` com turma;
- `classes` com wrapper da turma;
- `course.accountOwner.id = 9`;
- `course.userOwner.id = 999208`.



## Alternativa: Treinamento com Vídeo (Hyperframes + Narração)

Quando o usuário pedir vídeo em vez de SCORM:

1. Escrever narração clara (60-120s).
2. Criar composição HTML com Hyperframes (`data-duration`, `data-start` etc no root `<div data-composition-id>`).
3. Gerar áudio (Hermes TTS ou `hyperframes tts`).
4. Renderizar:
   ```bash
   npx hyperframes render . --output video_silent.mp4 --fps 24 --quality draft --low-memory-mode
   ffmpeg -i video_silent.mp4 -i narration.mp3 -c:v copy -c:a aac final.mp4
   ```
5. Validar com ffprobe.
6. Upload como documento com path terminando em **.mp4.lmp4**.
7. No curso, usar `DocumentResource` (não SCOResource).
8. Criar curso + turma + capa normalmente.

Skill dedicada: `lector-criar-treinamento-video-hyperframes`

Exemplo validado: courseId 1481259 (LGPD 2026).


## Avaliação como recurso do treinamento

Quando houver avaliação final vinculada ao treinamento, criar a avaliação por API e incluir em `course.resources` como:

```json
{
  "@class": "EvaluationResource",
  "type": "EVALUATION",
  "id": 0,
  "evaluation": {"id": 43126}
}
```

Na prática, usar o objeto completo retornado por `GET /lector-web-service/quiz/evaluation/{evaluationId}` dentro de `evaluation`. O backend cria um novo `resourceId` para o curso. Exemplo validado: curso `1481260` com `SCOResource` `10091616` e `EvaluationResource` `10091617` apontando para avaliação `43126`.

## Validação após criação

Curso:

```text
GET /lector-web-service/courses/{courseId}
```

Turmas edição:

```text
GET /lector-web-service/courses/classesForEditing/{courseId}/9
```

Turmas públicas:

```text
GET /lector-web-service/courses/classes/{courseId}/9
```

Verificar:

- título correto;
- `accountOwner.id = 9`;
- `userOwner.id = 999208`;
- recurso `@class: SCOResource`;
- `scormPackageId` presente;
- turma `free: true`;
- `purchaseInfo.price: 0.0`;
- `requireApproval: false`;
- `purchaseEnabled: true`.
