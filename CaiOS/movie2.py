"""
movie.py v2.0 — Whiteboard Animation Engine
SejaUmaPessoaMelhor

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PARA EDITAR CONTEÚDO (textos / imagens): edite content.py
PARA ALTERAR O MOTOR DE ANIMAÇÃO: edite este arquivo

Melhorias v2.0:
  ✓ Câmera virtual — canvas infinito com pan + zoom
  ✓ Reveal por máscara orgânica (alpha masking estilo sketch)
  ✓ Fontes handwritten (Patrick Hand) com fallback automático
  ✓ Textura de quadro branco + vinheta procedural
  ✓ Easing elástico e back com overshoot pronunciado
  ✓ Loader de assets PNG com cache e compositing RGBA
  ✓ Separação total de conteúdo e engine (content.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys, math, textwrap, time, random

# Importa configurações de conteúdo
sys.path.insert(0, os.path.dirname(__file__))
from content import SETTINGS, PALETTE, INTRO, LESSONS, FINAL

# ══════════════════════════════════════════════════════════
# CONSTANTES DERIVADAS DO CONTENT
# ══════════════════════════════════════════════════════════
W, H   = SETTINGS["resolution"]
FPS    = SETTINGS["fps"]
OUT    = os.path.dirname(SETTINGS["output_path"])
os.makedirs(OUT, exist_ok=True)
os.makedirs("assets", exist_ok=True)
os.makedirs("assets/fonts", exist_ok=True)

# Atalhos de cores
C = PALETTE   # ex: C["red"], C["ink"], C["bg"]

# ══════════════════════════════════════════════════════════
# EASING FUNCTIONS — Curvas de animação
# ══════════════════════════════════════════════════════════

def _clamp(t): return max(0.0, min(1.0, t))

def ease_linear(t):             return _clamp(t)

def ease_in_out_cubic(t):
    t = _clamp(t)
    return 4*t**3 if t < 0.5 else 1 - (-2*t+2)**3 / 2

def ease_in_out_quart(t):
    t = _clamp(t)
    return 8*t**4 if t < 0.5 else 1 - (-2*t+2)**4 / 2

def ease_in_out_expo(t):
    t = _clamp(t)
    if t == 0: return 0
    if t == 1: return 1
    return (2**(20*t-10))/2 if t < 0.5 else (2-2**(-20*t+10))/2

def ease_out_quad(t):           return 1 - (1-_clamp(t))**2
def ease_out_cubic(t):          return 1 - (1-_clamp(t))**3
def ease_out_quart(t):          return 1 - (1-_clamp(t))**4

def ease_out_back(t, s=2.2):
    """Overshoot elástico — s maior = mais 'mola'."""
    t = _clamp(t)
    return 1 + (s+1)*(t-1)**3 + s*(t-1)**2

def ease_out_bounce(t):
    t = _clamp(t)
    n1, d1 = 7.5625, 2.75
    if t < 1/d1:         return n1*t*t
    elif t < 2/d1:       t -= 1.5/d1;   return n1*t*t + 0.75
    elif t < 2.5/d1:     t -= 2.25/d1;  return n1*t*t + 0.9375
    else:                t -= 2.625/d1; return n1*t*t + 0.984375

def ease_out_elastic(t, amplitude=1.0, period=0.3):
    """Efeito de mola elástica na chegada."""
    t = _clamp(t)
    if t in (0, 1): return t
    s = period/(2*math.pi) * math.asin(1/amplitude) if amplitude >= 1 else period/4
    return amplitude * (2**(-10*t)) * math.sin((t-s)*(2*math.pi)/period) + 1

def lerp(a, b, t): return a + (b-a)*_clamp(t)

# ══════════════════════════════════════════════════════════
# FONT ENGINE — Patrick Hand com fallback automático
# ══════════════════════════════════════════════════════════

_font_cache = {}

def _system_font_paths(bold=False):
    """Caminhos de fallback no sistema operacional (Linux, Mac e Windows)."""
    candidates = []
    if bold:
        candidates += [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoescb.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    else:
        candidates += [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoesc.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    return [p for p in candidates if os.path.exists(p)]

def font(size, bold=False):
    """Carrega fonte handwritten com fallback em cascata."""
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]

    size = max(8, size)
    # Prioridade: Patrick Hand → AmaticSC → sistema
    priority = [
        SETTINGS.get("font_bold" if bold else "font_handwritten",
                     "assets/fonts/PatrickHand-Regular.ttf"),
        "assets/fonts/AmaticSC-Bold.ttf" if bold else "assets/fonts/AmaticSC-Regular.ttf",
        "assets/fonts/IndieFlower-Regular.ttf",
    ] + _system_font_paths(bold)

    for path in priority:
        if path and os.path.exists(path):
            try:
                fnt = ImageFont.truetype(path, size)
                _font_cache[key] = fnt
                return fnt
            except Exception:
                continue

    # último recurso: fonte embutida do Pillow
    fnt = ImageFont.load_default()
    _font_cache[key] = fnt
    return fnt

# ══════════════════════════════════════════════════════════
# WHITEBOARD CANVAS — Textura + Vinheta
# ══════════════════════════════════════════════════════════

_vignette_cache = None
_texture_cache  = None

def _make_vignette(w, h, intensity=0.38):
    """Gera máscara de vinheta (bordas mais escuras)."""
    mask = Image.new("L", (w, h), 255)
    dm = ImageDraw.Draw(mask)
    steps = 60
    for i in range(steps):
        t = i / steps
        alpha = int(255 * (1 - intensity * (1 - ease_out_quad(1-t))))
        dm.rectangle([i, i, w-i, h-i], outline=alpha, width=1)
    return mask

def _make_grain(w, h, intensity=14, seed=42):
    """Gera textura de grão procedural para o fundo do quadro branco."""
    rng = np.random.default_rng(seed)
    noise = rng.integers(-intensity, intensity+1, (h, w, 3), dtype=np.int16)
    base = np.full((h, w, 3), C["bg"], dtype=np.int16)
    result = np.clip(base + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(result, "RGB")

def _load_whiteboard_texture():
    """Carrega textura PNG se existir, caso contrário usa grão procedural."""
    global _texture_cache
    if _texture_cache is not None:
        return _texture_cache
    path = SETTINGS.get("whiteboard_texture", "")
    if path and os.path.exists(path):
        try:
            img = Image.open(path).convert("L").resize((W, H), Image.LANCZOS)
            _texture_cache = img
            return img
        except Exception:
            pass
    _texture_cache = _make_grain(W, H).convert("L")
    return _texture_cache

def blank_canvas():
    """
    Cria frame base com:
      - Cor de fundo do quadro branco (quase branco, levemente quente)
      - Textura de grão em baixa opacidade
      - Vinheta nas bordas
    """
    global _vignette_cache

    # Fundo base
    img = Image.new("RGB", (W, H), C["bg"])

    # Textura de grão
    texture = _load_whiteboard_texture()
    opacity = SETTINGS.get("texture_opacity", 0.06)
    if opacity > 0:
        grain_rgb = Image.merge("RGB", [texture]*3)
        img = Image.blend(img, grain_rgb, opacity)

    # Vinheta
    if _vignette_cache is None:
        _vignette_cache = _make_vignette(W, H, SETTINGS.get("vignette_intensity", 0.38))

    black = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.composite(img, black, _vignette_cache)

    return img

# ══════════════════════════════════════════════════════════
# ASSET LOADER — PNG com fundo transparente + cache
# ══════════════════════════════════════════════════════════

_asset_cache = {}

def load_asset(path, scale=1.0):
    """
    Carrega um PNG com canal alpha.
    Retorna None se o arquivo não existir (o engine usa fallback procedural).
    """
    if not path or not os.path.exists(path):
        return None
    key = (path, round(scale, 3))
    if key in _asset_cache:
        return _asset_cache[key].copy()
    try:
        img = Image.open(path).convert("RGBA")
        if scale != 1.0:
            nw = max(1, int(img.width  * scale))
            nh = max(1, int(img.height * scale))
            img = img.resize((nw, nh), Image.LANCZOS)
        _asset_cache[key] = img
        return img.copy()
    except Exception:
        return None

def paste_asset(base, path, xy, scale=1.0, alpha=1.0):
    """Compõe um asset PNG sobre o frame base (com alpha opcional)."""
    img = load_asset(path, scale)
    if img is None:
        return base
    if alpha < 1.0:
        r, g, b, a = img.split()
        a = a.point(lambda p: int(p * alpha))
        img.putalpha(a)
    base = base.convert("RGBA")
    base.paste(img, xy, img)
    return base.convert("RGB")

# ══════════════════════════════════════════════════════════
# REVEAL ENGINE — Efeitos de revelação de assets
# ══════════════════════════════════════════════════════════

def reveal_organic(base, asset_img, center_xy, progress):
    """
    Revela o asset com máscara orgânica irregular — simula o traço
    de um pincel ou marcador expandindo sobre o desenho.

    Substitui o corte retangular (wipe) por algo que lembra
    pintura real sendo preenchida.
    """
    p = ease_out_quad(progress)
    if p <= 0 or asset_img is None:
        return base

    w, h = asset_img.size
    cx, cy = w//2, h//2
    max_r = math.hypot(w, h) * 0.6

    # Máscara orgânica: vários elipses sobrepostos com jitter
    mask = Image.new("L", (w, h), 0)
    dm   = ImageDraw.Draw(mask)
    num_blobs = 24
    for i in range(num_blobs):
        angle  = (i / num_blobs) * 2 * math.pi
        jitter = 0.7 + 0.6 * math.sin(angle * 3.7 + 1.4) * math.cos(angle * 5.1)
        r      = int(max_r * p * jitter)
        ox     = int(cx * 0.15 * math.cos(angle * 2.3))
        oy     = int(cy * 0.15 * math.sin(angle * 1.7))
        if r <= 0:
            continue
        dm.ellipse([cx+ox-r, cy+oy-r, cx+ox+r, cy+oy+r], fill=255)

    blur_r = max(1, int(max_r * p * 0.12))
    mask = mask.filter(ImageFilter.GaussianBlur(blur_r))

    # Aplica a máscara ao canal alpha do asset
    r, g, b, a = asset_img.split()
    new_a = Image.composite(a, Image.new("L", (w, h), 0), mask)
    revealed = Image.merge("RGBA", (r, g, b, new_a))

    result = base.convert("RGBA")
    px = center_xy[0] - w//2
    py = center_xy[1] - h//2
    result.paste(revealed, (px, py), revealed)
    return result.convert("RGB")

def reveal_wipe_lr(base, asset_img, pos, progress):
    """Revelação wipe da esquerda para direita."""
    p = ease_in_out_cubic(progress)
    if p <= 0 or asset_img is None:
        return base
    ow, oh = asset_img.size
    rw = max(1, int(ow * p))
    crop = asset_img.crop((0, 0, rw, oh))
    result = base.convert("RGBA")
    result.paste(crop, pos, crop)
    return result.convert("RGB")

def reveal_pop(base, asset_img, center_xy, progress, s=2.2):
    """Pop-in com overshoot elástico (efeito 'mola')."""
    p = ease_out_back(progress, s=s)
    p = max(0.001, p)
    if asset_img is None:
        return base
    ow, oh = asset_img.size
    nw = max(1, int(ow * p))
    nh = max(1, int(oh * p))
    scaled = asset_img.resize((nw, nh), Image.LANCZOS)
    px = center_xy[0] - nw//2
    py = center_xy[1] - nh//2
    result = base.convert("RGBA")
    result.paste(scaled, (px, py), scaled)
    return result.convert("RGB")

def reveal_fade(base, asset_img, pos, progress):
    """Fade-in suave."""
    p = ease_out_quad(progress)
    if asset_img is None:
        return base
    r, g, b, a = asset_img.split()
    new_a = a.point(lambda x: int(x * p))
    img2  = Image.merge("RGBA", (r, g, b, new_a))
    result = base.convert("RGBA")
    result.paste(img2, pos, img2)
    return result.convert("RGB")

def reveal_slide_bottom(base, asset_img, target_pos, progress):
    """Slide vindo de baixo com bounce."""
    p = ease_out_back(progress, s=1.2)
    if asset_img is None:
        return base
    tx, ty = target_pos
    cur_y  = int(lerp(H + 50, ty, p))
    result = base.convert("RGBA")
    result.paste(asset_img, (tx, cur_y), asset_img)
    return result.convert("RGB")

def reveal_slide_left(base, asset_img, target_pos, progress):
    """Slide vindo da esquerda."""
    p = ease_out_cubic(progress)
    if asset_img is None:
        return base
    tx, ty = target_pos
    cur_x  = int(lerp(-asset_img.width - 20, tx, p))
    result = base.convert("RGBA")
    result.paste(asset_img, (cur_x, ty), asset_img)
    return result.convert("RGB")

# ══════════════════════════════════════════════════════════
# TEXT ENGINE — Typewriter + Jitter de escrita manual
# ══════════════════════════════════════════════════════════

def _line_jitter(line_idx, char_idx=0, amount=2):
    """Retorna um deslocamento Y consistente por linha (não flicka entre frames)."""
    val = math.sin(line_idx * 7.31 + char_idx * 0.17 + 1.2) * amount
    return int(val)

def draw_typewriter(draw, text, pos, size=28, color=None, bold=False,
                    progress=1.0, align="left", max_width=None, jitter=2):
    """
    Texto com efeito máquina de escrever + leve jitter de baseline
    para simular a irregularidade de uma escrita humana.
    """
    if color is None:
        color = C["ink"]
    fnt = font(size, bold)
    p   = ease_in_out_cubic(progress)

    # Quebra de linha manual ou por max_width
    if max_width:
        chars_per_line = max(10, max_width // max(1, size // 2))
        lines = textwrap.wrap(text, width=chars_per_line)
    else:
        lines = text.split("\n")

    full_text = "\n".join(lines)
    n_visible = max(0, int(len(full_text) * p))
    visible   = full_text[:n_visible]

    x, y  = pos
    lh    = size + 10
    for li, line in enumerate(visible.split("\n")):
        jy = _line_jitter(li, amount=jitter)
        if align == "center":
            try:
                bb = draw.textbbox((0, 0), line, font=fnt)
                lw = bb[2] - bb[0]
                draw.text((x - lw//2, y + jy), line, font=fnt, fill=color)
            except Exception:
                draw.text((x, y + jy), line, font=fnt, fill=color)
        elif align == "right":
            try:
                bb = draw.textbbox((0, 0), line, font=fnt)
                lw = bb[2] - bb[0]
                draw.text((x - lw, y + jy), line, font=fnt, fill=color)
            except Exception:
                draw.text((x, y + jy), line, font=fnt, fill=color)
        else:
            draw.text((x, y + jy), line, font=fnt, fill=color)
        y += lh

def draw_title(img, text, color="red", progress=1.0):
    """
    Título principal da lição:
      - Fonte grande, cor de destaque
      - Wipe da esquerda para a direita
      - Sublinhado animado
    """
    d    = ImageDraw.Draw(img)
    fnt  = font(38, bold=True)
    clr  = C.get(color, C["red"])
    p    = ease_out_quad(progress)
    n    = max(0, int(len(text) * p))
    vis  = text[:n]

    try:
        bb = d.textbbox((0, 0), text, font=fnt)
        tw = bb[2] - bb[0]
    except Exception:
        tw = len(text) * 20

    tx = (W - tw) // 2
    ty = 22
    d.text((tx, ty), vis, font=fnt, fill=clr)

    if p > 0.85:
        uw = int(tw * (p - 0.85) / 0.15)
        d.rectangle([tx, ty + 48, tx + uw, ty + 53], fill=clr)
    return img

# ══════════════════════════════════════════════════════════
# CAMERA TRANSITION — Pan suave entre lições
# ══════════════════════════════════════════════════════════

def camera_transition(vw, get_frame_b, direction="right",
                      prev_frame=None, duration=None):
    """
    Cria uma transição de câmera deslizando horizontalmente ou
    verticalmente — simula a câmera percorrendo o canvas infinito.

    Args:
        vw            : VideoWriter
        get_frame_b   : callable() → PIL.Image do primeiro frame da próxima lição
        direction     : "right" | "left" | "down" | "up"
        prev_frame    : PIL.Image do último frame da lição anterior
        duration      : segundos (None = usa SETTINGS)
    """
    dur = duration or SETTINGS.get("transition_duration", 1.4)
    n   = max(4, int(dur * FPS))

    if prev_frame is None:
        prev_frame = blank_canvas()
    frame_b = get_frame_b()

    # Monta staging canvas: lição A + lição B lado a lado / acima abaixo
    if direction in ("right", "left"):
        staging = Image.new("RGB", (3 * W, H), C["bg"])
        if direction == "right":
            staging.paste(prev_frame, (0,     0))
            staging.paste(frame_b,    (W,     0))
            start_x, end_x = 0, W
        else:
            staging.paste(frame_b,    (0,     0))
            staging.paste(prev_frame, (W,     0))
            start_x, end_x = W, 0

        for i in range(n):
            t    = ease_in_out_cubic(i / (n - 1))
            zoom = 1.0 - 0.04 * math.sin(t * math.pi)   # leve zoom-out no meio
            x_off = int(lerp(start_x, end_x, t))

            crop = staging.crop((x_off, 0, x_off + W, H))
            if zoom < 1.0:
                nw = max(1, int(W * zoom))
                nh = max(1, int(H * zoom))
                crop = crop.resize((nw, nh), Image.LANCZOS)
                pad  = Image.new("RGB", (W, H), C["bg"])
                pad.paste(crop, ((W - nw)//2, (H - nh)//2))
                crop = pad
            vw.write_pil(crop)

    elif direction in ("down", "up"):
        staging = Image.new("RGB", (W, 3 * H), C["bg"])
        if direction == "down":
            staging.paste(prev_frame, (0, 0))
            staging.paste(frame_b,    (0, H))
            start_y, end_y = 0, H
        else:
            staging.paste(frame_b,    (0, 0))
            staging.paste(prev_frame, (0, H))
            start_y, end_y = H, 0

        for i in range(n):
            t     = ease_in_out_cubic(i / (n - 1))
            zoom  = 1.0 - 0.04 * math.sin(t * math.pi)
            y_off = int(lerp(start_y, end_y, t))

            crop = staging.crop((0, y_off, W, y_off + H))
            if zoom < 1.0:
                nw = max(1, int(W * zoom))
                nh = max(1, int(H * zoom))
                crop = crop.resize((nw, nh), Image.LANCZOS)
                pad  = Image.new("RGB", (W, H), C["bg"])
                pad.paste(crop, ((W - nw)//2, (H - nh)//2))
                crop = pad
            vw.write_pil(crop)

# ══════════════════════════════════════════════════════════
# DRAWING PRIMITIVES — Elementos procedurais (usados como
# fallback quando o asset PNG não existe)
# ══════════════════════════════════════════════════════════

def draw_hand_rect(draw, xy, wh, progress=1.0, color=None, width=3):
    """Retângulo desenhado progressivamente, simulando traço manual."""
    if color is None: color = C["ink"]
    x, y = xy; rw, rh = wh
    p = ease_in_out_cubic(progress)
    perim = 2 * (rw + rh)
    dist  = perim * p
    pts   = [(x,y), (x+rw,y), (x+rw,y+rh), (x,y+rh), (x,y)]
    segs  = [rw, rh, rw, rh]
    drawn = 0
    for i in range(4):
        s = segs[i]
        if drawn + s <= dist:
            draw.line([pts[i], pts[i+1]], fill=color, width=width)
            drawn += s
        else:
            rem = dist - drawn
            t_  = rem / s if s > 0 else 0
            mx  = int(lerp(pts[i][0], pts[i+1][0], t_))
            my  = int(lerp(pts[i][1], pts[i+1][1], t_))
            draw.line([pts[i], (mx, my)], fill=color, width=width)
            break

def draw_arrow(draw, x1, y1, x2, y2, color=None, width=4, progress=1.0):
    if color is None: color = C["blue"]
    p  = ease_in_out_cubic(progress)
    ex = int(x1 + (x2-x1)*p); ey = int(y1 + (y2-y1)*p)
    draw.line([(x1,y1),(ex,ey)], fill=color, width=width)
    if p > 0.9:
        ang = math.atan2(y2-y1, x2-x1)
        hs  = 16
        for sign in [-1, 1]:
            ax = ex - int(hs*math.cos(ang - sign*0.5))
            ay = ey - int(hs*math.sin(ang - sign*0.5))
            draw.line([(ex,ey),(ax,ay)], fill=color, width=width)

def draw_imperfect_circle(draw, cx, cy, r, color, width=5, progress=1.0):
    """Círculo com traço orgânico — imita rabisco com marcador."""
    p    = ease_in_out_cubic(progress)
    n    = 72
    pts  = []
    for i in range(n):
        ang    = (i/n) * 2*math.pi
        jitter = 1 + 0.045*math.sin(ang*7+1.2) + 0.03*math.cos(ang*11)
        pts.append((cx + int(r*jitter*math.cos(ang)), cy + int(r*jitter*math.sin(ang))))
    n_draw = max(2, int(len(pts)*p))
    for i in range(n_draw-1):
        draw.line([pts[i], pts[(i+1)%n_draw]], fill=color, width=width)

def draw_stick_figure(draw, cx, cy, scale=1.0, shirt=None, hair=None,
                      pose="neutral", progress=1.0):
    if shirt is None: shirt = C["red"]
    if hair  is None: hair  = C["yellow"]
    s = scale
    p = ease_out_quad(progress)
    if p <= 0: return
    r = int(22*s)

    draw.ellipse([cx-r,cy-r,cx+r,cy+r], outline=C["ink"], fill=C["white"],
                 width=max(1,int(3*s)))
    if p > 0.15:
        for angle in range(-70, 71, 25):
            rad = math.radians(angle-90)
            hx  = cx + int((r+9*s)*math.cos(rad))
            hy  = cy + int((r+9*s)*math.sin(rad))
            draw.line([cx+int(r*math.cos(rad)), cy+int(r*math.sin(rad)), hx, hy],
                      fill=hair, width=max(1,int(3*s)))
    if p > 0.25:
        eo = int(8*s); er = int(3*s)
        draw.ellipse([cx-eo-er, cy-er, cx-eo+er, cy+er], fill=C["ink"])
        draw.ellipse([cx+eo-er, cy-er, cx+eo+er, cy+er], fill=C["ink"])
    if p > 0.35:
        draw.arc([cx-int(10*s), cy+int(4*s), cx+int(10*s), cy+int(16*s)],
                 0, 180, fill=C["ink"], width=max(1,int(2*s)))

    body_top = cy+r; body_bot = cy+int(90*s); sw = int(28*s)
    if p > 0.45:
        draw.rectangle([cx-sw,body_top,cx+sw,body_bot], fill=shirt,
                       outline=C["ink"], width=max(1,int(2*s)))
    if p > 0.6:
        if pose == "pointing":
            draw.line([cx+sw,cy+int(40*s), cx+int(75*s),cy+int(22*s)],
                      fill=C["ink"], width=max(1,int(3*s)))
            draw.polygon([(cx+int(75*s),cy+int(22*s)),
                          (cx+int(62*s),cy+int(17*s)),
                          (cx+int(65*s),cy+int(32*s))], fill=C["ink"])
            draw.line([cx-sw,cy+int(40*s), cx-int(50*s),cy+int(68*s)],
                      fill=C["ink"], width=max(1,int(3*s)))
        elif pose == "arms_up":
            draw.line([cx-sw,cy+int(35*s), cx-int(55*s),cy-int(15*s)],
                      fill=C["ink"], width=max(1,int(3*s)))
            draw.line([cx+sw,cy+int(35*s), cx+int(55*s),cy-int(15*s)],
                      fill=C["ink"], width=max(1,int(3*s)))
        elif pose == "shrug":
            draw.line([cx-sw,cy+int(32*s), cx-int(50*s),cy+int(18*s)],
                      fill=C["ink"], width=max(1,int(3*s)))
            draw.line([cx+sw,cy+int(32*s), cx+int(50*s),cy+int(18*s)],
                      fill=C["ink"], width=max(1,int(3*s)))
        else:
            draw.line([cx-sw,cy+int(40*s), cx-int(50*s),cy+int(68*s)],
                      fill=C["ink"], width=max(1,int(3*s)))
            draw.line([cx+sw,cy+int(40*s), cx+int(50*s),cy+int(68*s)],
                      fill=C["ink"], width=max(1,int(3*s)))
    if p > 0.8:
        draw.line([cx-int(12*s),body_bot, cx-int(18*s),cy+int(155*s)],
                  fill=C["ink"], width=max(1,int(3*s)))
        draw.line([cx+int(12*s),body_bot, cx+int(18*s),cy+int(155*s)],
                  fill=C["ink"], width=max(1,int(3*s)))

def draw_battery(draw, x, y, w, h, level=1.0, color=None, t_anim=0.0):
    if color is None: color = C["green"]
    bw = 3
    draw.rectangle([x,y,x+w,y+h], outline=C["ink"], width=bw, fill=C["white"])
    draw.rectangle([x+w//3, y-8, x+2*w//3, y], fill=C["ink"])
    inner_h = max(0, int((h-bw*2)*level))
    pulse = 0.85+0.15*math.sin(t_anim*4) if t_anim else 1.0
    fc    = tuple(min(255,int(c*pulse)) for c in color)
    if inner_h > 0:
        draw.rectangle([x+bw, y+h-bw-inner_h, x+w-bw, y+h-bw], fill=fc)
    if level > 0.3:
        mx = x+w//2; my = y+h//2
        draw.polygon([(mx-4,my-8),(mx+2,my-2),(mx-2,my+2),(mx+4,my+8),
                      (mx-1,my+1),(mx+3,my-4)], fill=C["white"])

def draw_brain(draw, cx, cy, r=45, progress=1.0):
    p = ease_out_quad(progress)
    draw.pieslice([cx-r,cy-int(r*0.8),cx+r,cy+int(r*0.8)], 90, 270,
                  fill=C["blue"], outline=C["ink"], width=max(1,int(3*p)))
    draw.pieslice([cx-r,cy-int(r*0.8),cx+r,cy+int(r*0.8)], 270, 90,
                  fill=C["red"],  outline=C["ink"], width=max(1,int(3*p)))
    draw.line([cx,cy-int(r*0.8),cx,cy+int(r*0.8)], fill=C["ink"], width=2)
    if p > 0.5:
        draw.arc([cx-r//2,cy-r//2,cx,cy], 0,180, fill=C["ink"], width=2)
        draw.arc([cx,cy-r//2,cx+r//2,cy], 0,180, fill=C["ink"], width=2)

def draw_smiley(draw, cx, cy, r=40, color=None, sad=False, progress=1.0):
    if color is None: color = C["yellow"]
    p  = ease_out_bounce(progress)
    cr = max(1, int(r*p))
    draw.ellipse([cx-cr,cy-cr,cx+cr,cy+cr], fill=color, outline=C["ink"],
                 width=max(1,int(r/12)))
    if p < 0.5: return
    eo = int(r*0.32); er = max(1,int(r*0.1))
    draw.ellipse([cx-eo-er,cy-int(r*0.18)-er,cx-eo+er,cy-int(r*0.18)+er], fill=C["ink"])
    draw.ellipse([cx+eo-er,cy-int(r*0.18)-er,cx+eo+er,cy-int(r*0.18)+er], fill=C["ink"])
    arc_y = cy+int(r*0.08) if not sad else cy+int(r*0.3)
    if sad:
        draw.arc([cx-int(r*.5),arc_y,cx+int(r*.5),arc_y+int(r*.4)],
                 180,360, fill=C["ink"], width=max(1,int(r*0.1)))
    else:
        draw.arc([cx-int(r*.5),arc_y,cx+int(r*.5),arc_y+int(r*.47)],
                 0,180, fill=C["ink"], width=max(1,int(r*0.1)))

def draw_thought_bubble(draw, text, cx, cy, w=320, h=90, progress=1.0):
    p = ease_out_back(progress)
    if p <= 0: return
    nw = max(10,int(w*p)); nh = max(10,int(h*p))
    nx = cx-nw//2; ny = cy-nh//2
    draw.rounded_rectangle([nx,ny,nx+nw,ny+nh], radius=int(20*p),
                            fill=C["white"], outline=C["ink"], width=max(1,int(3*p)))
    if p > 0.65:
        fnt = font(max(10, int(20*p)), bold=True)
        draw.text((cx, cy), text, font=fnt, fill=C["ink"], anchor="mm")
    for i, r_ in enumerate([6,4,2]):
        dy = nh//2 + 10 + i*12
        if ny + dy < H:
            draw.ellipse([cx-r_,ny+dy-r_,cx+r_,ny+dy+r_], fill=C["ink"])

def draw_speech_rect(draw, text, rx, ry, w=280, h=70, progress=1.0):
    p = ease_out_back(progress, s=1.8)
    if p <= 0: return
    nw = max(10,int(w*p)); nh = max(10,int(h*p))
    draw.rounded_rectangle([rx,ry,rx+nw,ry+nh], radius=10,
                            fill=C["white"], outline=C["ink"], width=max(1,int(2*p)))
    if p > 0.7:
        fnt = font(max(10,int(20*p)), bold=True)
        draw.text((rx+nw//2,ry+nh//2), text, font=fnt, fill=C["ink"], anchor="mm")
    if p > 0.8:
        draw.polygon([(rx+nw//4,ry+nh),(rx+nw//4+20,ry+nh),
                      (rx+nw//4-10,ry+nh+20)], fill=C["ink"])

def draw_gravestone(draw, cx, cy, progress=1.0):
    p = ease_out_quad(progress)
    w, h = 90, 110; ph = max(1,int(h*p))
    x, y = cx-w//2, cy-h//2
    draw.rectangle([x,cy-h//2+h-ph,x+w,cy+h//2],
                   fill=C["gray"], outline=C["ink"], width=3)
    if p > 0.7:
        draw.ellipse([x,y,x+w,y+w//1.5], fill=C["gray"], outline=C["ink"], width=3)
    if p > 0.85:
        draw.text((cx,cy+5), "R.I.P", font=font(20,bold=True), fill=C["ink"], anchor="mm")

def draw_book_stack(draw, x, y, n=5, progress=1.0):
    colors_ = [C["red"],C["blue"],C["green"],C["yellow"],C["purple"]]
    bh, bw  = 24, 130
    p       = ease_out_quad(progress)
    for i in range(n):
        a_i = min(1.0, p*n - i)
        if a_i <= 0: continue
        col = colors_[i % len(colors_)]
        by_ = y - i*bh
        draw.rectangle([x,by_,x+bw,by_+bh], fill=col, outline=C["ink"], width=2)
        draw.line([x+10,by_,x+10,by_+bh],     fill=C["ink"], width=2)
        draw.line([x+18,by_+7,x+bw-8,by_+7],  fill=C["white"], width=2)

def draw_alarm_clock(draw, cx, cy, r=55, progress=1.0):
    p  = ease_out_back(progress)
    if p <= 0: return
    cr = max(1,int(r*p))
    draw.ellipse([cx-cr,cy-cr,cx+cr,cy+cr],
                 fill=C["red"], outline=C["ink"], width=max(1,int(4*p)))
    draw.ellipse([cx-int(cr*.85),cy-int(cr*.85),cx+int(cr*.85),cy+int(cr*.85)],
                 fill=C["white"], outline=C["ink"], width=max(1,int(2*p)))
    if p > 0.5:
        draw.line([cx,cy,cx,cy-int(cr*.6)], fill=C["ink"], width=max(1,int(4*p)))
        draw.line([cx,cy,cx+int(cr*.4),cy-int(cr*.2)],
                  fill=C["ink"], width=max(1,int(4*p)))
    if p > 0.7:
        for sign in [-1,1]:
            bx_ = cx + sign*int(cr*.65)
            draw.ellipse([bx_-int(cr*.2),cy-cr-int(cr*.3),
                          bx_+int(cr*.2),cy-cr+int(cr*.15)],
                         fill=C["red"], outline=C["ink"], width=max(1,int(2*p)))

def draw_fridge(draw, x, y, w, h, progress=1.0):
    p  = ease_out_quad(progress)
    ph = max(1,int(h*p))
    draw.rounded_rectangle([x,y+h-ph,x+w,y+h], radius=8,
                            fill=(215,215,215), outline=C["ink"], width=max(1,int(3*p)))
    div_y = y + int(h*.42)
    if div_y > y+h-ph:
        draw.line([x,div_y,x+w,div_y], fill=C["ink"], width=2)
    hx_ = x+w-20
    if p > 0.5:
        draw.rounded_rectangle([hx_,y+h-ph+25,hx_+12,y+h-ph+55],
                                radius=4, fill=C["gray_dark"])
    if p > 0.85:
        for fx,fy,fc,fr in [(x+25,div_y-30,(255,60,60),13),
                             (x+60,div_y-32,(255,200,0),11),
                             (x+93,div_y-30,(50,200,50),13)]:
            if fy > y+h-ph:
                draw.ellipse([fx-fr,fy-fr,fx+fr,fy+fr], fill=fc, outline=C["ink"], width=2)

# ══════════════════════════════════════════════════════════
# VIDEO WRITER
# ══════════════════════════════════════════════════════════

def pil2cv(img):
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)

class VideoWriter:
    def __init__(self, path):
        def get_fcc():
            # Tenta avc1 (H.264), X264 ou mp4v como fallback
            for c in ['avc1', 'X264', 'mp4v']:
                fcc = cv2.VideoWriter_fourcc(*c)
                if fcc != -1: return fcc
            return cv2.VideoWriter_fourcc(*'mp4v')
            
        self.vw   = cv2.VideoWriter(path, get_fcc(), FPS, (W, H))
        if not self.vw.isOpened():
            raise RuntimeError(f"VideoWriter falhou ao abrir: {path}")
        self.frame_count = 0
        self._last_frame = None

    def write_pil(self, img):
        self.vw.write(pil2cv(img))
        self.frame_count += 1
        self._last_frame  = img

    def write_n(self, img, seconds):
        n     = max(1, int(seconds * FPS))
        frame = pil2cv(img)
        for _ in range(n):
            self.vw.write(frame)
            self.frame_count += 1
        self._last_frame = img

    def animate(self, frame_fn, duration, hold=0.2):
        """
        Anima chamando frame_fn(t) para t em [0..1] ao longo de `duration` segundos.
        Mantém o último frame por `hold` segundos.
        """
        n    = max(2, int(duration * FPS))
        last = None
        for i in range(n):
            t   = i / (n - 1)
            img = frame_fn(t)
            self.write_pil(img)
            last = img
        if hold > 0 and last is not None:
            self.write_n(last, hold)
            self._last_frame = last

    def last_frame(self):
        return self._last_frame

    def release(self):
        self.vw.release()

# ══════════════════════════════════════════════════════════
# QUADROS — Cada função renderiza uma lição
# Todas leem os textos e assets de LESSONS em content.py
# ══════════════════════════════════════════════════════════

def _lesson(idx):
    """Atalho para pegar conteúdo de uma lição pelo índice."""
    return LESSONS[idx]

def _asset(lesson_data, key, scale=1.0):
    """Carrega um asset de uma lição; retorna None se não existir."""
    path = lesson_data.get("assets", {}).get(key, "")
    return load_asset(path, scale)


# ── INTRO ─────────────────────────────────────────────────

def quadro_1_intro(vw):
    """Personagem sendo desenhado + seta apontando para o painel."""
    def frame(t):
        img = blank_canvas()
        d   = ImageDraw.Draw(img)
        # Tenta usar asset PNG; fallback procedural
        asset = load_asset(INTRO.get("asset_personagem", ""))
        if asset:
            img = reveal_organic(img, asset, (185, 295), t)
        else:
            draw_stick_figure(d, 185, 295, scale=1.15,
                              shirt=C["red"], hair=C["yellow"],
                              pose="pointing", progress=t)
        return img
    vw.animate(frame, 1.8, hold=0.1)

    base = frame(1.0)

    def frame2(t):
        img = base.copy()
        d   = ImageDraw.Draw(img)
        draw_arrow(d, 268, 270, 415, 265, color=C["ink"], width=3, progress=t)
        return img
    vw.animate(frame2, 0.5, hold=0.3)


def quadro_2_panel(vw):
    """Painel principal com borda azul animada + 6 retângulos."""
    base = blank_canvas()
    d    = ImageDraw.Draw(base)
    asset = load_asset(INTRO.get("asset_personagem", ""))
    if asset:
        base = reveal_organic(base, asset, (185, 295), 1.0)
    else:
        draw_stick_figure(d, 185, 295, scale=1.15, shirt=C["red"],
                          hair=C["yellow"], pose="pointing", progress=1.0)
    draw_arrow(ImageDraw.Draw(base), 268, 270, 415, 265,
               color=C["ink"], width=3, progress=1.0)

    PX, PY, PW, PH = 425, 48, 828, 638

    def frame_border(t):
        img = base.copy()
        draw_hand_rect(ImageDraw.Draw(img), (PX,PY), (PW,PH),
                       progress=t, color=C["blue"], width=4)
        return img
    vw.animate(frame_border, 1.2, hold=0.1)

    base2 = frame_border(1.0)

    def frame_title(t):
        img = base2.copy()
        d2  = ImageDraw.Draw(img)
        draw_typewriter(d2, INTRO["titulo_painel"],
                        (PX + PW//2, PY+20), size=26, color=C["blue"],
                        bold=True, progress=t, align="center")
        return img
    vw.animate(frame_title, 1.5, hold=0.1)

    cols, rows = 2, 3
    sw = (PW-60)//cols; sh = (PH-100)//rows
    rects = []
    for r in range(rows):
        for c in range(cols):
            rects.append((PX+20+c*(sw+10), PY+65+r*(sh+10), sw-10, sh-10))

    base_t = frame_title(1.0)
    for i, (rx, ry, rw, rh) in enumerate(rects):
        prev_base = base_t.copy()
        dp = ImageDraw.Draw(prev_base)
        for j in range(i):
            prx,pry,prw,prh = rects[j]
            draw_hand_rect(dp, (prx,pry), (prw,prh), progress=1.0,
                           color=C["ink"], width=2)

        def frame_rect(t, _px=rx,_py=ry,_pw=rw,_ph=rh,_pb=prev_base):
            img = _pb.copy()
            draw_hand_rect(ImageDraw.Draw(img), (_px,_py), (_pw,_ph),
                           progress=t, color=C["ink"], width=2)
            return img
        vw.animate(frame_rect, 0.5, hold=0.08)
        base_t = frame_rect(1.0)

    return rects, base_t


def quadro_3_numbers(vw, rects, base_img):
    """Números 1–6 com pop-in elástico."""
    labels = INTRO["labels"]
    base   = base_img.copy()

    for i in range(6):
        rx, ry, rw, rh = rects[i]
        prev   = base.copy()
        dp     = ImageDraw.Draw(prev)
        for j in range(i):
            prx, pry, _, _ = rects[j]
            lbl, lc = labels[j]
            dp.text((prx+14, pry+10), str(j+1), font=font(52,bold=True), fill=C["ink"])
            dp.text((prx+14, pry+68), lbl,       font=font(18,bold=True), fill=C.get(lc, C["ink"]))

        def frame_num(t, _i=i, _rx=rx, _ry=ry, _pb=prev):
            img = _pb.copy()
            d2  = ImageDraw.Draw(img)
            p_  = ease_out_back(t, s=2.4)
            sz  = max(8, int(52*p_))
            lbl, lc = labels[_i]
            d2.text((_rx+14,_ry+10), str(_i+1), font=font(sz,bold=True), fill=C["ink"])
            if p_ > 0.6:
                d2.text((_rx+14,_ry+68), lbl,
                        font=font(max(8,int(18*p_)),bold=True),
                        fill=C.get(lc, C["ink"]))
            return img
        vw.animate(frame_num, 0.38, hold=0.05)
        base = frame_num(1.0)

    vw.write_n(base, 0.6)
    return base


# ── LIÇÃO 1: SAÚDE ────────────────────────────────────────

def quadro_4_saude(vw):
    les = _lesson(0)   # "01_saude"

    # Título
    vw.animate(lambda t: draw_title(blank_canvas(), les["titulo"],
                                    les["titulo_color"], t), 1.0, hold=0.1)
    base_t = blank_canvas()
    draw_title(base_t, les["titulo"], les["titulo_color"], 1.0)

    # Personagem esquerdo
    def frame_esq(t):
        img   = base_t.copy()
        asset = _asset(les, "personagem_esq", scale=0.75)
        if asset:
            return reveal_organic(img, asset, (200, 410), t)
        d = ImageDraw.Draw(img)
        # Fallback: sofá + figura
        ds = d
        ds.rectangle([80,440,510,565], fill=C["brown"], outline=C["ink"], width=3)
        ds.rectangle([80,370,135,455], fill=(120,75,30), outline=C["ink"], width=2)
        ds.rectangle([460,370,510,455], fill=(120,75,30), outline=C["ink"], width=2)
        draw_stick_figure(d, 180, 385, scale=0.85,
                          shirt=C["red"], hair=C["yellow"], progress=t)
        return img
    vw.animate(frame_esq, 1.5, hold=0.2)
    base_esq = frame_esq(1.0)

    # Balão de pensamento
    def frame_bubble(t):
        img = base_esq.copy()
        d   = ImageDraw.Draw(img)
        asset = _asset(les, "balao", scale=0.7)
        if asset:
            img = reveal_pop(img, asset, (300, 270), t)
            d   = ImageDraw.Draw(img)
            if t > 0.6:
                draw_typewriter(d, les["balao_texto"], (220, 240),
                                size=18, bold=True, progress=(t-0.6)/0.4)
        else:
            draw_thought_bubble(d, les["balao_texto"], 310, 272,
                                w=305, h=98, progress=t)
        return img
    vw.animate(frame_bubble, 0.9, hold=0.25)
    base_bubble = frame_bubble(1.0)

    # Personagem direito
    def frame_dir(t):
        img   = base_bubble.copy()
        asset = _asset(les, "personagem_dir", scale=0.75)
        if asset:
            return reveal_organic(img, asset, (980, 410), t)
        d = ImageDraw.Draw(img)
        draw_stick_figure(d, 940, 365, scale=1.0,
                          shirt=C["blue"], hair=C["yellow"], progress=t)
        return img
    vw.animate(frame_dir, 1.0, hold=0.2)
    base_dir = frame_dir(1.0)

    # Texto principal
    def frame_txt(t):
        img = base_dir.copy()
        draw_typewriter(ImageDraw.Draw(img), les["texto_principal"],
                        (W//2, 590), size=22, bold=True, color=C["ink"],
                        progress=t, align="center")
        return img
    vw.animate(frame_txt, 2.2, hold=0.4)
    base_txt = frame_txt(1.0)

    # Lápide + ícones (decorativo central)
    def frame_grave(t):
        img   = base_txt.copy()
        asset = _asset(les, "decorativo", scale=0.7)
        if asset:
            return reveal_organic(img, asset, (820, 500), t)
        draw_gravestone(ImageDraw.Draw(img), 820, 515, progress=t)
        return img
    vw.animate(frame_grave, 0.7, hold=0.1)
    base_grave = frame_grave(1.0)

    # Ícones pequenos com pop-in elástico
    icon_base = base_grave
    for key, cx, cy in [("icone_sol",778,392), ("icone_bateria",824,392), ("icone_halter",872,392)]:
        def frame_icon(t, _k=key, _x=cx, _y=cy, _b=icon_base):
            img   = _b.copy()
            asset = _asset(les, _k, scale=0.4)
            if asset:
                return reveal_pop(img, asset, (_x, _y), t)
            d   = ImageDraw.Draw(img)
            p_  = ease_out_back(t)
            r_  = max(1, int(15*p_))
            if _k == "icone_sol":
                d.ellipse([_x-r_,_y-r_,_x+r_,_y+r_], fill=C["yellow"], outline=C["ink"], width=2)
                for ang in range(0,360,45):
                    rad = math.radians(ang)
                    d.line([_x+int((r_+2)*math.cos(rad)),_y+int((r_+2)*math.sin(rad)),
                            _x+int((r_+8)*math.cos(rad)),_y+int((r_+8)*math.sin(rad))],
                           fill=C["yellow"], width=2)
            elif _k == "icone_bateria":
                draw_battery(d,_x-12,_y-7,25,14, level=1.0, color=C["green"])
            else:
                d.line([_x-13,_y,_x+13,_y], fill=C["gray_dark"], width=max(1,int(4*p_)))
                for sx in [_x-13,_x+13]:
                    d.ellipse([sx-int(7*p_),_y-int(7*p_),sx+int(7*p_),_y+int(7*p_)],
                              fill=C["gray_dark"], outline=C["ink"], width=max(1,int(2*p_)))
            return img
        vw.animate(frame_icon, 0.38, hold=0.06)
        icon_base = frame_icon(1.0)

    vw.write_n(icon_base, 0.8)
    return icon_base


# ── LIÇÃO 2: AMBIENTE ─────────────────────────────────────

def quadro_5_ambiente(vw):
    les = _lesson(1)   # "02_ambiente"

    vw.animate(lambda t: draw_title(blank_canvas(), les["titulo"],
                                    les["titulo_color"], t), 1.0, hold=0.1)
    base_t = blank_canvas()
    draw_title(base_t, les["titulo"], les["titulo_color"], 1.0)

    # Personagem central
    def frame_char(t):
        img   = base_t.copy()
        asset = _asset(les, "personagem_centro", scale=0.9)
        if asset:
            return reveal_organic(img, asset, (W//2, 385), t)
        d = ImageDraw.Draw(img)
        draw_stick_figure(d, 640, 365, scale=1.15,
                          shirt=C["red"], hair=C["yellow"], progress=t)
        return img
    vw.animate(frame_char, 1.0, hold=0.2)
    base_char = frame_char(1.0)

    # Cérebro + bateria (energia interna)
    def frame_brain(t):
        img   = base_char.copy()
        asset = _asset(les, "cerebro_bateria", scale=0.75)
        if asset:
            return reveal_organic(img, asset, (185, 350), t)
        d = ImageDraw.Draw(img)
        draw_brain(d, 200, 280, r=62, progress=t)
        draw_battery(d, 155, 355, 92, 46, level=0.9, color=C["green"])
        return img
    vw.animate(frame_brain, 1.0, hold=0.1)
    base_brain = frame_brain(1.0)

    # Balão de fala
    def frame_speech(t):
        img   = base_brain.copy()
        asset = _asset(les, "balao", scale=0.6)
        if asset:
            img = reveal_pop(img, asset, (400, 225), t)
            if t > 0.6:
                draw_typewriter(ImageDraw.Draw(img), les["balao_texto"],
                                (360, 235), size=18, bold=True, progress=(t-0.6)/0.4)
        else:
            draw_speech_rect(ImageDraw.Draw(img), les["balao_texto"],
                             400, 222, w=258, h=68, progress=t)
        return img
    vw.animate(frame_speech, 0.7, hold=0.25)
    base_speech = frame_speech(1.0)

    # Refrigerante + X
    def frame_bottle(t):
        img   = base_speech.copy()
        d     = ImageDraw.Draw(img)
        asset = _asset(les, "refrigerante", scale=0.5)
        p_    = ease_out_back(t)
        if asset:
            img = reveal_pop(img, asset, (1100, 340), t)
        else:
            bh_ = max(1, int(170*p_))
            d.rectangle([1100,260+170-bh_,1152,432], fill=(30,30,30), outline=C["ink"], width=2)
        # X vermelho
        x_asset = _asset(les, "marca_x", scale=0.5)
        if x_asset and t > 0.5:
            img = reveal_pop(img, x_asset, (1100, 280), (t-0.5)/0.5)
        elif t > 0.65:
            xp_ = ease_out_quad((t-0.65)/0.35)
            xl  = int(70*xp_)
            d   = ImageDraw.Draw(img)
            d.line([(1090,248),(1090+xl,248+xl)], fill=C["red"], width=7)
            d.line([(1162,248),(1162-xl,248+xl)], fill=C["red"], width=7)
        return img
    vw.animate(frame_bottle, 0.9, hold=0.1)
    base_bottle = frame_bottle(1.0)

    # Doces + X
    def frame_candy(t):
        img   = base_bottle.copy()
        asset = _asset(les, "doces", scale=0.5)
        if asset:
            img = reveal_pop(img, asset, (1100, 480), t)
        else:
            d = ImageDraw.Draw(img)
            p_ = ease_out_back(t)
            cx_, cy_ = 1100, 482
            sz_ = max(1,int(30*p_))
            d.rectangle([cx_-sz_,cy_-sz_//2,cx_+sz_,cy_+sz_//2],
                         fill=(100,55,20), outline=C["ink"], width=2)
        x_asset = _asset(les, "marca_x", scale=0.5)
        if x_asset and t > 0.5:
            img = reveal_pop(img, x_asset, (1100, 470), (t-0.5)/0.5)
        elif t > 0.65:
            d   = ImageDraw.Draw(img)
            xp_ = ease_out_quad((t-0.65)/0.35)
            xl_ = int(60*xp_)
            d.line([(1058,440),(1058+xl_,440+xl_)], fill=C["red"], width=7)
            d.line([(1148,440),(1148-xl_,440+xl_)], fill=C["red"], width=7)
        return img
    vw.animate(frame_candy, 0.7, hold=0.1)
    base_candy = frame_candy(1.0)

    # Geladeira
    def frame_fridge(t):
        img   = base_candy.copy()
        asset = _asset(les, "geladeira", scale=0.7)
        if asset:
            return reveal_organic(img, asset, (980, 400), t)
        draw_fridge(ImageDraw.Draw(img), 945, 250, 162, 295, progress=t)
        return img
    vw.animate(frame_fridge, 1.2, hold=0.15)
    base_fridge = frame_fridge(1.0)

    # Texto conclusivo
    def frame_txt(t):
        img = base_fridge.copy()
        draw_typewriter(ImageDraw.Draw(img), les["texto_principal"],
                        (W//2, 595), size=20, color=C["ink"],
                        progress=t, align="center")
        return img
    vw.animate(frame_txt, 2.5, hold=0.8)
    return frame_txt(1.0)


# ── LIÇÃO 3: AUTENTICIDADE ────────────────────────────────

def quadro_6_mentira(vw):
    les = _lesson(2)   # "03_autenticidade"

    vw.animate(lambda t: draw_title(blank_canvas(), les["titulo"],
                                    les["titulo_color"], t), 0.9, hold=0.1)
    base_t = blank_canvas()
    draw_title(base_t, les["titulo"], les["titulo_color"], 1.0)

    # Cena de reunião (lado esquerdo)
    def frame_meet(t):
        img   = base_t.copy()
        asset = _asset(les, "cena_reuniao", scale=0.8)
        if asset:
            return reveal_organic(img, asset, (310, 415), t)
        d = ImageDraw.Draw(img)
        d.rectangle([122,365,562,495], fill=C["brown"], outline=C["ink"], width=3)
        for px,py,sc in [(202,308,C["orange"]),(342,298,C["green"]),(482,308,C["blue"])]:
            draw_stick_figure(d, px, py, scale=0.7, shirt=sc,
                              hair=C["yellow"], progress=t)
        return img
    vw.animate(frame_meet, 1.5, hold=0.15)
    base_meet = frame_meet(1.0)

    # Texto apoio esquerda
    def frame_txt_esq(t):
        img = base_meet.copy()
        draw_typewriter(ImageDraw.Draw(img), les["texto_apoio_esq"],
                        (300, 238), size=22, color=C["gray_dark"],
                        progress=t, align="center")
        return img
    vw.animate(frame_txt_esq, 1.0, hold=0.15)
    base_t1 = frame_txt_esq(1.0)

    # Seta de transição
    def frame_arrow(t):
        img   = base_t1.copy()
        asset = _asset(les, "seta_transicao", scale=0.5)
        if asset:
            return reveal_pop(img, asset, (620, 368), t)
        draw_arrow(ImageDraw.Draw(img), 612, 395, 782, 395,
                   color=C["blue"], width=6, progress=t)
        return img
    vw.animate(frame_arrow, 0.5, hold=0.1)
    base_arr = frame_arrow(1.0)

    # Caixa de destaque azul + texto
    def frame_hl(t):
        img = base_arr.copy()
        d   = ImageDraw.Draw(img)
        p_  = ease_out_back(t)
        bw_ = max(1, int(402*p_))
        bh_ = max(1, int(100*p_))
        d.rounded_rectangle([800, 340, 800+bw_, 340+bh_], radius=10,
                             fill=C["blue_light"] + (180,) if len(C["blue_light"])==3
                             else C["blue_light"],
                             outline=C["blue"], width=3)
        if p_ > 0.65:
            draw_typewriter(d, les["texto_apoio_dir"], (1002, 348),
                            size=22, bold=True, progress=(p_-0.65)/0.35, align="center")
        return img
    vw.animate(frame_hl, 0.9, hold=0.35)
    base_hl = frame_hl(1.0)

    # Personagem isolado → social
    def frame_alone(t):
        img   = base_hl.copy()
        asset = _asset(les, "personagem_isolado", scale=0.65)
        if asset:
            return reveal_fade(img, asset, (888, 450), t)
        draw_stick_figure(ImageDraw.Draw(img), 922, 535, scale=0.75,
                          shirt=C["orange"], hair=C["yellow"],
                          pose="shrug", progress=t)
        return img
    vw.animate(frame_alone, 0.7, hold=0.5)
    base_alone = frame_alone(1.0)

    def frame_group(t):
        img   = base_alone.copy()
        asset = _asset(les, "personagem_social", scale=0.65)
        if asset:
            img_new = blank_canvas()
            # fade entre isolado e social
            img = Image.blend(img, reveal_fade(img, asset, (888, 450), t), t*0.9)
            return img
        d = ImageDraw.Draw(img)
        shirts = [C["orange"],C["blue"],C["green"],C["red"],C["yellow"]]
        offs   = [(-45,0),(0,0),(45,0),(-22,35),(22,35)]
        for i,(ox,oy) in enumerate(offs):
            draw_stick_figure(d, 952+ox, 525+oy, scale=0.62,
                              shirt=shirts[i], hair=C["yellow"], progress=t)
        return img
    vw.animate(frame_group, 0.9, hold=0.2)
    base_group = frame_group(1.0)

    # Texto final
    def frame_txt2(t):
        img = base_group.copy()
        draw_typewriter(ImageDraw.Draw(img), les["texto_principal"],
                        (820, 620), size=20, color=C["ink"], progress=t)
        return img
    vw.animate(frame_txt2, 1.5, hold=0.8)
    return frame_txt2(1.0)


# ── LIÇÃO 4: LEITURA ──────────────────────────────────────

def quadro_7_leitura(vw):
    les = _lesson(3)   # "04_leitura"

    vw.animate(lambda t: draw_title(blank_canvas(), les["titulo"],
                                    les["titulo_color"], t), 0.8, hold=0.1)
    base_t = blank_canvas()
    draw_title(base_t, les["titulo"], les["titulo_color"], 1.0)

    # Cabeça/cérebro central
    def frame_head(t):
        img   = base_t.copy()
        asset = _asset(les, "cabeca_cerebro", scale=0.9)
        if asset:
            return reveal_organic(img, asset, (W//2, 395), t)
        draw_brain(ImageDraw.Draw(img), W//2, 350, r=75, progress=t)
        return img
    vw.animate(frame_head, 1.2, hold=0.15)
    base_head = frame_head(1.0)

    # Pilha de livros (pop-in sobre o cérebro)
    def frame_books(t):
        img   = base_head.copy()
        asset = _asset(les, "pilha_livros", scale=0.85)
        if asset:
            return reveal_pop(img, asset, (W//2, 330), t, s=1.8)
        draw_book_stack(ImageDraw.Draw(img), W//2-65, 510, n=6, progress=t)
        return img
    vw.animate(frame_books, 0.9, hold=0.1)
    base_books = frame_books(1.0)

    # Homem escalando os livros
    def frame_climber(t):
        img   = base_books.copy()
        asset = _asset(les, "homem_escalando", scale=0.55)
        if asset:
            return reveal_slide_bottom(img, asset, (W//2+80, 330), t)
        d = ImageDraw.Draw(img)
        p_ = ease_out_back(t, s=1.3)
        draw_stick_figure(d, W//2+100, int(lerp(H,325,ease_out_cubic(t))),
                          scale=0.55, shirt=C["blue"], hair=C["yellow"], progress=t)
        return img
    vw.animate(frame_climber, 1.0, hold=0.1)
    base_climber = frame_climber(1.0)

    # Texto esquerda
    def frame_txt_esq(t):
        img = base_climber.copy()
        draw_typewriter(ImageDraw.Draw(img), les["texto_esq"],
                        (240, 270), size=24, color=C["ink"],
                        progress=t, align="right")
        return img
    vw.animate(frame_txt_esq, 2.0, hold=0.15)
    base_tesq = frame_txt_esq(1.0)

    # Texto direita
    def frame_txt_dir(t):
        img = base_tesq.copy()
        draw_typewriter(ImageDraw.Draw(img), les["texto_dir"],
                        (W-240, 270), size=24, color=C["ink"],
                        progress=t, align="left")
        return img
    vw.animate(frame_txt_dir, 2.0, hold=0.15)
    base_tdir = frame_txt_dir(1.0)

    # Multidão na base
    def frame_crowd(t):
        img   = base_tdir.copy()
        asset = _asset(les, "multidao", scale=1.1)
        if asset:
            return reveal_wipe_lr(img, asset, (0, 560), t)
        d = ImageDraw.Draw(img)
        for i in range(18):
            x_ = 60 + i * 68
            draw_stick_figure(d, x_, 620, scale=0.45,
                              shirt=C["blue"], hair=C["yellow"], progress=t)
        return img
    vw.animate(frame_crowd, 1.5, hold=0.8)
    return frame_crowd(1.0)


# ── LIÇÃO 5: ENERGIA ──────────────────────────────────────

def quadro_8_energia(vw):
    les = _lesson(4)   # "05_energia"
    labels = les.get("labels", {})

    vw.animate(lambda t: draw_title(blank_canvas(), les["titulo"],
                                    les["titulo_color"], t), 1.0, hold=0.1)
    base_t = blank_canvas()
    draw_title(base_t, les["titulo"], les["titulo_color"], 1.0)

    # Despertador (relógio — gestão de tempo)
    def frame_clock(t):
        img   = base_t.copy()
        asset = _asset(les, "despertador", scale=0.7)
        if asset:
            return reveal_pop(img, asset, (950, 390), t)
        draw_alarm_clock(ImageDraw.Draw(img), 948, 390, r=55, progress=t)
        return img
    vw.animate(frame_clock, 0.7, hold=0.15)
    base_clock = frame_clock(1.0)

    # Bateria cheia + quadro sol (energia alta)
    def frame_bat_full(t):
        img   = base_clock.copy()
        asset = _asset(les, "bateria_cheia", scale=0.65)
        if asset:
            img = reveal_organic(img, asset, (225, 480), t)
        else:
            draw_battery(ImageDraw.Draw(img), 180, 440, 92, 46, level=1.0, color=C["green"])
        asset2 = _asset(les, "quadro_sol", scale=0.55)
        if asset2 and t > 0.4:
            img = reveal_fade(img, asset2, (175, 260), (t-0.4)/0.6)
        return img
    vw.animate(frame_bat_full, 1.2, hold=0.1)
    base_full = frame_bat_full(1.0)

    # Bateria metade + quadro chuva (energia baixa)
    def frame_bat_half(t):
        img   = base_full.copy()
        asset = _asset(les, "bateria_metade", scale=0.65)
        if asset:
            img = reveal_organic(img, asset, (500, 480), t)
        else:
            draw_battery(ImageDraw.Draw(img), 462, 440, 92, 46, level=0.4, color=C["orange"])
        asset2 = _asset(les, "quadro_chuva", scale=0.55)
        if asset2 and t > 0.4:
            img = reveal_fade(img, asset2, (455, 260), (t-0.4)/0.6)
        return img
    vw.animate(frame_bat_half, 1.2, hold=0.1)
    base_half = frame_bat_half(1.0)

    # Círculo verde de destaque (bateria cheia)
    def frame_circle(t):
        img = base_half.copy()
        d   = ImageDraw.Draw(img)
        draw_imperfect_circle(d, 225, 480, r=85, color=C["green_v"],
                              width=5, progress=t)
        return img
    vw.animate(frame_circle, 0.9, hold=0.15)
    base_circle = frame_circle(1.0)

    # Labels de eficiência
    label_items = [
        (labels.get("eficiencia","MAIS EFICIÊNCIA"),     (225, 590), C["ink"]),
        (labels.get("producao","PRODUZ MAIS"),            (500, 590), C["ink"]),
        (labels.get("timing","TRABALHAR NO\nMOMENTO"),   (225, 660), C["green"]),
    ]
    label_base = base_circle
    for text, pos, color in label_items:
        def frame_lbl(t, _text=text, _pos=pos, _col=color, _base=label_base):
            img = _base.copy()
            draw_typewriter(ImageDraw.Draw(img), _text, _pos,
                            size=22, bold=True, color=_col, progress=t)
            return img
        vw.animate(frame_lbl, 0.8, hold=0.08)
        label_base = frame_lbl(1.0)

    # Personagens contrastantes
    def frame_energized(t):
        img   = label_base.copy()
        asset = _asset(les, "personagem_ativo", scale=0.7)
        if asset:
            return reveal_slide_left(img, asset, (80, 420), t)
        draw_stick_figure(ImageDraw.Draw(img), 135, 500, scale=0.9,
                          shirt=C["green"], hair=C["yellow"],
                          pose="arms_up", progress=t)
        return img
    vw.animate(frame_energized, 1.0, hold=0.15)
    base_en = frame_energized(1.0)

    def frame_exhausted(t):
        img   = base_en.copy()
        asset = _asset(les, "personagem_exausto", scale=0.7)
        if asset:
            return reveal_organic(img, asset, (1150, 500), t)
        draw_stick_figure(ImageDraw.Draw(img), 1150, 500, scale=0.9,
                          shirt=C["gray"], hair=C["gray_dark"],
                          pose="neutral", progress=t)
        return img
    vw.animate(frame_exhausted, 1.0, hold=0.8)
    return frame_exhausted(1.0)


# ── LIÇÃO 6: BOM DIA ──────────────────────────────────────

def quadro_9_bom_dia(vw):
    les  = _lesson(5)   # "06_bom_dia"
    grid = les.get("grid", {"rows":30,"cols":52,"label_x":"SEMANA DO ANO →"})

    vw.animate(lambda t: draw_title(blank_canvas(), les["titulo"],
                                    les["titulo_color"], t), 0.9, hold=0.1)
    base_t = blank_canvas()
    draw_title(base_t, les["titulo"], les["titulo_color"], 1.0)

    # Grade de semanas da vida
    GX, GY      = 252, 80
    SQ, GAP     = 11, 1
    COLS, ROWS  = grid["cols"], grid["rows"]

    def frame_grid(t):
        img = base_t.copy()
        d2  = ImageDraw.Draw(img)
        p_  = ease_in_out_cubic(t)
        n_  = int(COLS * ROWS * p_)
        for idx in range(n_):
            r_ = idx // COLS; c_ = idx % COLS
            x_ = GX + c_*(SQ+GAP); y_ = GY + r_*(SQ+GAP)
            d2.rectangle([x_,y_,x_+SQ,y_+SQ], outline=C["gray"], width=1)
        d2.text((GX + COLS*(SQ+GAP)//2, 68), grid.get("label_x",""),
                font=font(14,bold=True), fill=C["blue"], anchor="mm")
        return img
    vw.animate(frame_grid, 1.5, hold=0.08)
    base_grid = frame_grid(1.0)

    # Emojis preenchendo as primeiras 2 linhas
    def frame_emojis(t):
        img = base_grid.copy()
        d2  = ImageDraw.Draw(img)
        n_  = int(COLS * 2 * ease_in_out_cubic(t))
        for idx in range(n_):
            r_ = idx // COLS; c_ = idx % COLS
            x_ = GX + c_*(SQ+GAP); y_ = GY + r_*(SQ+GAP)
            d2.ellipse([x_,y_,x_+SQ,y_+SQ],
                       fill=C["yellow"], outline=C["ink"], width=1)
            d2.ellipse([x_+2,y_+2,x_+4,y_+4], fill=C["ink"])
            d2.ellipse([x_+7,y_+2,x_+9,y_+4], fill=C["ink"])
            d2.arc([x_+2,y_+5,x_+9,y_+9], 0, 180, fill=C["ink"], width=1)
        return img
    vw.animate(frame_emojis, 1.2, hold=0.15)
    base_em = frame_emojis(1.0)

    # Emoji gigante pop-in
    emoji_layer = Image.new("RGBA", (W, H), (0,0,0,0))
    draw_smiley(ImageDraw.Draw(emoji_layer), 942, 382, r=122, progress=1.0)

    def frame_ebig(t):
        return reveal_pop(base_em, emoji_layer, (942, 382), t, s=1.8)
    vw.animate(frame_ebig, 0.8, hold=0.25)
    base_ebig = frame_ebig(1.0)

    # Personagem triste (muitas semanas "cinza")
    def frame_gray(t):
        img   = base_ebig.copy()
        asset = _asset(les, "personagem_triste", scale=0.7)
        if asset:
            return reveal_organic(img, asset, (102, 620), t)
        d = ImageDraw.Draw(img)
        p_ = ease_out_quad(t)
        gs = int(155*p_)
        draw_stick_figure(d, 102, 562, scale=0.75, shirt=(gs,gs,gs),
                          hair=(gs,gs,gs), progress=t)
        if p_ > 0.82:
            d.text((58, 668), "50 SEMANAS", font=font(16,bold=True), fill=C["gray_dark"])
        return img
    vw.animate(frame_gray, 0.8, hold=0.18)
    base_gray = frame_gray(1.0)

    # Personagem feliz (2 semanas boas = diferença)
    def frame_happy(t):
        img   = base_gray.copy()
        asset = _asset(les, "personagem_feliz", scale=0.7)
        if asset:
            return reveal_pop(img, asset, (222, 600), t)
        draw_stick_figure(ImageDraw.Draw(img), 222, 558, scale=0.8,
                          shirt=C["orange"], hair=C["yellow"],
                          pose="arms_up", progress=t)
        if t > 0.82:
            ImageDraw.Draw(img).text((222, 662), "2 SEMANAS!",
                                     font=font(16,bold=True), fill=C["ink"], anchor="mm")
        return img
    vw.animate(frame_happy, 0.7, hold=0.18)
    base_happy = frame_happy(1.0)

    # Texto conclusivo
    def frame_sat(t):
        img = base_happy.copy()
        draw_typewriter(ImageDraw.Draw(img), les["texto_principal"],
                        (1022, 322), size=22, bold=True,
                        color=C["ink"], progress=t)
        return img
    vw.animate(frame_sat, 1.0, hold=0.18)
    base_sat = frame_sat(1.0)

    # Trabalhador satisfeito
    def frame_worker(t):
        img   = base_sat.copy()
        asset = _asset(les, "trabalhador", scale=0.7)
        if asset:
            return reveal_slide_bottom(img, asset, (1020, 450), t)
        d = ImageDraw.Draw(img)
        p_ = ease_out_back(t)
        xo = int(40*(1-p_))
        d.rectangle([1002+xo,492,1232,622], fill=(30,30,100), outline=C["ink"], width=2)
        d.rectangle([1012+xo,502,1222,612], fill=(20,20,80))
        pts_w = [(1015+xo,602),(1045+xo,572),(1082+xo,555),
                 (1115+xo,572),(1145+xo,545),(1160+xo,565)]
        d.line(pts_w, fill=C["green"], width=3)
        draw_stick_figure(d, 1102, 485, scale=0.72,
                          shirt=(80,102,182), hair=C["yellow"], progress=t)
        return img
    vw.animate(frame_worker, 0.8, hold=0.8)
    return frame_worker(1.0)


# ── FINAL: VISÃO GERAL + LOGO ─────────────────────────────

def quadro_10_final(vw):
    """Zoom-out mostrando todas as lições + logo animado."""
    overview = blank_canvas()
    d        = ImageDraw.Draw(overview)

    px,py,pw,ph = 222, 52, 842, 605
    draw_hand_rect(d, (px,py), (pw,ph), progress=1.0, color=C["blue"], width=4)
    draw_typewriter(d, INTRO["titulo_painel"], (px+pw//2, py+20),
                    size=22, bold=True, color=C["blue"], align="center")

    labels  = INTRO["labels"]
    mini_cl = [C.get(lc, C["ink"]) for _, lc in labels]
    cols_n, rows_n = 2, 3
    sw_ = (pw-50)//cols_n; sh_ = (ph-90)//rows_n
    for i, ((lbl, _), mc) in enumerate(zip(labels, mini_cl)):
        c_ = i % 2; r_ = i // 2
        rx_ = px+20+c_*(sw_+10); ry_ = py+55+r_*(sh_+10)
        d.rounded_rectangle([rx_,ry_,rx_+sw_-10,ry_+sh_-10],
                             radius=6, outline=C["ink"], width=2,
                             fill=(250,250,250))
        d.text((rx_+12,ry_+12), lbl, font=font(18,bold=True), fill=mc)

    asset_p = load_asset(INTRO.get("asset_personagem",""))
    if asset_p:
        overview = reveal_organic(overview, asset_p, (122, 360), 1.0)
    else:
        draw_stick_figure(d, 122, 362, scale=1.05, shirt=C["red"],
                          hair=C["yellow"], pose="pointing", progress=1.0)

    def frame_ov(t):
        p_ = ease_in_out_cubic(t)
        return Image.blend(blank_canvas(), overview, p_)
    vw.animate(frame_ov, 1.5, hold=1.5)

    def frame_fade(t):
        return Image.blend(overview, blank_canvas(), ease_in_out_cubic(t))
    vw.animate(frame_fade, 1.0, hold=0.08)

    # Logo animado
    logo_base = blank_canvas()
    dl        = ImageDraw.Draw(logo_base)
    bx, by    = 362, 362

    logo_asset = load_asset(FINAL.get("asset_logo",""))
    if logo_asset:
        logo_base = reveal_pop(logo_base, logo_asset, (bx, by), 1.0)
    else:
        dl.ellipse([bx-78,by-115,bx+78,by+58], fill=C["white"], outline=C["ink"], width=4)
        dl.rectangle([bx-30,by+58,bx+30,by+105], fill=(200,200,200), outline=C["ink"], width=3)
        draw_brain(dl, bx, by-22, r=64, progress=1.0)

    def frame_logo(t):
        img = logo_base.copy()
        d2  = ImageDraw.Draw(img)
        p_  = ease_out_back(t, s=1.5)

        # Raios de luz
        if p_ > 0.1:
            for ang in range(0,360,45):
                rad = math.radians(ang)
                r1 = 92; r2 = int(92+32*p_)
                d2.line([bx+int(r1*math.cos(rad)),by-22+int(r1*math.sin(rad)),
                         bx+int(r2*math.cos(rad)),by-22+int(r2*math.sin(rad))],
                        fill=C["yellow"], width=max(1,int(3*p_)))

        # Nome do canal (typewriter)
        txt_full = FINAL["nome_canal"]
        n_  = max(0, int(len(txt_full) * ease_in_out_cubic(t)))
        d2.text((bx+115, by-38), txt_full[:n_],
                font=font(44,bold=True), fill=C["ink"])

        # Subtítulo
        if t > 0.7:
            d2.text((bx+115, by+22), FINAL["subtitulo"],
                    font=font(22,False), fill=C["gray_dark"])

        # Logo texto (asset PNG se existir)
        logo_txt = load_asset(FINAL.get("asset_texto",""), scale=0.9)
        if logo_txt and t > 0.5:
            img = reveal_wipe_lr(img, logo_txt, (bx+110, by-42), (t-0.5)/0.5)
            d2  = ImageDraw.Draw(img)
        return img

    vw.animate(frame_logo, 2.2, hold=2.8)


# ══════════════════════════════════════════════════════════
# MAIN — Orquestração com câmera virtual entre lições
# ══════════════════════════════════════════════════════════

def main():
    out_path = SETTINGS["output_path"]
    vw       = VideoWriter(out_path)

    print("🎬 SejaUmaPessoaMelhor — Whiteboard Engine v2.0")
    print(f"   Resolução: {W}×{H} @ {FPS}fps")
    print(f"   Saída: {out_path}\n")

    t0 = time.time()

    # ── Intro ──────────────────────────────────────────────
    print("  [1/10] Intro — personagem draw-on...")
    quadro_1_intro(vw)

    print("  [2/10] Painel + borda animada...")
    rects, base_panel = quadro_2_panel(vw)

    print("  [3/10] Números pop-in elástico...")
    last = quadro_3_numbers(vw, rects, base_panel)

    # ── Lições com câmera virtual entre elas ──────────────
    lesson_fns = [
        ("SAÚDE NÃO É UM LUXO",       quadro_4_saude,    "down"),
        ("CONTROLE SEU AMBIENTE",      quadro_5_ambiente, "right"),
        ("NÃO MINTA PARA SI MESMO",    quadro_6_mentira,  "up"),
        ("LEIA SEMPRE",                quadro_7_leitura,  "left"),
        ("GERENCIE SUA ENERGIA",       quadro_8_energia,  "down"),
        ("TENHA UM BOM DIA",           quadro_9_bom_dia,  None),
    ]

    prev_frame = last

    for i, (name, fn, direction) in enumerate(lesson_fns, 4):
        print(f"  [{i}/10] {name}...")

        # Transição de câmera antes de cada lição (exceto a 1ª após números)
        if i > 4 and direction and prev_frame is not None:
            # Renderiza primeiro frame da lição de forma "lazy"
            def _get_first_frame(_fn=fn):
                canvas = blank_canvas()
                d = ImageDraw.Draw(canvas)
                return canvas  # frame em branco — lição começa logo depois

            camera_transition(vw, _get_first_frame, direction,
                              prev_frame=prev_frame)

        prev_frame = fn(vw)

    # ── Final ──────────────────────────────────────────────
    print("  [10/10] Logo final animado...")
    quadro_10_final(vw)

    vw.release()

    elapsed = time.time() - t0
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    frames  = vw.frame_count
    dur_s   = frames / FPS

    print(f"\n✅  Vídeo salvo: {out_path}")
    print(f"    Frames  : {frames}")
    print(f"    Duração : ~{dur_s:.0f}s ({dur_s/60:.1f} min)")
    print(f"    Render  : {elapsed:.1f}s")
    print(f"    Tamanho : {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
