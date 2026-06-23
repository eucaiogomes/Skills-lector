# SCORM e Conteúdo Didático

## Padrão adotado

Criar pacotes SCORM 1.2 simples, compatíveis com o Lector, contendo:

```text
imsmanifest.xml
index.html
style.css
scorm_api.js
cover.png opcional
```

## Estrutura didática mínima

Um SCORM criado pelo agente deve conter:

1. Capa / abertura;
2. objetivos de aprendizagem;
3. módulos explicativos;
4. exemplos práticos;
5. checklist ou desafio;
6. quiz final;
7. chamada `completeScorm(100)` ao concluir.

## Manifest

O `imsmanifest.xml` deve ficar na raiz do ZIP e conter:

```xml
<schema>ADL SCORM</schema>
<schemaversion>1.2</schemaversion>
```

O recurso principal deve apontar para `index.html` e usar `adlcp:scormtype="sco"`.

## JavaScript SCORM mínimo

Funções importantes:

- `initScorm()`
- `setScore(score)`
- `completeScorm(score)`

Ao concluir:

```javascript
API.LMSSetValue('cmi.core.lesson_status', 'completed');
API.LMSCommit('');
API.LMSFinish('');
```

## Importação no Lector

Endpoint:

```text
POST /lector-web-service/scorm/importAsync
```

Campos multipart:

- `accountId = 9`
- `useS3 = true`
- `content = arquivo .zip SCORM`

Depois consultar:

```text
GET /lector-web-service/scorm/importStatus/{scormPackageId}
```

## Recurso correto no curso

SCORM deve ser salvo como `SCOResource`:

```json
{
  "@class": "SCOResource",
  "type": "SCO",
  "scormPackageId": 9882,
  "scoItem": {
    "identifier": "ITEM-...",
    "title": "Título do SCORM"
  },
  "minimumProgress": 100
}
```

Não usar `DocumentResource` para SCORM.

## Exemplo validado

Treinamento: `Lógica de Programação: Fundamentos Essenciais`

SCORM package: `9882`

Recurso no curso:

- `@class: SCOResource`
- `resourceId: 10091611`
- `minimumProgress: 100`

Conteúdo abordado:

- lógica de programação;
- algoritmos;
- variáveis;
- operadores;
- estruturas de decisão;
- estruturas de repetição;
- funções;
- decomposição de problemas;
- pseudocódigo;
- teste de mesa;
- desafio prático;
- quiz final.

## Exemplo validado — treinamento de RH baseado em pesquisa

Treinamento: `IA no RH: Trabalho Humano-Máquina e Liderança Estratégica`

SCORM package: `9884`

Recurso no curso:

- `@class: SCOResource`
- `resourceId: 10091613`
- `minimumProgress: 100`

Conteúdo abordado:

- por que IA no RH está em alta;
- IA como parceira do RH;
- redesenho do trabalho humano-máquina;
- skills, upskilling e reskilling;
- employee experience e EVP;
- saúde mental e riscos psicossociais;
- liderança para mudança contínua;
- cenário prático;
- checklist de aplicação;
- quiz final.

Validação local adicional:

- abrir o HTML em navegador local;
- testar funções JS do quiz e conclusão;
- confirmar que `finishCourse()` chama `completeScorm(100)`;
- quando o clique automatizado não refletir o estado visual, testar a função diretamente no console antes de assumir erro no conteúdo.
