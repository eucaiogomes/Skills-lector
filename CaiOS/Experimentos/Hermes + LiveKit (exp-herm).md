---
caios_id: "exp-hermes-livekit"
caios_type: "experiment"
rating: 6
continue: true
project: "Agente de vendas ao vivo"
tools: ["Hermes", "Claude Code"]
tags: ["caios", "experimento"]
created: "2026-06-21T15:27:14.924Z"
updated: "2026-06-21T15:27:14.924Z"
---

# Hermes + LiveKit
Projeto: [[Agente de vendas ao vivo]]
Ferramentas: [[Hermes]] · [[Claude Code]]
## Objetivo
Capturar áudio de chamada e mandar para Hermes sugerir respostas.
## Resultado
Funcionou parcialmente. Latência aceitável, transcrição precisa de ajuste.
**Nota:** 6/5 · **Continuar?** Sim

## Comandos
```
npm run dev
hermes listen --port 8080
```

## Logs
```
Áudio capturado OK. Whisper local com delay de 2s.
```
---
*Gerado automaticamente pelo CaiOS*