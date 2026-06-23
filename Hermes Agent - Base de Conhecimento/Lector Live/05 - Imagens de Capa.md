# Imagens de Capa para Treinamentos

## Objetivo

Criar capas profissionais para treinamentos do Lector Live, alinhadas ao tema e ao nome editorial do curso.

## Padrão de qualidade

A capa deve:

- comunicar o tema do treinamento;
- parecer profissional;
- funcionar em miniatura;
- não depender de texto gerado por IA;
- não ter logotipos indevidos;
- ter contraste adequado;
- combinar com título, descrição e conteúdo.

## Geração por IA

Quando disponível, usar `image_generate` com prompt específico.

Exemplo para programação:

```text
Imagem de capa profissional para um treinamento online chamado "Lógica de Programação: Fundamentos Essenciais". Estilo moderno de educação em tecnologia, fundo azul escuro com gradientes roxo e ciano, fluxogramas abstratos, blocos lógicos, pseudocódigo sutil, ícones de decisão e sequência, sensação de clareza e aprendizado. Sem texto legível, sem logotipos, sem pessoas reais, alta qualidade, clean, corporativo, 16:9.
```

## Fallback local

Se o gerador externo estiver indisponível, usar Python/Pillow para gerar capa local.

Foi validado um fallback com:

- imagem 1600x900;
- gradiente azul/roxo/ciano;
- fluxogramas;
- painel de pseudocódigo;
- texto controlado.

Arquivo gerado no exemplo:

```text
C:\Users\gcaio\logica_programacao_fundamentos_essenciais_capa.png
```

## Upload para o Lector

Endpoint validado:

```text
POST /lector-web-service/courses/thumbset/{courseId}/{version}
```

Campos multipart:

```text
square
banner
cover
squareRemoved=false
bannerRemoved=false
coverRemoved=false
```

Execução validada:

```text
courseId: 1481255
version: 1
status: 200
```

## Boas práticas

- Gerar `cover` e `banner` em 16:9.
- Gerar `square` com crop centralizado.
- Evitar texto pequeno demais.
- Se usar IA, evitar texto dentro da imagem.
- Se precisar de texto, adicionar via Pillow para controle total.

## Exemplo validado — RH e IA

Treinamento:

```text
IA no RH: Trabalho Humano-Máquina e Liderança Estratégica
```

Conceito visual:

- rede humano-máquina;
- chip central com `AI`;
- formas abstratas representando pessoas e conexões;
- fundo azul/verde corporativo;
- texto controlado por Pillow para evitar erros de IA generativa.

Arquivos locais gerados no diretório:

```text
/c/Users/gcaio/agent-tools/lector-training-build/rh-ia-trabalho-humano-maquina-2026
```

Arquivos:

```text
ia_no_rh_trabalho_humano_maquina_lideranca_estrategica_cover.png
ia_no_rh_trabalho_humano_maquina_lideranca_estrategica_banner.png
ia_no_rh_trabalho_humano_maquina_lideranca_estrategica_square.png
```

Upload validado:

```text
courseId: 1481257
version: 1
status: 200
```

Observação: o endpoint de upload `thumbset` retornando `200` é a validação direta do envio. O `GET /courses/{id}` pode não retornar imediatamente chaves de thumb preenchidas.
