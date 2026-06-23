import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys, math, textwrap, time, re, json
from brain_logger import OrionBrain
from assets_manager import AssetsManager

# ══════════════════════════════════════════════════════════
# CONFIG GLOBAL (Default, será sobrescrita pelo JSON se houver)
# ══════════════════════════════════════════════════════════
W, H   = 1920, 1080
FPS    = 30
ASSETS = os.path.join("assets", "imagens")
OUT    = "output"
os.makedirs(OUT, exist_ok=True)

# Fontes padrão do Windows
FONT_BOLD   = r"C:\Windows\Fonts\arialbd.ttf"
FONT_NORMAL = r"C:\Windows\Fonts\arial.ttf"

# ══════════════════════════════════════════════════════════
# EASING & MATH
# ══════════════════════════════════════════════════════════
def ease_in_out_cubic(t):
    t = max(0.0, min(1.0, t))
    if t < 0.5: return 4 * t * t * t
    return 1 - (-2 * t + 2) ** 3 / 2

def ease_out_back(t, s=1.70158):
    t = max(0.0, min(1.0, t))
    return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2

def ease_out_quad(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 2

def ease_out_elastic(t):
    t = max(0.0, min(1.0, t))
    if t == 0: return 0
    if t == 1: return 1
    p = 0.3
    s = p / 4
    return (2**(-10*t) * math.sin((t-s)*(2*math.pi)/p) + 1)

def lerp(a, b, t): return a + (b - a) * t

# ══════════════════════════════════════════════════════════
# VIRTUAL CAMERA
# ══════════════════════════════════════════════════════════
class VirtualCamera:
    """Núcleo da Câmera Virtual [ORION-WHITEBOARD]"""
    def __init__(self, w=1920, h=1080):
        self.w, self.h = w, h
        self.x, self.y = w // 2, h // 2
        self.zoom = 1.0

    def apply(self, canvas):
        """Aplica Pan e Zoom ao Canvas Infinito."""
        # Crop e Resize para simular Zoom
        cw, ch = int(self.w / self.zoom), int(self.h / self.zoom)
        left = max(0, self.x - cw // 2)
        top = max(0, self.y - ch // 2)
        right = min(canvas.width, left + cw)
        bottom = min(canvas.height, top + ch)
        
        view = canvas.crop((left, top, right, bottom))
        return view.resize((self.w, self.h), Image.BILINEAR)

def get_pos(ev, t_rel, dur_total):
    """Calcula a posição dinâmica com base em keyframes ou posicao_inicial/final"""
    if "posicao" in ev:
        p = ev["posicao"]
        if p == ["center", "center"]: return (W//2, H//2)
        if isinstance(p, list) and p[0] == "center": return (W//2, p[1])
        if isinstance(p, list) and p[1] == "center": return (p[0], H//2)
        return tuple(p)
    
    p_init = ev.get("posicao_inicial", [0, 0])
    p_final = ev.get("posicao_final", [0, 0])
    
    # Se houver keyframes, a lógica fica mais complexa, mas vamos simplificar para lerp inicial/final por enquanto
    # a menos que o tempo t_rel exija keyframes específicos
    progress = t_rel / dur_total if dur_total > 0 else 1.0
    progress = ease_in_out_cubic(progress)
    
    kx = lerp(p_init[0], p_final[0], progress)
    ky = lerp(p_init[1], p_final[1], progress)
    return (int(kx), int(ky))

# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════
def get_font(size, bold=False):
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT_NORMAL, int(size))
    except:
        return ImageFont.load_default()

def extrair_timelines(caminho_arquivo):
    """Busca blocos JSON de timeline de forma robusta."""
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        conteudo = f.read()

    eventos_totais = []
    config_global = {"resolucao": [1920, 1080], "fps": 30, "cor_fundo": "#FFFFFF"}
    
    decoder = json.JSONDecoder()
    pos = 0
    while pos < len(conteudo):
        match = re.search(r'\{', conteudo[pos:])
        if not match: break
        
        start_index = pos + match.start()
        try:
            obj, end_index = decoder.raw_decode(conteudo[start_index:])
            
            def processar_objeto(d):
                nonlocal config_global
                if isinstance(d, dict):
                    if "configuracoes_globais" in d:
                        config_global.update(d["configuracoes_globais"])
                    if "trilha_principal" in d:
                        eventos_totais.extend(d["trilha_principal"])
                    for v in d.values():
                        processar_objeto(v)

            processar_objeto(obj)
            pos = start_index + end_index
        except json.JSONDecodeError:
            pos = start_index + 1
            
    return eventos_totais, config_global

# ══════════════════════════════════════════════════════════
# ENGINE
# ══════════════════════════════════════════════════════════
class VideoEngine:
    def __init__(self, eventos, config):
        self.eventos = eventos
        self.config = config
        self.cache_assets = {}
        self.W, self.H = config.get("resolucao", [1920, 1080])
        self.cor_fundo = config.get("cor_fundo", "#FFFFFF")
        
        # Supercérebro [ORION-WHITEBOARD]
        self.brain = OrionBrain()
        self.assets = AssetsManager()
        self.camera = VirtualCamera(self.W, self.H)
        
        if self.cor_fundo.startswith("#"):
            self.cor_fundo = tuple(int(self.cor_fundo[i:i+2], 16) for i in (1, 3, 5))
        else:
            self.cor_fundo = (255, 255, 255)
            
        self.duracao_total = max([e.get("end_time", 0) for e in eventos]) if eventos else 0

    def reveal_organic(self, img, progress):
        """Luma Matte / Alpha Masking profissional via OpenCV/PIL."""
        # Gerar uma máscara de gradiente de revelação (ex: ruído ou varredura)
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        # Varredura horizontal orgânica
        rw = int(img.width * progress)
        draw.rectangle([0, 0, rw, img.height], fill=255)
        # Suavização para efeito "Whiteboard"
        mask = mask.filter(ImageFilter.GaussianBlur(3))
        return mask

    def load_image(self, asset_id):
        if asset_id in self.cache_assets: return self.cache_assets[asset_id]
        path = os.path.join(ASSETS, f"{asset_id}.png")
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            self.cache_assets[asset_id] = img
            return img
        return None

    def render_frame(self, t):
        # Canvas base
        canvas = Image.new("RGBA", (self.W, self.H), self.cor_fundo + (255,))
        
        # Filtrar eventos ativos no tempo t
        ativos = [e for e in self.eventos if e["start_time"] <= t <= e["end_time"]]
        # Ordenar por camada
        ativos.sort(key=lambda x: x.get("camada", 0))

        for ev in ativos:
            tipo = ev.get("tipo_midia", "imagem")
            
            # 1. Posição e Escala
            t_rel = t - ev["start_time"]
            dur_total_ev = ev["end_time"] - ev["start_time"]
            px, py = get_pos(ev, t_rel, dur_total_ev)
            escala = ev.get("escala", 1.0)
            
            # Progressão do efeito de entrada
            efeito_cfg = ev.get("efeito_entrada", {})
            dur_efeito = efeito_cfg.get("duracao", 0.5)
            progress = min(1.0, t_rel / dur_efeito) if dur_efeito > 0 else 1.0
            
            if "imagem" in tipo:
                img = self.load_image(ev["asset_id"])
                if not img: continue
                
                # Redimensionamento
                nw, nh = int(img.width * escala), int(img.height * escala)
                img_res = img.resize((nw, nh), Image.BILINEAR)
                
                efeito = efeito_cfg.get("tipo", "fadein")
                
                if efeito == "pop_in":
                    p_ease = ease_out_back(progress)
                    nw2, nh2 = max(1, int(nw * p_ease)), max(1, int(nh * p_ease))
                    img_ready = img_res.resize((nw2, nh2), Image.BILINEAR)
                    canvas.paste(img_ready, (px - nw2//2, py - nh2//2), img_ready)
                
                elif efeito == "mask_reveal_box":
                    p_ease = ease_in_out_cubic(progress)
                    rw = int(nw * p_ease)
                    if rw > 0:
                        crop = img_res.crop((0, 0, rw, nh))
                        canvas.paste(crop, (px - nw//2, py - nh//2), crop)
                
                elif efeito == "mask_reveal_radial":
                    p_ease = ease_out_quad(progress)
                    mask = Image.new("L", (nw, nh), 0)
                    draw_m = ImageDraw.Draw(mask)
                    max_r = int(math.hypot(nw, nh) * p_ease)
                    draw_m.ellipse([nw//2-max_r, nh//2-max_r, nw//2+max_r, nh//2+max_r], fill=255)
                    mask = mask.filter(ImageFilter.GaussianBlur(5))
                    canvas.paste(img_res, (px - nw//2, py - nh//2), mask)
                
                else: # fadein
                    p_ease = ease_out_quad(progress)
                    r,g,b,a = img_res.split()
                    new_a = a.point(lambda x: int(x * p_ease))
                    mask = Image.merge("L", (new_a,))
                    canvas.paste(img_res, (px - nw//2, py - nh//2), mask)

            elif tipo == "texto":
                d = ImageDraw.Draw(canvas)
                fnt = get_font(ev.get("tamanho", 30), ev.get("peso") == "bold")
                cor_str = ev.get("cor", "#000000")
                cor = tuple(int(cor_str[i:i+2], 16) for i in (1, 3, 5)) if cor_str.startswith("#") else (0,0,0)
                
                conteudo = ev.get("conteudo", "")
                efeito = efeito_cfg.get("tipo", "fadein")
                
                visible = conteudo[:int(len(conteudo) * ease_out_quad(progress))] if efeito == "typewriter" else conteudo
                
                bb = d.multiline_textbbox((0,0), visible, font=fnt)
                tw, th = bb[2]-bb[0], bb[3]-bb[1]
                
                # Suporte a centralização baseada na chave "posicao" se ela existir
                pos_conf = ev.get("posicao", [0, 0])
                tx = px - tw//2 if isinstance(pos_conf, list) and pos_conf[0] == "center" else px
                ty = py - th//2 if isinstance(pos_conf, list) and len(pos_conf)>1 and pos_conf[1] == "center" else py
                
                d.multiline_text((tx, ty), visible, font=fnt, fill=cor + (int(255 * min(1, progress*2)),))

        # Aplica a Câmera Virtual Antes de Retornar
        final_view = self.camera.apply(canvas)
        return final_view.convert("RGB")

def main():
    print("🚀 Iniciando Motor de Renderização SuperCérebro [ORION-WHITEBOARD]...")
    eventos, config = extrair_timelines("imagens.txt")
    if not eventos:
        print("❌ Erro: Nenhuma timeline válida encontrada!")
        return

    engine = VideoEngine(eventos, config)
    W, H = engine.W, engine.H
    FPS = config.get("fps", 30)
    
    # Log de Inicialização no Obsidian
    engine.brain.log_decision(
        title="Sessão de Renderização Whiteboard",
        decision=f"Iniciando renderização de {len(eventos)} eventos em {W}x{H}.",
        json_data=config,
        python_code="engine.render_frame(t)",
        rationale="Validando a integração da Câmera Virtual e do Logger Neural no pipeline principal.",
        related_links="[[Virtual Camera Core]], [[Alpha Masking com OpenCV]]"
    )
    def get_fourcc():
        """Tenta encontrar um codec de vídeo compatível, priorizando H.264 (avc1) para melhor suporte em players modernos e IDEs."""
        codecs = [('avc1', '.mp4'), ('X264', '.mp4'), ('mp4v', '.mp4')]
        for codec, ext in codecs:
            fcc = cv2.VideoWriter_fourcc(*codec)
            # Teste rápido de criação (opcional, mas vamos tentar o fcc direto)
            if fcc != -1: return fcc
        return cv2.VideoWriter_fourcc(*'mp4v')

    out_path = os.path.join(OUT, "video_final.mp4")
    fourcc = get_fourcc()
    vw = cv2.VideoWriter(out_path, fourcc, FPS, (W, H))
    
    total_frames = int(engine.duracao_total * FPS)
    print(f"📹 Renderizando {total_frames} frames em {W}x{H} @ {FPS}fps...", flush=True)
    
    t0 = time.time()
    for f in range(total_frames):
        t = f / FPS
        img_frame = engine.render_frame(t)
        vw.write(cv2.cvtColor(np.array(img_frame), cv2.COLOR_RGB2BGR))
        if f % 10 == 0:
            print(f"   -> Progresso: {(f/total_frames)*100:.1f}% ({f}/{total_frames})", flush=True)

    vw.release()
    print(f"\n✅ Vídeo salvo em: {out_path} (Tempo: {time.time()-t0:.1f}s)", flush=True)

if __name__ == "__main__": main()
