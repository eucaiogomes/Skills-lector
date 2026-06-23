---
caios_type: "session-doc"
session_date: "2026-06-21"
project: "CaiOS"
tags: ["caios", "sessão", "hermes", "kanban", "mission-control", "chat", "websocket"]
updated: "2026-06-22T00:00:00.000Z"
---

# Sessão 2026-06-21 — Hermes Chat, Kanban e Mission Control

> Documentação detalhada de tudo que foi implementado nesta sessão de desenvolvimento do [[CaiOS]].
> Ferramenta principal: [[Hermes]]

---

## 1. Contexto

O **CaiOS** é o workspace pessoal do Caio — um app Tauri + React que centraliza projetos, ferramentas de IA, terminal, notas e o **Segundo Cérebro** (grafo Obsidian em `/brain`).

Nesta sessão, o foco foi integrar o **Hermes** (orquestrador de agentes) de forma mais completa no CaiOS:

1. Chat com histórico de sessões
2. Visibilidade das tarefas dos agentes (Kanban) no Dashboard
3. Painel de Cron jobs
4. Correção de bugs críticos no chat: **"session busy"** e **parada aparente ao sair da página**

Tudo foi construído consumindo as APIs HTTP e WebSocket do **Hermes Dashboard** (porta 9119 em Tauri, proxy `/hermes-api` no browser).

---

## 2. Pedidos do usuário (em ordem)

| # | Pedido | Status |
|---|--------|--------|
| 1 | Sidebar de sessões no Hermes — listar anteriores, mostrar atual, iniciar nova | ✅ Feito |
| 2 | Kanban + Cron jobs no Dashboard — quadro de tarefas dos agentes | ✅ Feito |
| 3 | Corrigir "session busy" que quebrava o estado do chat | ✅ Feito |
| 4 | Hermes não deve parar ao sair da página / trocar de aba do projeto | ✅ Feito |
| 5 | Documentar tudo no Segundo Cérebro | ✅ Este arquivo |

---

## 3. Funcionalidades implementadas

### 3.1 Sidebar de sessões Hermes

**O que faz:**
- Lista as últimas 30 sessões do Hermes ordenadas por atividade recente
- Destaca a sessão ativa
- Botão **Nova sessão** cria conversa limpa
- Botão **Refresh** recarrega a lista
- Ao clicar numa sessão, retoma via WebSocket `session.resume` e carrega mensagens

**Componentes:**
- `HermesSessionSidebar.tsx` — UI lateral (260px)
- `HermesChatView.tsx` — layout sidebar + chat + header

**Fluxo:**
```
Usuário clica sessão → switchSession(id)
  → gw.request('session.resume', { session_id, close_on_disconnect: false })
  → applyResumeResult() → mensagens + running state
```

**Helpers de exibição:**
- `formatSessionLabel()` — título, preview ou "Conversa sem título"
- `formatSessionTime()` — "agora", "5 min", "ontem", etc.

---

### 3.2 Chat Hermes (WebSocket)

**Hook central:** `useHermesChat.ts`

**Estados expostos:**
| Estado | Tipo | Descrição |
|--------|------|-----------|
| `phase` | `booting \| connecting \| ready \| busy \| error` | Ciclo de vida da conexão |
| `messages` | `HermesChatMessage[]` | Histórico com streaming e tools |
| `thinking` | `boolean` | Indicador de raciocínio |
| `backgroundNote` | `string \| null` | Aviso amarelo (trabalho em background) |
| `error` | `string \| null` | Erro vermelho (falha real) |
| `sessions` | `HermesSessionInfo[]` | Lista para sidebar |
| `storedSessionId` | `string \| null` | Chave da sessão ativa |
| `isBusy` / `canType` | `boolean` | Controle do composer |

**Eventos WebSocket tratados:**
- `message.start` / `message.delta` / `message.complete` — resposta do agente
- `thinking.delta` — indicador de pensamento
- `tool.start` / `tool.complete` — atividade de ferramentas no bubble
- `session.info` — sincroniza `running` do servidor
- `error` — trata "session busy" sem resetar estado

**Model picker:** `HermesModelPicker.tsx` — troca provider/modelo via `POST /api/model/set` e reinicia sessão.

---

### 3.3 Kanban no Dashboard

