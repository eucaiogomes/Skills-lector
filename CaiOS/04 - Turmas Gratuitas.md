# Turmas Gratuitas no Lector Live

## Conceito

No Lector, turmas são salvas junto com o curso pelo endpoint `saveCourse`.

A turma deve aparecer em dois pontos do payload:

1. `course.classes`
2. `classes` como wrapper

## Payload mínimo validado

```json
{
  "name": {"pt_BR": "Turma Gratuita - Nome do Treinamento"},
  "type": "indefinite",
  "requireApproval": false,
  "priceType": "free",
  "free": true,
  "purchaseInfo": {
    "price": 0,
    "quantity": 2,
    "frequency": "MONTHLY",
    "free": true
  },
  "subscriptionsLimit": null,
  "resourcesMap": {},
  "permissions": [],
  "removedPermissions": [],
  "subscriptionPackageType": "CONCURRENT",
  "useSubscriptionsPackage": false,
  "expiresNotice": 1,
  "hideFreeMask": false,
  "inactivateOnFinish": false,
  "tutors": [],
  "customFields": [],
  "userFields": []
}
```

Wrapper:

```json
{
  "courseClass": {"...": "objeto da turma"},
  "permissions": [],
  "removedPermissions": [],
  "viewBlockings": []
}
```

## Validação

Turmas para edição:

```text
GET /lector-web-service/courses/classesForEditing/{courseId}/9
```

Turmas públicas:

```text
GET /lector-web-service/courses/classes/{courseId}/9
```

## Exemplo validado

Curso:

```text
1481255 — Lógica de Programação: Fundamentos Essenciais
```

Turma:

```text
129404 — Turma Gratuita - Lógica de Programação: Fundamentos Essenciais
```

Retorno validado:

```json
{
  "free": true,
  "purchaseInfo": {
    "price": 0.0,
    "free": true
  },
  "requireApproval": false,
  "subscriptionStatus": "NOT_SUBSCRIBED",
  "purchaseEnabled": true
}
```
