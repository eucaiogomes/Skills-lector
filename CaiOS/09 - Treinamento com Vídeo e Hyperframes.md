# Treinamento com Vídeo e Hyperframes (com Narração)

Atualizado em: 2026-06-20

## Objetivo

Registrar o fluxo validado para criar treinamentos baseados em **vídeo** no Lector Live, usando Hyperframes para gerar o vídeo determinístico + narração, em vez de SCORM.

## Quando usar vídeo em vez de SCORM

- Conteúdo mais dinâmico, com narração falada.
- Quando o público responde melhor a formato de vídeo curto/formatado.
- Para temas que precisam de "voz" (explicação falada, tom mais humano).
- Quando não é necessário rastreamento avançado de SCO (o Lector trata vídeo local como DocumentResource).

## Fluxo validado (LGPD 2026)

**Tema criado:**
```
LGPD em 2026: Governança, IA e Privacidade na Prática
```

**Por que este tema:**
Pesquisa mostrou que em 2026 LGPD saiu da fase de "política no site" para exigência de governança prática, especialmente com IA, dados sensíveis e resposta a incidentes.

## Ferramenta usada para o vídeo

**Hyperframes** (`hyperframes.video`)

- Escreve HTML com `data-*` attributes para timing, animações e composição.
- Renderiza MP4 determinístico (mesmos bytes em máquinas diferentes).
- Suporta narração separada (TTS ou arquivo de áudio).
- CLI: `hyperframes render`, `hyperframes tts`, `hyperframes lint`, etc.

**Processo usado:**
1. Criar narração em texto.
2. Gerar áudio de narração (Hermes TTS ou Hyperframes tts).
3. Criar `index.html` com composição (div root com `data-duration`, `data-width`, `data-height`, `data-fps` + elementos com `data-start` / `data-duration`).
4. Renderizar MP4 silencioso com Hyperframes.
5. Muxar áudio com `ffmpeg`.
6. Validar duração e qualidade.

**Resultado do vídeo LGPD:**
- Duração: 83 segundos
- Resolução: 1920x1080
- Tamanho: ~6.1 MB
- Formato: MP4 (H.264 + AAC)

## Como o Lector trata vídeos locais

Vídeos enviados diretamente (não YouTube/Vimeo) devem ser tratados como:

```json
{
  "@class": "DocumentResource",
  "type": "DOCUMENT",
  "path": "/Pasta/LGPD_2026_Video.mp4.lmp4",
  "document": { ... metadados do documento ... }
}
```

**Importante:**
- Extensão **.mp4.lmp4** (o Lector converte/empacota como .lmp4 internamente).
- Não use `SCOResource` para vídeo simples.
- O player do Lector abre o vídeo no mesmo estilo dos documentos de vídeo.

## Publicação validada

```text
courseId: 1481259
version: 1
title: LGPD em 2026: Governança, IA e Privacidade na Prática
resource @class: DocumentResource
video path: /LGPD 2026/LGPD_Governanca_IA_Privacidade_2026.mp4.lmp4
thumbset: 200 (capa enviada com sucesso)
```

## Artefatos locais do fluxo de vídeo

Estrutura típica:
```
lgpd-video-hyperframes/
├── index.html              # Composição Hyperframes
├── narration.txt           # Texto da narração
├── narration.mp3           # Áudio gerado
├── lgpd_governanca_ia_privacidade_video.mp4          # Vídeo final com áudio
├── lgpd_cover.png          # Capa principal 16:9
├── lgpd_square.png
├── lgpd_banner.png
└── publish_lgpd_video.py   # Script de upload + criação (sem credencial)
```

## Diferenças importantes SCORM vs Vídeo

| Aspecto              | SCORM                          | Vídeo (Hyperframes)                  |
|----------------------|--------------------------------|--------------------------------------|
| Tipo de recurso      | SCOResource                    | DocumentResource                     |
| Extensão             | .scorm                         | .mp4.lmp4                            |
| Rastreamento         | Completo (SCO)                 | Básico (progresso de vídeo)          |
| Criação de conteúdo  | HTML + JS + manifest           | HTML + render Hyperframes + narração |
| Ideal para           | Conteúdo interativo + quiz     | Explicação falada + visual dinâmico  |

## Recomendação de fluxo completo

1. Pesquisar tendências (`agent-reach` + `lector-kb-search`).
2. Curar título editorial.
3. Decidir: SCORM ou Vídeo?
4. Se vídeo:
   - Escrever narração.
   - Criar composição HTML com Hyperframes.
   - Gerar áudio.
   - Renderizar + muxar.
   - Validar MP4.
5. Gerar capa profissional.
6. Fazer upload do conteúdo (SCORM ou vídeo).
7. Criar curso via `saveCourse` com o recurso correto.
8. Incluir turma gratuita.
9. Enviar capa via `thumbset`.
10. Validar por API.
11. Registrar aprendizado na base.

## Lições aprendidas

- Sempre usar `DocumentResource` + extensão `.lmp4` para vídeos locais enviados.
- Hyperframes exige `data-duration`, `data-width`, `data-height` e `data-fps` no elemento raiz da composição (`<div data-composition-id="...">`).
- Render em máquinas com pouca RAM pode ser lento → usar `--low-memory-mode --quality draft` para testes.
- Narração pode ser gerada fora (TTS do Hermes) e muxada depois.
- Validar o vídeo final com `ffprobe` antes do upload.

## Skills relacionadas

- `lector-pesquisar-tendencias-criar-treinamento` (atualizada para suportar vídeo)
- `lector-portal-9-criar-treinamentos`
- `lector-upload-documentos-scorms`
- `lector-criar-imagens-capa`
- Nova skill recomendada: `lector-criar-treinamento-video-hyperframes`

## Exemplo de uso futuro

Usuário pede: "Pesquise tendências de [tema] e crie um treinamento em vídeo com narração."

Agente deve:
1. Usar pesquisa.
2. Curar nome.
3. Gerar narração + composição Hyperframes.
4. Renderizar vídeo.
5. Seguir o fluxo acima com `DocumentResource`.
6. Documentar na base.

---

**Lição principal:**  
Para treinamentos que precisam de voz e dinamismo visual, o caminho **Hyperframes + narração + DocumentResource .lmp4** é mais leve e eficaz que SCORM.