**O que faz:**
- Exibe quadro Kanban com colunas ativas: triagem, a fazer, pronto, em andamento, bloqueado, concluído
- Cada card mostra título, resumo, assignee (agente), tenant, prioridade
- Badge no header: "X em andamento" ou "Y tarefas"
- Atualização automática a cada **5 segundos**

**Componentes:**
- `KanbanBoard.tsx` — renderização das colunas
- `useMissionControlFeed.ts` — polling unificado
- `Dashboard.tsx` — seção integrada

**Origem dos dados:** tarefas criadas pelo Hermes e outros agentes via plugin Kanban do Hermes.

---

### 3.4 Cron jobs no Dashboard

**O que faz:**
- Lista jobs agendados do Hermes (`profile=all`)
- Mostra schedule, última/próxima execução, estado enabled/disabled
- Ações: **Pausar**, **Retomar**, **Executar agora**

**Componente:** `CronJobsPanel.tsx`

---

### 3.5 Mission Control Feed

**Hook:** `useMissionControlFeed.ts`

```
refresh() a cada 5s:
  1. ensureDashboard() — garante Hermes dashboard online
  2. Promise.all([
       fetchHermesKanbanBoard(),
       fetchHermesCronJobs('all')
     ])
  3. Atualiza board, cronJobs, online, error
```

**Métricas derivadas:**
- `activeTaskCount` — tarefas fora de done/archived
- `runningCount` — tarefas na coluna `running`

> **Nota:** O polling só roda quando o usuário está na página Dashboard. Não interfere no chat Hermes.

---

## 4. Correção de bugs

### 4.1 "Session busy"

**Sintoma:** Hermes demora a responder → aparece "session busy" → UI quebra, estado inconsistente.

**Causas identificadas:**

1. **Timeout destrutivo (90s)** — resetava `busyRef` e `phase` para `ready` enquanto o servidor ainda tinha `running: true`. Próximo envio → "session busy".
2. **`canType` permitia digitar durante `busy`** — usuário enviava mensagem enquanto agente trabalhava → conflito.
3. **"Session busy" como erro vermelho** — assustava e parecia falha fatal, mas é estado normal de sessão ocupada.

**Correções aplicadas:**

| Correção | Detalhe |
|----------|---------|
| Removido timeout 90s destrutivo | Substituído por `backgroundNote` suave após 120s |
| `canType` só em `phase === 'ready'` | Composer bloqueado enquanto agente responde |
| "Session busy" → `backgroundNote` amarelo | Não reseta estado; mantém `busy` |
| `prompt.submit` timeout 30s | Só para ACK inicial; não assume fim da tarefa |
| Timeout/conexão perdida | Mantém `busy`, tenta `reconnect()` |
| Handler `session.info` | Sincroniza `running` com servidor |

---

### 4.2 Parar ao sair da página

**Sintoma:** Usuário navega para Dashboard ou outra aba → parece que o Hermes parou de trabalhar.

**Causas identificadas:**

1. **`close_on_disconnect: true` (padrão antigo)** — ao fechar WebSocket, servidor encerrava sessão/agente.
2. **Cleanup no unmount fechava WS** — `gw.close()` ao sair da rota `/hermes`.
3. **Sem retomada ao voltar** — sempre criava sessão nova em vez de `resume`.

**Correções aplicadas:**

| Correção | Detalhe |
|----------|---------|
| `close_on_disconnect: false` | Em `session.create` e `session.resume` |
| **Gateway persistente** | `persistentGateway` em nível de módulo — WS não fecha ao trocar rota |
| **Listeners removíveis** | `clearGatewayListeners()` no unmount; conexão permanece |
| **Persistência de sessão** | `sessionStorage` chave `caios_hermes_active_session` |
| **Boot com resume** | Ao montar, tenta `session.resume` da sessão salva |
| **Banner backgroundNote** | "Você pode sair da página que o trabalho continua" |
| **Botão Sincronizar** | `reconnect()` — reconecta WS e faz `session.resume` |

**Arquivo de persistência:** `src/lib/hermes-session-persist.ts`

```typescript
STORAGE_KEY = 'caios_hermes_active_session'
getPersistedHermesSession() / setPersistedHermesSession()
```

---

## 5. Arquitetura técnica

### 5.1 Camadas

