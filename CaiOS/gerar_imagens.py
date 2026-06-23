import os
import re
import io
import time
import requests
from pathlib import Path
from rembg import remove
from PIL import Image
from dotenv import load_dotenv

# Carrega as chaves do arquivo .env (se existir)
load_dotenv()

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================
ARQUIVO_ENTRADA = "imagens.txt"
DIRETORIO_SAIDA = "assets/imagens"

# Configuração Cloudflare AI
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")

# Usando o modelo livre do Cloudflare para Stable Diffusion
CF_MODEL = "@cf/stabilityai/stable-diffusion-xl-base-1.0"
CF_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}" if CF_ACCOUNT_ID else ""


def extrair_prompts_do_arquivo(caminho_arquivo):
    """
    Lê o arquivo de texto com as listas de imagens (mesmo se estiver fragmentado)
    e extrai todos os IDs e Prompts de geração via Regex.
    """
    if not os.path.exists(caminho_arquivo):
        print(f"[ERRO] Arquivo '{caminho_arquivo}' não encontrado.")
        return []

    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Regex para capturar os IDs e os Prompts dentro dos JSONs
    padrao = re.compile(
        r'"id":\s*"([^"]+)",\s*"(?:quadro_referencia)":\s*"[^"]*",\s*"prompt_geracao":\s*"([^"]+)"'
    )
    
    imagens = []
    for match in padrao.finditer(conteudo):
        imagens.append({
            "id": match.group(1),
            "prompt": match.group(2)
        })
    
    return imagens

def gerar_imagem_stable_diffusion(prompt):
    """
    Chama a API do Cloudflare AI para gerar a imagem base com SD.
    """
    if not CF_ACCOUNT_ID or not CF_API_TOKEN:
        raise ValueError("ERRO: Credenciais 'CF_ACCOUNT_ID' ou 'CF_API_TOKEN' não encontradas no .env")

    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}"
    }

    # Adicionamos um sufixo para garantir clareza no estilo lousa e fundo branco
    prompt_completo = f"{prompt}, centered, high contrast, pure white solid background, high quality, sharp focus"

    # Negative prompt para forçar fundo limpo e sem artefatos ou sombras
    negative_prompt = "shadows, gray, textures, photorealistic, complex, noise, blur, dithered, gradient"

    payload = {
        "prompt": prompt_completo,
        "negative_prompt": negative_prompt
    }

    print(f"    -> Conectando ao Cloudflare AI para gerar a imagem...")
    resposta = requests.post(CF_URL, headers=headers, json=payload)
    
    if resposta.status_code != 200:
        raise Exception(f"Erro na API Cloudflare: {resposta.text}")
    
    # A API Text-to-Image do Cloudflare entrega os próprios bytes da imagem como resposta
    return resposta.content

def processar_e_salvar_imagem(image_bytes, caminho_saida):
    """
    Salva a imagem gerada diretamente, sem remover o fundo.
    """
    print(f"    -> Salvando imagem original (sem remoção de fundo)...")
    with open(caminho_saida, "wb") as f:
        f.write(image_bytes)
    print(f"    -> [SUCESSO] Salva em: {caminho_saida}")

def main():
    print("=========================================================")
    print(" INICIANDO PIPELINE DE GERAÇÃO E RECORTE DE IMAGENS (SD) ")
    print("=========================================================")

    # 1. Preparar pastas
    os.makedirs(DIRETORIO_SAIDA, exist_ok=True)
    
    # 2. Extrair prompts
    imagens_para_gerar = extrair_prompts_do_arquivo(ARQUIVO_ENTRADA)
    total = len(imagens_para_gerar)
    
    if total == 0:
        print("[AVISO] Nenhuma imagem encontrada para processar. Verifique o arquivo imagens.txt.")
        return

    print(f"-> Total de imagens identificadas: {total}")
    
    # 3. Processamento em Batch
    for indice, item in enumerate(imagens_para_gerar, start=1):
        id_imagem = item["id"]
        prompt = item["prompt"]
        
        caminho_destino = Path(DIRETORIO_SAIDA) / f"{id_imagem}.png"
        
        print(f"\n[{indice}/{total}] Processando imagem: {id_imagem}")
        
        # Pula se já existe no diretório para não gastar créditos
        if caminho_destino.exists():
            print(f"    -> [SKIPPED] Imagem '{id_imagem}.png' já existe na pasta de assets.")
            continue
            
        print(f"    -> Prompt: '{prompt}'")
        
        try:
            # Etapa 1: Gerar a imagem com bordas brancas usando IA (Stable Diffusion)
            image_bytes = gerar_imagem_stable_diffusion(prompt)
            
            # Etapa 2: Remover fundo e salvar no diretório em PNG
            processar_e_salvar_imagem(image_bytes, caminho_destino)
            
            # Pausa breve para respeitar limites da API (Rate Limiting)
            time.sleep(1)
            
        except Exception as e:
            print(f"    -> [ERRO ao processar '{id_imagem}']: {e}")

if __name__ == "__main__":
    main()
