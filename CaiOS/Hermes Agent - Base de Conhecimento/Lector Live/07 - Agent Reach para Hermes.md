# Agent Reach para Hermes

Criado em: 2026-06-20 17:14:03

## Resumo

O repositório `Panniantong/Agent-Reach` foi clonado, instalado e integrado ao Hermes como uma camada adicional de busca/leitura na internet. Ele não substitui as ferramentas nativas do Hermes; funciona como um roteador/diagnosticador de backends externos para várias plataformas.

Repositório local:

```text
C:\Users\gcaio\Agent-Reach
```

Ambiente virtual:

```text
C:\Users\gcaio\.agent-reach-venv
```

Skill local instalada no Hermes:

```text
C:\Users\gcaio\AppData\Local\hermes\skills\research\agent-reach
```

Para o Hermes carregar a nova skill em sessões já abertas, usar `/reload-skills`; em novas sessões ela deve aparecer automaticamente como `agent-reach`.

## Funcionalidades adicionadas ao Hermes

| Área | O que adiciona | Status atual |
|---|---|---|
| Busca web sem API key | Exa Search via `mcporter` | Funcionando |
| Leitura de páginas web | Jina Reader via `curl https://r.jina.ai/...` | Funcionando |
| YouTube | Metadados e legendas via `yt-dlp` | Funcionando |
| RSS/Atom | Leitura de feeds via `feedparser` | Funcionando |
| GitHub | Acesso via `gh` CLI | Instalado, precisa `gh auth login` para uso completo |
| Bilibili | Busca básica via API pública | Funcionando |
| V2EX | API pública de tópicos | Detectado, mas com erro SSL no momento |
| Twitter/X | Busca/leitura via `twitter-cli` ou OpenCLI | Opcional, não instalado |
| Reddit | Busca/leitura com login via OpenCLI ou `rdt-cli` | Opcional, não instalado |
| XiaoHongShu / 小红书 | Busca/leitura via OpenCLI ou MCP | Opcional, não instalado |
| LinkedIn | Leitura básica/Jina ou MCP completo | Opcional, não instalado |
| Xueqiu / 雪球 | Ações e comunidade com cookie | Precisa login/cookie |
| Xiaoyuzhou Podcast / 小宇宙 | Transcrição com Whisper/Groq | Opcional, não instalado |
| Diagnóstico | `agent-reach doctor` | Funcionando |
| Skill para agentes | Instruções de roteamento para o Hermes | Instalada |
| Monitoramento | `agent-reach watch` e `agent-reach check-update` | Disponível |

## Status real verificado

Comando executado:

```bash
agent-reach doctor --json
```

Resumo:

```text
github       warn  gh CLI instalado, mas não autenticado
youtube      ok    yt-dlp
bilibili     ok    B站搜索 API
rss          ok    feedparser
exa_search   ok    Exa via mcporter
web          ok    Jina Reader
v2ex         warn  erro SSL/certificado
twitter      warn  backend não instalado
reddit       off   backend não instalado
xiaohongshu  off   backend não instalado
linkedin     off   backend não configurado
xiaoyuzhou   off   script/API key não configurados
xueqiu       warn  precisa login/cookie
```

## Testes executados

### 1. Exa Search

```bash
mcporter call exa.web_search_exa query='Agent Reach GitHub internet capability router' numResults=1
```

Resultado: retornou o repositório/README do Agent Reach no GitHub, com descrição e highlights. Funcionando.

### 2. Exa Fetch

```bash
mcporter call exa.web_fetch_exa urls='["https://github.com/Panniantong/Agent-Reach"]' maxCharacters=800
```

Resultado: retornou dados reais do repositório, incluindo nome, descrição, estrelas, linguagem principal e licença. Funcionando.

### 3. Leitura web via Jina Reader

```bash
curl -L -s 'https://r.jina.ai/http://r.jina.ai/http://example.com'
```

Resultado: retornou conteúdo em Markdown do Example Domain. Funcionando.

### 4. RSS

```python
import feedparser
feed = feedparser.parse("https://hnrss.org/frontpage")
```

Resultado verificado:

```text
feed_title= Hacker News: Front Page
entries= 20
```

Funcionando.

### 5. YouTube via yt-dlp

```bash
yt-dlp --skip-download --dump-json 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
```

Resultado verificado:

```text
OK title= Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)
id= dQw4w9WgXcQ
```

Funcionando.

### 6. Bilibili API

Endpoint equivalente ao usado pelo `doctor`:

```text
https://api.bilibili.com/x/web-interface/search/all/v2?keyword=test&page=1
```

Resultado verificado:

```text
code= 0
has data= True
```

Funcionando para busca básica.

### 7. GitHub CLI

```bash
gh --version
```

Resultado:

```text
gh version 2.95.0
```

Ao tentar usar dados GitHub via `gh`, o CLI pediu autenticação:

```text
To get started with GitHub CLI, please run: gh auth login
```

Conclusão: instalado, mas precisa login para uso completo.

## Exemplo prático para testar tudo em uma tarefa real

Pedido sugerido ao Hermes:

> Use Agent Reach para pesquisar o repositório Agent-Reach, ler a página do GitHub, encontrar menções recentes sobre ferramentas de busca para agentes, verificar um vídeo do YouTube relacionado a AI agents e resumir tudo em uma comparação curta.

Esse teste exercita:

1. Exa Search para busca ampla.
2. Exa Fetch para ler páginas encontradas.
3. Jina Reader para ler URL direta.
4. GitHub/gh ou Exa Fetch para inspecionar repositório.
5. YouTube/yt-dlp para extrair metadados ou legendas.
6. RSS se for adicionada uma fonte como Hacker News.
7. `agent-reach doctor` para decidir quais backends usar.

## Roteiro direto de teste

```bash
agent-reach doctor

mcporter call exa.web_search_exa query='best AI agent internet search tools Agent Reach Exa MCP' numResults=3

mcporter call exa.web_fetch_exa urls='["https://github.com/Panniantong/Agent-Reach"]' maxCharacters=1200

curl -L -s 'https://r.jina.ai/http://r.jina.ai/http://example.com'

python -c "import feedparser; f=feedparser.parse('https://hnrss.org/frontpage'); print(f.feed.get('title'), len(f.entries), f.entries[0].title if f.entries else 'none')"

yt-dlp --skip-download --dump-json 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
```

## Próximos desbloqueios opcionais

Para GitHub completo:

```bash
gh auth login
```

Para redes sociais e backends desktop:

```bash
agent-reach install --env=auto --channels=opencli
```

O OpenCLI pode desbloquear Reddit, XiaoHongShu, Bilibili avançado e fallback para Twitter usando sessão do navegador.

## Links relacionados

- [[00 - Índice]]
- [[06 - Soul do Agente]]