```
┌─────────────────────────────────────────────────────────┐
│  UI (React)                                             │
│  HermesChatView, HermesSessionSidebar, KanbanBoard,     │
│  CronJobsPanel, Dashboard                               │
├─────────────────────────────────────────────────────────┤
│  Hooks                                                  │
│  useHermesChat, useMissionControlFeed                   │
├─────────────────────────────────────────────────────────┤
│  Lib                                                    │
│  hermes-api.ts (HTTP), hermes-gateway.ts (WS JSON-RPC), │
│  hermes-session-persist.ts                              │
├─────────────────────────────────────────────────────────┤
│  Services                                               │
│  hermes-dashboard.service.ts (ensureDashboard)          │
├─────────────────────────────────────────────────────────┤
│  Hermes Dashboard (9119)                                │
│  HTTP REST + WebSocket /api/ws                          │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Cliente WebSocket (`HermesGateway`)

- Protocolo JSON-RPC 2.0 sobre WebSocket
- `request(method, params, timeoutMs)` — chamadas com id e timeout
- `on(eventType, callback)` — eventos push (`method: "event"`)
- `onState(callback)` — `idle | connecting | open | closed | error`
- Reconexão automática quando `state === 'closed'` e componente montado

### 5.3 Fluxo de boot do chat

```
boot()
  → ensureDashboard()
  → fetchHermesSessionToken() (HTML scrape do dashboard)
  → connectGateway() [reusa persistentGateway se open]
  → getPersistedHermesSession()
     ├─ tem sessão → session.resume → applyResumeResult
     └─ não tem → session.create → mensagem de boas-vindas
  → refreshModelInfo() + refreshSessions()
```

### 5.4 Fluxo de envio de mensagem

```
sendMessage(text)
  → busyRef = true, phase = 'busy'
  → adiciona bubble user
  → gw.request('prompt.submit', { session_id, text }, 30_000)
  → eventos WS: message.start → delta → complete
  → finalizeAssistant() → phase = 'ready'
