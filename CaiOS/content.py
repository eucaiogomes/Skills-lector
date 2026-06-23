"""
content.py — Configuração de Conteúdo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EDITE AQUI: textos, caminhos de imagens, fontes e cores.
NÃO É NECESSÁRIO MEXER NO movie.py para alterar o conteúdo.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ══════════════════════════════════════════════════════════
# CONFIGURAÇÕES GLOBAIS
# ══════════════════════════════════════════════════════════
SETTINGS = {
    "resolution"      : (1920, 1080),
    "fps"             : 30,
    "output_path"     : "output/video_sejaumapessoamelhor_HD.mp4",

    # Fontes — Windows (Ajustado para Segoe Script e Arial)
    "font_handwritten": "C:/Windows/Fonts/segoesc.ttf",
    "font_bold"       : "C:/Windows/Fonts/segoescb.ttf",
    "font_standard"   : "C:/Windows/Fonts/arial.ttf",

    # Textura do quadro branco (Vazio para usar geração procedural no v2.0)
    "whiteboard_texture": "",
    "texture_opacity"   : 0.05,

    # Vinheta nas bordas
    "vignette_intensity": 0.35,

    # Transição entre lições (câmera deslizando pelo canvas)
    "transition_duration": 1.2,
}

# ══════════════════════════════════════════════════════════
# PALETA DE CORES  (R, G, B)
# ══════════════════════════════════════════════════════════
PALETTE = {
    "bg"         : (253, 252, 251),
    "ink"        : (15,  12,  10),
    "red"        : (220, 35,  35),
    "blue"       : (25,  80,  210),
    "blue_light" : (173, 216, 230),
    "green"      : (30,  165, 60),
    "green_v"    : (40,  200, 70),
    "yellow"     : (255, 205, 20),
    "orange"     : (240, 125, 20),
    "gray"       : (155, 155, 155),
    "gray_dark"  : (80,  80,  80),
    "white"      : (255, 255, 255),
    "brown"      : (140, 80,  30),
    "purple"     : (130, 60,  200),
    "pink"       : (255, 180, 195),
}

# ══════════════════════════════════════════════════════════
# INTRO — Painel principal com os 6 temas
# ══════════════════════════════════════════════════════════
INTRO = {
    "titulo_painel": "EXPERIÊNCIA, REFLEXÃO E CONSELHOS",
    "asset_personagem": "assets/imagens/img_01_apresentador.png",
    "labels": [
        ("1 SAÚDE",   "red"),
        ("2 AMBIENTE", "green"),
        ("3 SER VOCÊ", "orange"),
        ("4 LEITURA",  "blue"),
        ("5 ENERGIA",  "green"),
        ("6 BOM DIA",  "yellow"),
    ],
}

# ══════════════════════════════════════════════════════════
# LIÇÕES — Edite textos e caminhos de assets aqui
# ══════════════════════════════════════════════════════════
LESSONS = [

    # ── LIÇÃO 1 ───────────────────────────────────────────
    {
        "id": "01_saude",
        "titulo": "SAÚDE NÃO É UM LUXO, ELA É A BASE",
        "titulo_color": "red",
        "texto_principal": (
            "VOCÊ TEM MUITOS PROBLEMAS ATÉ DESCOBRIR\n"
            "UM PROBLEMA DE SAÚDE.\n"
            "AÍ VOCÊ SÓ TEM UM PROBLEMA!"
        ),
        "balao_texto": "AÇÕES TÊM\nCONSEQUÊNCIAS",
        "assets": {
            "personagem_esq"  : "assets/imagens/img_02_homem_sofa.png",
            "personagem_dir"  : "assets/imagens/img_03_mulher_escritorio.png",
            "decorativo"      : "assets/imagens/img_04_lapide_icones.png",
            "balao"           : "assets/imagens/img_32_nuvem_pensamento.png",
            "icone_sol"       : "assets/imagens/img_33_icone_sol.png",
            "icone_bateria"   : "assets/imagens/img_18_bateria_cheia.png",
            "icone_halter"    : "assets/imagens/img_35_icone_halter.png",
        },
        "transition_out": "down",
    },

    # ── LIÇÃO 2 ───────────────────────────────────────────
    {
        "id": "02_ambiente",
        "titulo": "CONTROLE O SEU AMBIENTE, CONTROLE A SUA VIDA",
        "titulo_color": "red",
        "texto_principal": (
            "FAÇO TUDO O QUE FOR PRECISO PARA\n"
            "FACILITAR OS BONS HÁBITOS\n"
            "E CRIO OBSTÁCULOS PARA OS MAUS HÁBITOS"
        ),
        "balao_texto": "NÃO QUERO\nISIS!!!",
        "assets": {
            "personagem_centro": "assets/imagens/img_05_homem_em_pe.png",
            "cerebro_bateria"  : "assets/imagens/img_07_cerebro_bateria.png",
            "geladeira"        : "assets/imagens/img_09_geladeira.png",
            "comida_saudavel"  : "assets/imagens/img_28_comida_saudavel.png",
            "refrigerante"     : "assets/imagens/img_06_garrafa_refrigerante.png",
            "doces"            : "assets/imagens/img_08_doces_proibidos.png",
            "marca_x"          : "assets/imagens/img_48_marca_x_vermelho.png",
            "balao"            : "assets/imagens/img_46_balao_fala_retangular.png",
        },
        "transition_out": "right",
    },

    # ── LIÇÃO 3 ───────────────────────────────────────────
    {
        "id": "03_autenticidade",
        "titulo": "NÃO MINTA PARA SI MESMO",
        "titulo_color": "red",
        "texto_principal": (
            "ATRAI PESSOAS QUE GOSTAM DE VOCÊ\n"
            "PELO QUE VOCÊ É DE VERDADE"
        ),
        "texto_apoio_esq": "BASTA FALAR E FAZER\nO QUE OS OUTROS QUEREM",
        "texto_apoio_dir": "MAS É MELHOR\nSER VOCÊ MESMO!",
        "assets": {
            "cena_reuniao"       : "assets/imagens/img_10_reuniao_palitos.png",
            "personagem_isolado" : "assets/imagens/img_11_palito_isolado.png",
            "personagem_social"  : "assets/imagens/img_12_palitos_conectados.png",
            "seta_transicao"     : "assets/imagens/img_29_seta_azul.png",
        },
        "transition_out": "up",
    },

    # ── LIÇÃO 4 ───────────────────────────────────────────
    {
        "id": "04_leitura",
        "titulo": "LEIA SEMPRE",
        "titulo_color": "red",
        "texto_esq": (
            "A CADA PÁGINA LIDA,\n"
            "VOCÊ ESTÁ BAIXANDO\n"
            "A SABEDORIA DE UMA\n"
            "VIDA INTEIRA DE\n"
            "OUTRA PESSOA"
        ),
        "texto_dir": (
            "CADA LIVRO É UM\n"
            "CÉREBRO INTEIRO\n"
            "TE ENSINANDO O QUE\n"
            "LEVOU DÉCADAS\n"
            "PRA APRENDER"
        ),
        "assets": {
            "cabeca_cerebro"  : "assets/imagens/img_13_cabeca_cerebro.png",
            "pilha_livros"    : "assets/imagens/img_14_pilha_livros.png",
            "homem_escalando" : "assets/imagens/img_15_homem_escalando.png",
            "multidao"        : "assets/imagens/img_16_multidao_base.png",
        },
        "transition_out": "left",
    },

    # ── LIÇÃO 5 ───────────────────────────────────────────
    {
        "id": "05_energia",
        "titulo": "GERENCIE SUA ENERGIA, NÃO O SEU TEMPO",
        "titulo_color": "red",
        "labels": {
            "eficiencia" : "MAIS EFICIÊNCIA",
            "producao"   : "PRODUZ MAIS EM\nMENOS TEMPO",
            "timing"     : "TRABALHAR NO\nMOMENTO CERTO",
        },
        "assets": {
            "despertador"      : "assets/imagens/img_17_despertador.png",
            "bateria_cheia"    : "assets/imagens/img_18_bateria_cheia.png",
            "bateria_metade"   : "assets/imagens/img_19_bateria_metade.png",
            "quadro_sol"       : "assets/imagens/img_20_quadro_sol.png",
            "quadro_chuva"     : "assets/imagens/img_21_quadro_chuva.png",
            "personagem_ativo" : "assets/imagens/img_22_homem_energizado.png",
            "personagem_exausto": "assets/imagens/img_23_homem_exausto.png",
        },
        "transition_out": "down",
    },

    # ── LIÇÃO 6 ───────────────────────────────────────────
    {
        "id": "06_bom_dia",
        "titulo": "TENHA UM BOM DIA, E VOCÊ TERÁ UMA BOA VIDA",
        "titulo_color": "red",
        "texto_principal": "ENCONTRE SATISFAÇÃO NO SIMPLES",
        "grid": {
            "rows"    : 30,
            "cols"    : 52,
            "label_x" : "SEMANA DO ANO →",
        },
        "assets": {
            "personagem_triste" : "assets/imagens/img_24_homem_cinza.png",
            "personagem_feliz"  : "assets/imagens/img_25_homem_euforico.png",
            "trabalhador"       : "assets/imagens/img_26_homem_escritorio_joia.png",
            "logo_cerebro"      : "assets/imagens/img_27_logo_cerebro_lampada.png",
            "logo_texto"        : "assets/imagens/img_31_emoji_gigante.png", # Ajustado para o emoji
        },
        "transition_out": None,
    },
]

# ══════════════════════════════════════════════════════════
# FINAL — Tela de encerramento / logo
# ══════════════════════════════════════════════════════════
FINAL = {
    "nome_canal" : "SejaUmaPessoaMelhor",
    "subtitulo"  : "seja uma pessoa melhor",
    "asset_logo" : "assets/imagens/img_27_logo_cerebro_lampada.png",
    "asset_texto": "assets/imagens/img_59_logo_texto.png",
}