```

---

## 6. APIs Hermes utilizadas

### HTTP (via `hermes-api.ts`)

| Método | Endpoint | Uso |
|--------|----------|-----|
| GET | `/` | Scrape token `__HERMES_SESSION_TOKEN__` |
| GET | `/api/sessions?limit=30&offset=0&order=recent` | Lista sessões |
| GET | `/api/sessions/{id}/messages` | Mensagens de sessão (HTTP fallback) |
| GET | `/api/model/info` | Modelo atual |
| GET | `/api/model/options` | Providers e modelos |
| POST | `/api/model/set` | Trocar modelo |
| GET | `/api/plugins/kanban/board` | Quadro Kanban |
| GET | `/api/cron/jobs?profile=all` | Lista cron jobs |
| POST | `/api/cron/jobs/{id}/pause` | Pausar job |
| POST | `/api/cron/jobs/{id}/resume` | Retomar job |
| POST | `/api/cron/jobs/{id}/trigger` | Executar agora |

**Auth:** header `X-Hermes-Session-Token` em todas as chamadas HTTP.

### WebSocket (`/api/ws?token=...`)

| Método RPC | Params | Uso |
|------------|--------|-----|
| `session.create` | `{ close_on_disconnect: false }` | Nova sessão |
| `session.resume` | `{ session_id, close_on_disconnect: false }` | Retomar sessão |
| `prompt.submit` | `{ session_id, text }` | Enviar mensagem |

**Eventos recebidos:** `message.start`, `message.delta`, `message.complete`, `thinking.delta`, `tool.start`, `tool.complete`, `session.info`, `error`

---

## 7. Arquivos criados e modificados

### Novos arquivos

| Arquivo | Papel |
|---------|-------|
| `src/lib/hermes-session-persist.ts` | Persistência da sessão ativa em sessionStorage |
| `src/components/hermes/HermesSessionSidebar.tsx` | Sidebar de sessões |
| `src/components/dashboard/KanbanBoard.tsx` | Quadro Kanban |
| `src/components/dashboard/CronJobsPanel.tsx` | Painel de cron jobs |
| `src/hooks/useMissionControlFeed.ts` | Polling kanban + cron |

### Arquivos modificados

| Arquivo | Mudanças principais |
|---------|---------------------|
| `src/hooks/useHermesChat.ts` | Sessões, resume, busy fix, gateway persistente, backgroundNote |
| `src/lib/hermes-api.ts` | APIs sessions, kanban, cron; tipos `HermesSessionResumeResult` |
| `src/components/hermes/HermesChatView.tsx` | Layout sidebar, banner backgroundNote, Sincronizar |
| `src/pages/Dashboard.tsx` | Seções Kanban e Cron integradas |

### Arquivos de suporte (já existentes)

| Arquivo | Papel |
|---------|-------|
| `src/lib/hermes-gateway.ts` | Cliente WebSocket JSON-RPC |
| `src/services/hermes-dashboard.service.ts` | `ensureDashboard()` |
| `src/pages/Hermes.tsx` | Rota `/hermes` |

---

## 8. Rotas do CaiOS relacionadas

| Rota | Página | Relação |
|------|--------|---------|
| `/hermes` | HermesPage → HermesChatView | Chat + sessões |
| `/` | Dashboard | Kanban + Cron |
| `/mission-control` | MissionControl | Controle Hermes legado |
| `/brain` | BrainPage | Segundo Cérebro (este doc aparece no grafo) |

---

## 9. Como testar

### Chat e sessões
1. Abrir `/hermes` — deve conectar e mostrar sidebar
2. Enviar mensagem — status "Respondendo…", composer bloqueado
3. Clicar sessão anterior — carrega histórico
4. "Nova sessão" — conversa limpa

### Trabalho em background
1. Enviar tarefa longa (ex: pesquisa com tools)
2. Navegar para Dashboard
3. Voltar ao Hermes — deve retomar sessão, mostrar "Respondendo…" ou banner amarelo
4. Resposta deve completar normalmente

### Session busy (não deve mais quebrar)
1. Durante resposta, composer deve estar desabilitado
2. Se aparecer aviso amarelo, usar **Sincronizar**
3. Não deve aparecer erro vermelho "session busy"

### Kanban e Cron
1. Abrir Dashboard — kanban carrega se Hermes online
2. Executar tarefa via Hermes — card deve aparecer em "Em andamento"
3. Cron jobs listados com ações pause/resume/trigger

---

## 10. Decisões de design

1. **`close_on_disconnect: false`** — prioriza continuidade do trabalho do agente sobre economia de recursos no servidor.
2. **Gateway persistente entre rotas** — evita reconexão desnecessária; listeners são reattached ao voltar ao Hermes.
3. **sessionStorage (não localStorage)** — sessão ativa é por aba do browser; fecha ao fechar aba (comportamento desejado).
4. **backgroundNote vs error** — distingue "aguarde, está trabalhando" de "algo deu errado".
5. **Polling 5s no Dashboard** — balance entre frescor e carga; independente do chat WS.

---

## 11. Próximos passos (opcionais, não implementados)

- [ ] Indicador global no sidebar do CaiOS: "Hermes trabalhando…" visível em qualquer página
- [ ] Manter `HermesChatView` montado no layout (hidden) para zero perda de eventos WS
- [ ] Notificação desktop quando tarefa longa terminar
- [ ] Link direto do card Kanban → sessão Hermes que criou a tarefa
- [ ] Página Mission Control unificada com Kanban + Cron (hoje split Dashboard vs Mission Control)

---

## 12. Glossário

| Termo | Significado |
|-------|-------------|
| **Hermes** | Orquestrador de agentes de IA do Caio |
| **Mission Control** | Visão operacional do Hermes (tarefas, cron, status) |
| **Session busy** | Servidor rejeita novo prompt porque sessão já está processando |
| **close_on_disconnect** | Flag do Hermes: se `true`, encerra agente ao fechar WS |
| **persistentGateway** | Instância WS singleton que sobrevive à navegação entre rotas |
| **backgroundNote** | Banner amarelo informativo (não é erro) |
| **Segundo Cérebro** | Grafo de conhecimento CaiOS + Obsidian em `/brain` |

---

## 13. Links relacionados

- [[Hermes + LiveKit]] — experimento anterior com Hermes
- [[arquitetura.md]] — arquitetura do agente de vendas
- [[CaiOS]] — índice do segundo cérebro

---

*Documentado em 2026-06-22 — sessão de desenvolvimento CaiOS + Grok*