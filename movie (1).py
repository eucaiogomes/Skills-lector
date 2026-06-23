"""
movie.py — Whiteboard Animation "SejaUmaPessoaMelhor" — VERSÃO TURBINADA
Animações profissionais estilo After Effects usando OpenCV + Pillow + NumPy

Resolução: 1280x720 @ 24fps
Imagens opcionais em: assets/<nome>.png (fundo transparente)
Saída: output/video_sejaumapessoamelhor.mp4
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys, math, textwrap, time

# ══════════════════════════════════════════════════════════
# CONFIG GLOBAL
# ══════════════════════════════════════════════════════════
W, H   = 1280, 720
FPS    = 24
ASSETS = "assets"
OUT    = "output"
os.makedirs(OUT, exist_ok=True)

FONT_BOLD   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_NORMAL = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Paleta whiteboard premium
WHITE      = (255, 255, 255)
OFF_WHITE  = (252, 251, 248)
BLACK      = (15,  12,  10)
RED        = (220, 35,  35)
BLUE       = (25,  80,  210)
BLUE_LIGHT = (180, 210, 255)
GREEN      = (30,  165, 60)
GREEN_V    = (40,  200, 70)
YELLOW     = (255, 205, 20)
ORANGE     = (240, 125, 20)
GRAY       = (155, 155, 155)
GRAY_DARK  = (80,  80,  80)
PINK       = (255, 180, 195)
BROWN      = (140, 80,  30)
PURPLE     = (130, 60,  200)

# ══════════════════════════════════════════════════════════
# EASING FUNCTIONS
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

def ease_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def ease_out_bounce(t):
    n1, d1 = 7.5625, 2.75
    t = max(0.0, min(1.0, t))
    if t < 1/d1:         return n1 * t * t
    elif t < 2/d1:       t -= 1.5/d1;   return n1*t*t + 0.75
    elif t < 2.5/d1:     t -= 2.25/d1;  return n1*t*t + 0.9375
    else:                t -= 2.625/d1; return n1*t*t + 0.984375

def lerp(a, b, t): return a + (b - a) * t

# ══════════════════════════════════════════════════════════
# CANVAS & HELPERS
# ══════════════════════════════════════════════════════════

def blank_canvas():
    img = Image.new("RGB", (W, H), OFF_WHITE)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(35):
        alpha = int(i * 1.8)
        d.rectangle([i, i, W-i, H-i], outline=(200, 195, 185, alpha), width=1)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def pil2cv(img): return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)

def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_NORMAL, max(8, size))

def load_asset(name, size=None):
    path = os.path.join(ASSETS, name)
    if not os.path.exists(path): return None
    img = Image.open(path).convert("RGBA")
    if size: img = img.resize(size, Image.LANCZOS)
    return img

def paste_asset(base, name, xy, size=None, alpha=1.0):
    img = load_asset(name, size)
    if img is None: return base
    if alpha < 1.0:
        r,g,b,a = img.split()
        a = a.point(lambda p: int(p * alpha))
        img.putalpha(a)
    base = base.convert("RGBA")
    base.paste(img, xy, img)
    return base.convert("RGB")

# ══════════════════════════════════════════════════════════
# REVEAL EFFECTS (AE-style)
# ══════════════════════════════════════════════════════════

def apply_box_reveal(base, overlay, pos, progress, direction="left"):
    p = ease_in_out_cubic(progress)
    ow, oh = overlay.size
    if direction == "left":
        rw = int(ow * p)
        if rw <= 0: return base
        crop = overlay.crop((0, 0, rw, oh))
        result = base.convert("RGBA")
        result.paste(crop, pos, crop)
    elif direction == "bottom":
        rh = int(oh * p)
        if rh <= 0: return base
        crop = overlay.crop((0, oh-rh, ow, oh))
        result = base.convert("RGBA")
        result.paste(crop, (pos[0], pos[1]+oh-rh), crop)
    else:
        result = base.convert("RGBA")
    return result.convert("RGB")

def apply_radial_reveal(base, overlay, center, progress):
    p = ease_out_quad(progress)
    ow, oh = overlay.size
    mask = Image.new("L", (ow, oh), 0)
    dm = ImageDraw.Draw(mask)
    max_r = int(math.hypot(ow, oh) * p + 1)
    cx, cy = ow//2, oh//2
    dm.ellipse([cx-max_r, cy-max_r, cx+max_r, cy+max_r], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(10))
    r,g,b,a = overlay.split()
    new_a = Image.composite(a, Image.new("L",(ow,oh),0), mask)
    overlay2 = Image.merge("RGBA", (r,g,b,new_a))
    result = base.convert("RGBA")
    result.paste(overlay2, center, overlay2)
    return result.convert("RGB")

def apply_pop_in(base, overlay, center, progress):
    p = ease_out_back(progress)
    p = max(0.001, p)
    ow, oh = overlay.size
    nw = max(1, int(ow*p)); nh = max(1, int(oh*p))
    scaled = overlay.resize((nw, nh), Image.LANCZOS)
    px = center[0] - nw//2; py = center[1] - nh//2
    result = base.convert("RGBA")
    result.paste(scaled, (px, py), scaled)
    return result.convert("RGB")

def apply_fade(base, overlay, pos, progress):
    p = ease_out_quad(progress)
    r,g,b,a = overlay.split()
    new_a = a.point(lambda x: int(x*p))
    overlay2 = Image.merge("RGBA", (r,g,b,new_a))
    result = base.convert("RGBA")
    result.paste(overlay2, pos, overlay2)
    return result.convert("RGB")

def apply_slide_from_bottom(base, overlay, target_pos, progress):
    p = ease_out_back(progress, s=1.2)
    tx, ty = target_pos
    cur_y = int(lerp(H+50, ty, p))
    result = base.convert("RGBA")
    result.paste(overlay, (tx, cur_y), overlay)
    return result.convert("RGB")

def apply_slide_from_left(base, overlay, target_pos, progress):
    p = ease_out_cubic(progress)
    tx, ty = target_pos
    cur_x = int(lerp(-overlay.width-20, tx, p))
    result = base.convert("RGBA")
    result.paste(overlay, (cur_x, ty), overlay)
    return result.convert("RGB")

# ══════════════════════════════════════════════════════════
# DRAWING ELEMENTS
# ══════════════════════════════════════════════════════════

def draw_on_text(draw, text, xy, size=28, color=BLACK, bold=False,
                 progress=1.0, max_chars=36):
    fnt = font(size, bold)
    lines = textwrap.wrap(text, width=max_chars)
    full = "\n".join(lines)
    n = int(len(full) * ease_in_out_cubic(progress))
    visible = full[:n]
    x, y = xy
    lh = size + 8
    for line in visible.split("\n"):
        draw.text((x, y), line, font=fnt, fill=color)
        y += lh

def draw_on_text_center(draw, text, cx, cy, size=28, color=BLACK,
                         bold=False, progress=1.0):
    fnt = font(size, bold)
    n = int(len(text) * ease_in_out_cubic(progress))
    visible = text[:n]
    bb = draw.textbbox((0,0), visible, font=fnt)
    draw.text((cx-(bb[2]-bb[0])//2, cy), visible, font=fnt, fill=color)

def draw_hand_rect(draw, xy, wh, progress=1.0, color=BLACK, width=3):
    x,y = xy; rw,rh = wh
    p = ease_in_out_cubic(progress)
    perim = 2*(rw+rh)
    dist = perim*p
    pts = [(x,y),(x+rw,y),(x+rw,y+rh),(x,y+rh),(x,y)]
    segs = [rw,rh,rw,rh]
    drawn = 0
    for i in range(4):
        s = segs[i]
        if drawn+s <= dist:
            draw.line([pts[i], pts[i+1]], fill=color, width=width)
            drawn += s
        else:
            rem = dist - drawn
            t_ = rem/s if s>0 else 0
            mx = int(lerp(pts[i][0], pts[i+1][0], t_))
            my = int(lerp(pts[i][1], pts[i+1][1], t_))
            draw.line([pts[i], (mx,my)], fill=color, width=width)
            break

def draw_title_animated(img, text, color=RED, progress=1.0):
    d = ImageDraw.Draw(img)
    fnt = font(36, bold=True)
    p = ease_out_quad(progress)
    n = max(0, int(len(text)*p))
    visible = text[:n]
    bb = d.textbbox((0,0), text, font=fnt)
    tw = bb[2]-bb[0]
    tx = (W-tw)//2; ty = 22
    d.text((tx,ty), visible, font=fnt, fill=color)
    if p > 0.85:
        uw = int(tw*(p-0.85)/0.15)
        d.rectangle([tx, ty+46, tx+uw, ty+50], fill=color)
    return img

def draw_arrow(draw, x1,y1,x2,y2, color=BLUE, width=4, progress=1.0):
    p = ease_in_out_cubic(progress)
    ex = int(x1+(x2-x1)*p); ey = int(y1+(y2-y1)*p)
    draw.line([(x1,y1),(ex,ey)], fill=color, width=width)
    if p > 0.9:
        ang = math.atan2(y2-y1,x2-x1)
        hs = 16
        for sign in [-1,1]:
            ax = ex - int(hs*math.cos(ang - sign*0.5))
            ay = ey - int(hs*math.sin(ang - sign*0.5))
            draw.line([(ex,ey),(ax,ay)], fill=color, width=width)

def draw_stick_figure(draw, cx, cy, scale=1.0, shirt=RED, hair=YELLOW,
                      pose="neutral", progress=1.0):
    s = scale
    p = ease_out_quad(progress)
    if p <= 0: return
    r = int(22*s)
    # Cabeça
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=BLACK, fill=WHITE,
                 width=max(1,int(3*s)))
    # Cabelo espetado
    if p > 0.15:
        for angle in range(-70,71,25):
            rad = math.radians(angle-90)
            hx = cx+int((r+9*s)*math.cos(rad))
            hy = cy+int((r+9*s)*math.sin(rad))
            draw.line([cx+int(r*math.cos(rad)), cy+int(r*math.sin(rad)),
                       hx, hy], fill=hair, width=max(1,int(3*s)))
    # Olhos
    if p > 0.25:
        eo = int(8*s); er = int(3*s)
        draw.ellipse([cx-eo-er, cy-er, cx-eo+er, cy+er], fill=BLACK)
        draw.ellipse([cx+eo-er, cy-er, cx+eo+er, cy+er], fill=BLACK)
    # Sorriso
    if p > 0.35:
        draw.arc([cx-int(10*s),cy+int(4*s),cx+int(10*s),cy+int(16*s)],
                 0,180, fill=BLACK, width=max(1,int(2*s)))
    body_top = cy+r; body_bot = cy+int(90*s); sw = int(28*s)
    # Camisa
    if p > 0.45:
        draw.rectangle([cx-sw, body_top, cx+sw, body_bot],
                       fill=shirt, outline=BLACK, width=max(1,int(2*s)))
    # Braços
    if p > 0.6:
        if pose == "pointing":
            draw.line([cx+sw,cy+int(40*s), cx+int(75*s),cy+int(22*s)],
                      fill=BLACK, width=max(1,int(3*s)))
            draw.polygon([(cx+int(75*s),cy+int(22*s)),
                          (cx+int(62*s),cy+int(17*s)),
                          (cx+int(65*s),cy+int(32*s))], fill=BLACK)
            draw.line([cx-sw,cy+int(40*s), cx-int(50*s),cy+int(68*s)],
                      fill=BLACK, width=max(1,int(3*s)))
        elif pose == "arms_up":
            draw.line([cx-sw,cy+int(35*s), cx-int(55*s),cy-int(15*s)],
                      fill=BLACK, width=max(1,int(3*s)))
            draw.line([cx+sw,cy+int(35*s), cx+int(55*s),cy-int(15*s)],
                      fill=BLACK, width=max(1,int(3*s)))
        elif pose == "shrug":
            draw.line([cx-sw,cy+int(32*s), cx-int(50*s),cy+int(18*s)],
                      fill=BLACK, width=max(1,int(3*s)))
            draw.line([cx+sw,cy+int(32*s), cx+int(50*s),cy+int(18*s)],
                      fill=BLACK, width=max(1,int(3*s)))
        else:
            draw.line([cx-sw,cy+int(40*s), cx-int(50*s),cy+int(68*s)],
                      fill=BLACK, width=max(1,int(3*s)))
            draw.line([cx+sw,cy+int(40*s), cx+int(50*s),cy+int(68*s)],
                      fill=BLACK, width=max(1,int(3*s)))
    # Pernas
    if p > 0.8:
        draw.line([cx-int(12*s), body_bot, cx-int(18*s), cy+int(155*s)],
                  fill=BLACK, width=max(1,int(3*s)))
        draw.line([cx+int(12*s), body_bot, cx+int(18*s), cy+int(155*s)],
                  fill=BLACK, width=max(1,int(3*s)))

def draw_battery(draw, x, y, w, h, level=1.0, color=GREEN,
                 animated=False, t_anim=0.0):
    bw = 3
    draw.rectangle([x,y,x+w,y+h], outline=BLACK, width=bw, fill=WHITE)
    draw.rectangle([x+w//3, y-8, x+2*w//3, y], fill=BLACK)
    inner_h = max(0, int((h-bw*2)*level))
    fc = color
    if animated:
        pulse = 0.85+0.15*math.sin(t_anim*4)
        fc = tuple(min(255,int(c*pulse)) for c in color)
    if inner_h > 0:
        draw.rectangle([x+bw, y+h-bw-inner_h, x+w-bw, y+h-bw], fill=fc)
    if level > 0.3:
        mx = x+w//2; my = y+h//2
        draw.polygon([(mx-4,my-8),(mx+2,my-2),(mx-2,my+2),(mx+4,my+8),
                      (mx-1,my+1),(mx+3,my-4)], fill=WHITE)

def draw_brain(draw, cx, cy, r=45, progress=1.0):
    p = ease_out_quad(progress)
    draw.pieslice([cx-r,cy-int(r*0.8),cx+r,cy+int(r*0.8)], 90,270,
                  fill=BLUE, outline=BLACK, width=max(1,int(3*p)))
    draw.pieslice([cx-r,cy-int(r*0.8),cx+r,cy+int(r*0.8)], 270,90,
                  fill=RED, outline=BLACK, width=max(1,int(3*p)))
    draw.line([cx,cy-int(r*0.8),cx,cy+int(r*0.8)], fill=BLACK, width=2)
    if p > 0.5:
        draw.arc([cx-r//2,cy-r//2,cx,cy], 0,180, fill=BLACK, width=2)
        draw.arc([cx,cy-r//2,cx+r//2,cy], 0,180, fill=BLACK, width=2)

def draw_smiley(draw, cx, cy, r=40, color=YELLOW, sad=False, progress=1.0):
    p = ease_out_bounce(progress)
    cr = max(1, int(r*p))
    draw.ellipse([cx-cr,cy-cr,cx+cr,cy+cr], fill=color, outline=BLACK,
                 width=max(1,int(r/12)))
    if p < 0.5: return
    eo = int(r*0.32); er = max(1,int(r*0.1))
    draw.ellipse([cx-eo-er,cy-int(r*0.18)-er,cx-eo+er,cy-int(r*0.18)+er], fill=BLACK)
    draw.ellipse([cx+eo-er,cy-int(r*0.18)-er,cx+eo+er,cy-int(r*0.18)+er], fill=BLACK)
    if sad:
        draw.arc([cx-int(r*0.5),cy+int(r*0.3),cx+int(r*0.5),cy+int(r*0.7)],
                 180,360, fill=BLACK, width=max(1,int(r*0.1)))
    else:
        draw.arc([cx-int(r*0.5),cy+int(r*0.08),cx+int(r*0.5),cy+int(r*0.55)],
                 0,180, fill=BLACK, width=max(1,int(r*0.1)))

def draw_thought_bubble(draw, text, cx, cy, w=320, h=90, progress=1.0):
    p = ease_out_back(progress)
    if p <= 0: return
    nw = max(10,int(w*p)); nh = max(10,int(h*p))
    nx = cx-nw//2; ny = cy-nh//2
    draw.rounded_rectangle([nx,ny,nx+nw,ny+nh], radius=int(20*p),
                            fill=WHITE, outline=BLACK, width=max(1,int(3*p)))
    if p > 0.65:
        fnt = font(max(10,int(21*p)), bold=True)
        draw.text((cx,cy), text, font=fnt, fill=BLACK, anchor="mm")
    for i,r_ in enumerate([6,4,2]):
        dy = nh//2+10+i*12
        if ny+dy < H:
            draw.ellipse([cx-r_,ny+dy-r_,cx+r_,ny+dy+r_], fill=BLACK)

def draw_speech_rect(draw, text, rx, ry, w=280, h=70, progress=1.0):
    p = ease_out_back(progress, s=1.5)
    if p <= 0: return
    nw = max(10,int(w*p)); nh = max(10,int(h*p))
    draw.rounded_rectangle([rx,ry,rx+nw,ry+nh], radius=10,
                            fill=WHITE, outline=BLACK, width=max(1,int(2*p)))
    if p > 0.7:
        fnt = font(max(10,int(20*p)), bold=True)
        draw.text((rx+nw//2,ry+nh//2), text, font=fnt, fill=BLACK, anchor="mm")
    if p > 0.8:
        draw.polygon([(rx+nw//4,ry+nh),(rx+nw//4+20,ry+nh),
                      (rx+nw//4-10,ry+nh+20)], fill=BLACK)

def draw_book_stack(draw, x, y, n=5, progress=1.0):
    colors_ = [(220,50,50),(50,150,220),(50,180,80),(220,180,40),(130,70,200)]
    bh = 24; bw = 130
    p = ease_out_quad(progress)
    for i in range(n):
        alpha_i = min(1.0, p*n - i)
        if alpha_i <= 0: continue
        c = colors_[i%len(colors_)]
        by_ = y - i*bh
        draw.rectangle([x, by_, x+bw, by_+bh], fill=c, outline=BLACK, width=2)
        draw.line([x+10, by_, x+10, by_+bh], fill=BLACK, width=2)
        draw.line([x+18, by_+7, x+bw-8, by_+7], fill=WHITE, width=2)

def draw_alarm_clock(draw, cx, cy, r=55, progress=1.0):
    p = ease_out_back(progress)
    if p <= 0: return
    cr = max(1,int(r*p))
    draw.ellipse([cx-cr,cy-cr,cx+cr,cy+cr], fill=RED, outline=BLACK,
                 width=max(1,int(4*p)))
    draw.ellipse([cx-int(cr*0.85),cy-int(cr*0.85),cx+int(cr*0.85),cy+int(cr*0.85)],
                 fill=WHITE, outline=BLACK, width=max(1,int(2*p)))
    if p > 0.5:
        draw.line([cx,cy,cx,cy-int(cr*0.6)], fill=BLACK, width=max(1,int(4*p)))
        draw.line([cx,cy,cx+int(cr*0.4),cy-int(cr*0.2)], fill=BLACK,
                  width=max(1,int(4*p)))
    if p > 0.7:
        for sign in [-1,1]:
            bx_ = cx+sign*int(cr*0.65)
            draw.ellipse([bx_-int(cr*0.2),cy-cr-int(cr*0.3),
                          bx_+int(cr*0.2),cy-cr+int(cr*0.15)],
                         fill=RED, outline=BLACK, width=max(1,int(2*p)))

def draw_fridge(draw, x, y, w, h, progress=1.0):
    p = ease_out_quad(progress)
    ph = max(1, int(h*p))
    draw.rounded_rectangle([x,y+h-ph,x+w,y+h], radius=8,
                            fill=(215,215,215), outline=BLACK, width=max(1,int(3*p)))
    div_y = y+int(h*0.42)
    if div_y > y+h-ph:
        draw.line([x,div_y,x+w,div_y], fill=BLACK, width=2)
    hx_ = x+w-20; hw_ = 12
    if p > 0.5:
        draw.rounded_rectangle([hx_,y+h-ph+25,hx_+hw_,y+h-ph+55],
                                radius=4, fill=GRAY_DARK)
    if p > 0.85:
        for fx,fy,fc,fr in [(x+25,div_y-30,(255,60,60),13),
                            (x+60,div_y-32,(255,200,0),11),
                            (x+93,div_y-30,(50,200,50),13)]:
            if fy > y+h-ph:
                draw.ellipse([fx-fr,fy-fr,fx+fr,fy+fr], fill=fc, outline=BLACK, width=2)

def draw_gravestone(draw, cx, cy, progress=1.0):
    p = ease_out_quad(progress)
    w, h = 90, 110
    ph = max(1,int(h*p))
    x, y = cx-w//2, cy-h//2
    draw.rectangle([x,cy-h//2+h-ph,x+w,cy+h//2], fill=(160,160,160),
                   outline=BLACK, width=3)
    if p > 0.7:
        draw.ellipse([x,y,x+w,y+w//1.5], fill=(160,160,160), outline=BLACK, width=3)
    if p > 0.85:
        draw.text((cx,cy+5), "R.I.P", font=font(20,bold=True), fill=BLACK, anchor="mm")

def draw_imperfect_circle(draw, cx, cy, r, color, width=5, progress=1.0):
    p = ease_in_out_cubic(progress)
    n = 60
    pts = []
    for i in range(n):
        ang = (i/n)*2*math.pi
        jitter = 1+0.04*math.sin(ang*7+1.2)+0.03*math.cos(ang*11)
        pts.append((cx+int(r*jitter*math.cos(ang)), cy+int(r*jitter*math.sin(ang))))
    n_draw = max(2, int(len(pts)*p))
    for i in range(n_draw-1):
        draw.line([pts[i], pts[(i+1)%n_draw]], fill=color, width=width)

# ══════════════════════════════════════════════════════════
# VIDEO WRITER WRAPPER
# ══════════════════════════════════════════════════════════

class VideoWriter:
    def __init__(self, path):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.vw = cv2.VideoWriter(path, fourcc, FPS, (W,H))
        if not self.vw.isOpened():
            raise RuntimeError("VideoWriter falhou")
        self.frame_count = 0

    def write_pil(self, img):
        self.vw.write(pil2cv(img))
        self.frame_count += 1

    def write_n(self, img, seconds):
        n = max(1, int(seconds*FPS))
        frame = pil2cv(img)
        for _ in range(n):
            self.vw.write(frame)
            self.frame_count += 1

    def animate(self, frame_fn, duration, hold=0.2):
        n = max(2, int(duration*FPS))
        last = None
        for i in range(n):
            t = i/(n-1)
            img = frame_fn(t)
            self.write_pil(img)
            last = img
        if hold > 0 and last is not None:
            self.write_n(last, hold)

    def release(self):
        self.vw.release()

# ══════════════════════════════════════════════════════════
# QUADROS
# ══════════════════════════════════════════════════════════

def quadro_1_intro(vw):
    """Personagem sendo desenhado progressivamente."""
    def frame(t):
        img = blank_canvas()
        d = ImageDraw.Draw(img)
        draw_stick_figure(d, 185, 295, scale=1.15, shirt=RED, hair=YELLOW,
                          pose="pointing", progress=t)
        return img
    vw.animate(frame, 1.8, hold=0.1)

    base = frame(1.0)
    def frame2(t):
        img = base.copy()
        d = ImageDraw.Draw(img)
        draw_arrow(d, 268, 270, 415, 265, color=BLACK, width=3, progress=t)
        return img
    vw.animate(frame2, 0.5, hold=0.3)


def quadro_2_panel(vw):
    """Painel principal com borda azul + 6 retângulos."""
    base = blank_canvas()
    d = ImageDraw.Draw(base)
    draw_stick_figure(d, 185, 295, scale=1.15, shirt=RED, hair=YELLOW,
                      pose="pointing", progress=1.0)
    draw_arrow(d, 268, 270, 415, 265, color=BLACK, width=3, progress=1.0)

    PX, PY, PW, PH = 425, 48, 828, 638

    # Borda azul sendo desenhada
    def frame_border(t):
        img = base.copy()
        d2 = ImageDraw.Draw(img)
        draw_hand_rect(d2, (PX,PY), (PW,PH), progress=t, color=BLUE, width=4)
        return img
    vw.animate(frame_border, 1.2, hold=0.1)

    # Título typewriter
    base2 = frame_border(1.0)
    def frame_title(t):
        img = base2.copy()
        d2 = ImageDraw.Draw(img)
        draw_on_text_center(d2, "EXPERIÊNCIA, REFLEXÃO E CONSELHOS",
                            PX+PW//2, PY+20, size=26, color=BLUE, bold=True, progress=t)
        return img
    vw.animate(frame_title, 1.5, hold=0.1)

    # 6 retângulos
    cols, rows = 2, 3
    sw = (PW-60)//cols; sh = (PH-100)//rows
    rects = []
    for r in range(rows):
        for c in range(cols):
            rects.append((PX+20+c*(sw+10), PY+65+r*(sh+10), sw-10, sh-10))

    base_t = frame_title(1.0)
    for i,(rx,ry,rw,rh) in enumerate(rects):
        prev_base = base_t.copy()
        d_prev = ImageDraw.Draw(prev_base)
        for j in range(i):
            prx,pry,prw,prh = rects[j]
            draw_hand_rect(d_prev,(prx,pry),(prw,prh),progress=1.0,color=BLACK,width=2)

        def frame_rect(t, _px=rx,_py=ry,_pw=rw,_ph=rh,_pb=prev_base):
            img = _pb.copy()
            d2 = ImageDraw.Draw(img)
            draw_hand_rect(d2,(_px,_py),(_pw,_ph),progress=t,color=BLACK,width=2)
            return img
        vw.animate(frame_rect, 0.5, hold=0.08)
        base_t = frame_rect(1.0)

    return rects, base_t


def quadro_3_numbers(vw, rects, base_img):
    """Números 1-6 com pop-in elástico."""
    base = base_img.copy()
    for i in range(6):
        rx,ry,rw,rh = rects[i]
        prev = base.copy()
        dp = ImageDraw.Draw(prev)
        for j in range(i):
            prx,pry,_,_ = rects[j]
            dp.text((prx+14,pry+10), str(j+1), font=font(52,bold=True), fill=BLACK)

        def frame_num(t, _i=i, _rx=rx, _ry=ry, _pb=prev):
            img = _pb.copy()
            d2 = ImageDraw.Draw(img)
            p = ease_out_back(t)
            sz = max(8,int(52*p))
            d2.text((_rx+14,_ry+10), str(_i+1), font=font(sz,bold=True), fill=BLACK)
            return img
        vw.animate(frame_num, 0.38, hold=0.05)
        base = frame_num(1.0)

    vw.write_n(base, 0.6)
    return base


def quadro_4_saude(vw):
    """SAÚDE NÃO É UM LUXO, ELA É A BASE."""
    vw.animate(lambda t: draw_title_animated(blank_canvas(),
               "SAÚDE NÃO É UM LUXO, ELA É A BASE", progress=t), 1.0, hold=0.1)
    base_t = blank_canvas()
    draw_title_animated(base_t, "SAÚDE NÃO É UM LUXO, ELA É A BASE", progress=1.0)

    # Sofá + homem lendo
    sofa = Image.new("RGBA", (W,H), (0,0,0,0))
    ds = ImageDraw.Draw(sofa)
    ds.rectangle([80,440,510,565], fill=BROWN, outline=BLACK, width=3)
    ds.rectangle([80,370,135,455], fill=(120,75,30), outline=BLACK, width=2)
    ds.rectangle([460,370,510,455], fill=(120,75,30), outline=BLACK, width=2)
    ds.ellipse([112,365,172,425], outline=BLACK, fill=(255,225,190), width=3)
    for ang in [-60,-30,0,30,60]:
        rad = math.radians(ang-90)
        r_ = 30
        ds.line([142+int(r_*math.cos(rad)),395+int(r_*math.sin(rad)),
                 142+int((r_+8)*math.cos(rad)),395+int((r_+8)*math.sin(rad))],
                fill=YELLOW, width=2)
    ds.rectangle([172,392,435,440], fill=RED, outline=BLACK, width=2)
    ds.rectangle([345,348,435,395], fill=BLUE, outline=BLACK, width=2)
    ds.line([390,348,390,395], fill=WHITE, width=1)
    ds.ellipse([210,440,310,478], fill=WHITE, outline=BLACK, width=2)
    ds.ellipse([230,448,290,470], fill=(255,185,85))

    def frame_sofa(t):
        return apply_box_reveal(base_t, sofa, (0,0), t, direction="bottom")
    vw.animate(frame_sofa, 1.5, hold=0.2)
    base_sofa = frame_sofa(1.0)

    # Balão de pensamento
    def frame_bubble(t):
        img = base_sofa.copy()
        d2 = ImageDraw.Draw(img)
        draw_thought_bubble(d2, "AÇÕES TÊM\nCONSEQUÊNCIAS",
                            310, 272, w=305, h=98, progress=t)
        return img
    vw.animate(frame_bubble, 0.8, hold=0.25)
    base_bubble = frame_bubble(1.0)

    # Mulher no escritório
    woman = Image.new("RGBA", (W,H), (0,0,0,0))
    dw = ImageDraw.Draw(woman)
    dw.rectangle([680,378,965,415], fill=(165,108,48), outline=BLACK, width=3)
    dw.rectangle([700,415,730,535], fill=(140,90,40), outline=BLACK, width=2)
    dw.rectangle([925,415,955,535], fill=(140,90,40), outline=BLACK, width=2)
    dw.rectangle([735,232,932,380], fill=(30,30,100), outline=BLACK, width=3)
    dw.rectangle([745,242,922,372], fill=(20,20,80))
    pts_g = [(755,362),(785,312),(825,282),(865,302),(905,252),(918,272)]
    dw.line(pts_g, fill=RED, width=3)
    dw.line([(755,292),(920,292)], fill=(80,80,140), width=1)
    dw.rectangle([820,378,842,398], fill=GRAY, outline=BLACK, width=2)
    dw.rectangle([792,396,872,408], fill=GRAY, outline=BLACK, width=2)
    dw.ellipse([797,178,852,238], fill=(255,220,185), outline=BLACK, width=2)
    dw.rectangle([795,238,854,322], fill=(50,150,220), outline=BLACK, width=2)
    dw.line([795,262,752,292], fill=BLACK, width=2)
    dw.line([854,262,898,292], fill=BLACK, width=2)

    def frame_woman(t):
        return apply_slide_from_bottom(base_bubble, woman, (0,0), t)
    vw.animate(frame_woman, 1.0, hold=0.25)
    base_woman = frame_woman(1.0)

    # Texto inferior
    def frame_txt(t):
        img = base_woman.copy()
        d2 = ImageDraw.Draw(img)
        draw_on_text(d2, "VOCÊ TEM MUITOS PROBLEMAS ATÉ DESCOBRIR UM PROBLEMA DE SAÚDE. AÍ VOCÊ SÓ TEM UM PROBLEMA!",
                     (40,592), size=21, color=BLACK, bold=True, progress=t, max_chars=68)
        return img
    vw.animate(frame_txt, 2.0, hold=0.4)
    base_txt = frame_txt(1.0)

    # Lápide pop-in
    grave = Image.new("RGBA", (W,H), (0,0,0,0))
    dg = ImageDraw.Draw(grave)
    draw_gravestone(dg, 820, 515, progress=1.0)

    def frame_grave(t):
        return apply_pop_in(base_txt, grave, (820,515), t)
    vw.animate(frame_grave, 0.6, hold=0.1)
    base_grave = frame_grave(1.0)

    # Ícones acima da lápide
    icon_base = base_grave
    for name, ix, iy in [("sol",778,392),("bateria",824,392),("halter",872,392)]:
        def frame_icon(t, n_=name, _x=ix, _y=iy, _base=icon_base):
            img = _base.copy()
            d2 = ImageDraw.Draw(img)
            p_ = ease_out_back(t)
            if n_ == "sol":
                r_ = max(1,int(15*p_))
                d2.ellipse([_x-r_,_y-r_,_x+r_,_y+r_], fill=YELLOW, outline=BLACK, width=2)
                for ang in range(0,360,45):
                    rad = math.radians(ang)
                    d2.line([_x+int((r_+2)*math.cos(rad)),_y+int((r_+2)*math.sin(rad)),
                             _x+int((r_+8)*math.cos(rad)),_y+int((r_+8)*math.sin(rad))],
                            fill=YELLOW, width=2)
            elif n_ == "bateria":
                bw_,bh_ = max(1,int(25*p_)),max(1,int(14*p_))
                draw_battery(d2,_x-bw_//2,_y-bh_//2,bw_,bh_,level=1.0,color=GREEN)
            elif n_ == "halter":
                hl_ = max(1,int(26*p_))
                d2.line([_x-hl_//2,_y,_x+hl_//2,_y], fill=GRAY_DARK, width=max(1,int(4*p_)))
                for sx in [_x-hl_//2,_x+hl_//2]:
                    d2.ellipse([sx-int(7*p_),_y-int(7*p_),sx+int(7*p_),_y+int(7*p_)],
                               fill=GRAY_DARK, outline=BLACK, width=max(1,int(2*p_)))
            return img
        vw.animate(frame_icon, 0.35, hold=0.06)
        icon_base = frame_icon(1.0)

    vw.write_n(icon_base, 0.8)


def quadro_5_ambiente(vw):
    """CONTROLE O SEU AMBIENTE."""
    vw.animate(lambda t: draw_title_animated(blank_canvas(),
               "CONTROLE O SEU AMBIENTE, CONTROLE A SUA VIDA", progress=t),
               1.0, hold=0.1)
    base_t = blank_canvas()
    draw_title_animated(base_t, "CONTROLE O SEU AMBIENTE, CONTROLE A SUA VIDA", progress=1.0)

    def frame_char(t):
        img = base_t.copy()
        d2 = ImageDraw.Draw(img)
        draw_stick_figure(d2, 640, 365, scale=1.15, shirt=RED, hair=YELLOW,
                          pose="neutral", progress=t)
        return img
    vw.animate(frame_char, 1.0, hold=0.2)
    base_char = frame_char(1.0)

    def frame_brain(t):
        img = base_char.copy()
        d2 = ImageDraw.Draw(img)
        draw_brain(d2, 200, 280, r=62, progress=t)
        return img
    vw.animate(frame_brain, 1.0, hold=0.1)
    base_brain = frame_brain(1.0)

    def frame_bat(t):
        img = base_brain.copy()
        d2 = ImageDraw.Draw(img)
        lv = 0.2+0.8*ease_out_quad(t)
        draw_battery(d2, 155,355, 92,46, level=lv, color=GREEN, animated=True, t_anim=t*10)
        return img
    vw.animate(frame_bat, 1.2, hold=0.15)
    base_bat = frame_bat(1.0)

    def frame_speech(t):
        img = base_bat.copy()
        d2 = ImageDraw.Draw(img)
        draw_speech_rect(d2, "NÃO QUERO ISSO!!!",
                         400,222, w=258,h=68, progress=t)
        return img
    vw.animate(frame_speech, 0.6, hold=0.25)
    base_speech = frame_speech(1.0)

    def frame_fridge(t):
        img = base_speech.copy()
        d2 = ImageDraw.Draw(img)
        draw_fridge(d2, 945,250, 162,295, progress=t)
        return img
    vw.animate(frame_fridge, 1.2, hold=0.15)
    base_fridge = frame_fridge(1.0)

    def frame_bottle(t):
        img = base_fridge.copy()
        d2 = ImageDraw.Draw(img)
        p_ = ease_out_back(t)
        bx,by = 1100,260
        bh_ = max(1,int(170*p_))
        d2.rectangle([bx,by+170-bh_,bx+52,by+172], fill=(30,30,30), outline=BLACK, width=2)
        d2.ellipse([bx+5,by+172-bh_-20,bx+47,by+172-bh_+5], fill=(30,30,30), outline=BLACK)
        if p_ > 0.7:
            xp_ = ease_out_quad((p_-0.7)/0.3)
            xl = int(70*xp_)
            d2.line([(bx-10,by-10),(bx-10+xl,by-10+xl)], fill=RED, width=6)
            d2.line([(bx+60,by-10),(bx+60-xl,by-10+xl)], fill=RED, width=6)
        return img
    vw.animate(frame_bottle, 0.8, hold=0.1)
    base_bottle = frame_bottle(1.0)

    def frame_candy(t):
        img = base_bottle.copy()
        d2 = ImageDraw.Draw(img)
        p_ = ease_out_back(t)
        cx_,cy_ = 1100,482
        sz_ = max(1,int(30*p_))
        d2.rectangle([cx_-sz_,cy_-sz_//2,cx_+sz_,cy_+sz_//2],
                     fill=(100,55,20), outline=BLACK, width=2)
        d2.ellipse([cx_-sz_-42,cy_-sz_//2,cx_-5,cy_+sz_//2],
                   fill=ORANGE, outline=BLACK, width=2)
        if p_ > 0.6:
            xp_ = ease_out_quad((p_-0.6)/0.4)
            xl_ = int(60*xp_)
            d2.line([(cx_-58,cy_-48),(cx_-58+xl_,cy_-48+xl_)], fill=RED, width=7)
            d2.line([(cx_+48,cy_-48),(cx_+48-xl_,cy_-48+xl_)], fill=RED, width=7)
        return img
    vw.animate(frame_candy, 0.7, hold=0.1)
    base_candy = frame_candy(1.0)

    def frame_txt(t):
        img = base_candy.copy()
        d2 = ImageDraw.Draw(img)
        draw_on_text(d2, "FAÇO TUDO O QUE FOR PRECISO PARA FACILITAR OS BONS HÁBITOS E CRIO OBSTÁCULOS PARA OS MAUS HÁBITOS",
                     (50,592), size=20, color=BLACK, progress=t, max_chars=62)
        return img
    vw.animate(frame_txt, 2.5, hold=0.8)


def quadro_6_mentira(vw):
    """NÃO MINTA PARA SI MESMO."""
    vw.animate(lambda t: draw_title_animated(blank_canvas(),
               "NÃO MINTA PARA SI MESMO", progress=t), 0.8, hold=0.1)
    base_t = blank_canvas()
    draw_title_animated(base_t, "NÃO MINTA PARA SI MESMO", progress=1.0)

    meet = Image.new("RGBA", (W,H), (0,0,0,0))
    dm = ImageDraw.Draw(meet)
    dm.rectangle([122,365,562,495], fill=BROWN, outline=BLACK, width=3)
    for px,py,sc in [(202,308,ORANGE),(342,298,GREEN),(482,308,BLUE)]:
        dm.ellipse([px-20,py-20,px+20,py+20], fill=WHITE, outline=BLACK, width=2)
        dm.rectangle([px-18,py+20,px+18,py+68], fill=sc, outline=BLACK, width=2)
        dm.line([px-18,py+38,px-40,py+58], fill=BLACK, width=2)
        dm.line([px+18,py+38,px+40,py+58], fill=BLACK, width=2)

    def frame_meet(t):
        return apply_box_reveal(base_t, meet, (0,0), t, direction="left")
    vw.animate(frame_meet, 1.5, hold=0.15)
    base_meet = frame_meet(1.0)

    def frame_txt1(t):
        img = base_meet.copy()
        d2 = ImageDraw.Draw(img)
        draw_on_text(d2, "BASTA FALAR E FAZER O QUE OS OUTROS QUEREM",
                     (105,238), size=22, color=BLACK, progress=t, max_chars=44)
        return img
    vw.animate(frame_txt1, 1.0, hold=0.15)
    base_t1 = frame_txt1(1.0)

    def frame_arrow(t):
        img = base_t1.copy()
        d2 = ImageDraw.Draw(img)
        draw_arrow(d2, 612,395, 782,395, color=BLUE, width=6, progress=t)
        return img
    vw.animate(frame_arrow, 0.5, hold=0.1)
    base_arr = frame_arrow(1.0)

    def frame_hl(t):
        img = base_arr.copy()
        d2 = ImageDraw.Draw(img)
        p_ = ease_out_back(t)
        bw_ = max(1,int(402*p_)); bh_ = max(1,int(82*p_))
        d2.rounded_rectangle([800,348,800+bw_,348+bh_], radius=10,
                              fill=BLUE_LIGHT, outline=BLUE, width=3)
        if p_ > 0.6:
            fnt_ = font(max(10,int(24*p_)), bold=True)
            d2.text((1002,388), "MAS É MELHOR\nSER VOCÊ MESMO!",
                    font=fnt_, fill=BLACK, anchor="mm")
        return img
    vw.animate(frame_hl, 0.8, hold=0.35)
    base_hl = frame_hl(1.0)

    def frame_alone(t):
        img = base_hl.copy()
        d2 = ImageDraw.Draw(img)
        draw_stick_figure(d2, 922,535, scale=0.75, shirt=ORANGE,
                          hair=YELLOW, pose="shrug", progress=t)
        return img
    vw.animate(frame_alone, 0.7, hold=0.45)
    base_alone = frame_alone(1.0)

    def frame_group(t):
        img = base_alone.copy()
        d2 = ImageDraw.Draw(img)
        shirts = [ORANGE,BLUE,GREEN,RED,YELLOW]
        offs = [(-45,0),(0,0),(45,0),(-22,35),(22,35)]
        for i,(ox,oy) in enumerate(offs):
            draw_stick_figure(d2, 952+ox,525+oy, scale=0.62,
                              shirt=shirts[i], hair=YELLOW, progress=t)
        return img
    vw.animate(frame_group, 0.8, hold=0.15)
    base_group = frame_group(1.0)

    def frame_txt2(t):
        img = base_group.copy()
        d2 = ImageDraw.Draw(img)
        draw_on_text(d2, "ATRAI PESSOAS QUE GOSTAM DE VOCÊ PELO QUE VOCÊ É DE VERDADE",
                     (820,618), size=20, color=BLACK, progress=t, max_chars=46)
        return img
    vw.animate(frame_txt2, 1.5, hold=0.8)


def quadro_7_leitura(vw):
    """LEIA SEMPRE."""
    vw.animate(lambda t: draw_title_animated(blank_canvas(), "LEIA SEMPRE", progress=t),
               0.7, hold=0.1)
    base_t = blank_canvas()
    draw_title_animated(base_t, "LEIA SEMPRE", progress=1.0)

    def frame_head(t):
        img = base_t.copy()
        d2 = ImageDraw.Draw(img)
        p_ = ease_out_quad(t)
        r_ = max(1,int(90*p_))
        cx,cy = 640,342
        d2.ellipse([cx-r_,cy-r_,cx+r_,cy+r_], fill=WHITE,
                   outline=BLUE, width=max(1,int(4*p_)))
        if p_ > 0.4:
            draw_brain(d2, cx,cy, r=int(55*p_), progress=(p_-0.4)/0.6)
        return img
    vw.animate(frame_head, 1.2, hold=0.1)
    base_head = frame_head(1.0)

    def frame_books(t):
        img = base_head.copy()
        d2 = ImageDraw.Draw(img)
        draw_book_stack(d2, 578,595, n=5, progress=t)
        return img
    vw.animate(frame_books, 1.0, hold=0.15)
    base_books = frame_books(1.0)

    def frame_left(t):
        img = base_books.copy()
        d2 = ImageDraw.Draw(img)
        draw_on_text(d2, "A CADA PÁGINA LIDA, VOCÊ ESTÁ BAIXANDO A SABEDORIA DE UMA VIDA INTEIRA DE OUTRA PESSOA",
                     (52,268), size=20, color=BLACK, progress=t, max_chars=26)
        return img
    vw.animate(frame_left, 1.5, hold=0.1)
    base_left = frame_left(1.0)

    climber = Image.new("RGBA", (W,H), (0,0,0,0))
    dc = ImageDraw.Draw(climber)
    draw_stick_figure(dc, 698,425, scale=0.55, shirt=BLUE,
                      hair=YELLOW, pose="arms_up", progress=1.0)

    def frame_climber(t):
        return apply_slide_from_bottom(base_left, climber, (0,0), t)
    vw.animate(frame_climber, 0.7, hold=0.15)
    base_climber = frame_climber(1.0)

    def frame_right(t):
        img = base_climber.copy()
        d2 = ImageDraw.Draw(img)
        draw_on_text(d2, "CADA LIVRO É UM CÉREBRO INTEIRO TE ENSINANDO O QUE LEVOU DÉCADAS PRA APRENDER",
                     (842,268), size=20, color=BLACK, progress=t, max_chars=26)
        return img
    vw.animate(frame_right, 1.5, hold=0.15)
    base_right = frame_right(1.0)

    def frame_crowd(t):
        img = base_right.copy()
        d2 = ImageDraw.Draw(img)
        p_ = ease_in_out_cubic(t)
        n_ = max(1,int(14*p_))
        for i in range(n_):
            hx_ = 185+i*68
            hr_ = int(20*(1-abs(i-7)/10))
            d2.ellipse([hx_-hr_,642,hx_+hr_,682], fill=WHITE, outline=BLACK, width=2)
        return img
    vw.animate(frame_crowd, 0.8, hold=0.8)


def quadro_8_energia(vw):
    """GERENCIE SUA ENERGIA."""
    vw.animate(lambda t: draw_title_animated(blank_canvas(),
               "GERENCIE SUA ENERGIA, NÃO O SEU TEMPO", progress=t),
               0.9, hold=0.1)
    base_t = blank_canvas()
    draw_title_animated(base_t, "GERENCIE SUA ENERGIA, NÃO O SEU TEMPO", progress=1.0)

    def frame_bat_full(t):
        img = base_t.copy()
        d2 = ImageDraw.Draw(img)
        p_ = ease_out_quad(t)
        draw_battery(d2, 82,205, 100,202, level=1.0, color=GREEN)
        d2.rectangle([58,78,208,198], fill=(202,242,255), outline=BLACK, width=max(1,int(3*p_)))
        if p_ > 0.5:
            d2.ellipse([108,102,158,152], fill=YELLOW)
            for ang in range(0,360,45):
                rad = math.radians(ang)
                d2.line([133+int(32*math.cos(rad)),127+int(32*math.sin(rad)),
                         133+int(42*math.cos(rad)),127+int(42*math.sin(rad))],
                        fill=YELLOW, width=2)
            d2.ellipse([58,162,118,192], fill=WHITE, outline=(200,200,200))
            d2.ellipse([88,158,148,195], fill=WHITE, outline=(200,200,200))
        return img
    vw.animate(frame_bat_full, 1.2, hold=0.15)
    base_bfull = frame_bat_full(1.0)

    def frame_bat_half(t):
        img = base_bfull.copy()
        d2 = ImageDraw.Draw(img)
        p_ = ease_out_quad(t)
        draw_battery(d2, 352,205, 100,202, level=0.4, color=GREEN)
        d2.rectangle([328,78,478,198], fill=(162,168,188), outline=BLACK, width=max(1,int(3*p_)))
        if p_ > 0.5:
            d2.ellipse([332,142,402,188], fill=(132,138,158))
            d2.ellipse([372,132,452,188], fill=(122,128,148))
            for rx_ in range(338,472,18):
                d2.line([(rx_,178),(rx_-5,196)], fill=BLUE, width=2)
            d2.ellipse([342,88,382,132], fill=WHITE)
            d2.ellipse([358,88,398,132], fill=(162,168,188))
        return img
    vw.animate(frame_bat_half, 1.2, hold=0.15)
    base_bhalf = frame_bat_half(1.0)

    # Relógio pop-in
    clk = Image.new("RGBA", (W,H), (0,0,0,0))
    dclk = ImageDraw.Draw(clk)
    draw_alarm_clock(dclk, 1102,342, r=82, progress=1.0)

    def frame_clock(t):
        return apply_pop_in(base_bhalf, clk, (1102,342), t)
    vw.animate(frame_clock, 0.7, hold=0.15)
    base_clk = frame_clock(1.0)

    def frame_texts(t):
        img = base_clk.copy()
        d2 = ImageDraw.Draw(img)
        p1 = min(1.0, t*2.2)
        p2 = max(0.0,(t-0.45)*2.2)
        draw_on_text(d2, "MAIS EFICIÊNCIA\nMENOS ESFORÇO",
                     (58,422), size=22, bold=True, color=BLACK, progress=p1)
        if p2 > 0:
            draw_on_text(d2, "PRODUZ MAIS\nEM MENOS TEMPO",
                         (328,422), size=22, bold=True, color=BLACK, progress=p2)
        return img
    vw.animate(frame_texts, 2.0, hold=0.15)
    base_texts = frame_texts(1.0)

    # Círculo verde (destaque bateria cheia)
    def frame_circle(t):
        img = base_texts.copy()
        d2 = ImageDraw.Draw(img)
        draw_imperfect_circle(d2, 132,288, 112, GREEN_V, width=6, progress=t)
        return img
    vw.animate(frame_circle, 0.7, hold=0.08)
    base_circ = frame_circle(1.0)

    def frame_work(t):
        img = base_circ.copy()
        d2 = ImageDraw.Draw(img)
        draw_on_text(d2, "TRABALHAR NO MOMENTO CERTO",
                     (32,512), size=20, bold=True, color=GREEN, progress=t)
        return img
    vw.animate(frame_work, 0.8, hold=0.08)
    base_work = frame_work(1.0)

    # Energizado (slide left)
    energy_hi = Image.new("RGBA", (W,H), (0,0,0,0))
    dhi = ImageDraw.Draw(energy_hi)
    draw_stick_figure(dhi, 202,582, scale=0.9, shirt=BLUE, hair=YELLOW,
                      pose="pointing", progress=1.0)

    def frame_hi(t):
        return apply_slide_from_left(base_work, energy_hi, (0,0), t)
    vw.animate(frame_hi, 0.7, hold=0.08)
    base_hi = frame_hi(1.0)

    # Exausto (draw-on)
    def frame_lo(t):
        img = base_hi.copy()
        d2 = ImageDraw.Draw(img)
        p_ = ease_out_quad(t)
        cx,cy = 1060,582
        d2.ellipse([cx-20,cy-int(100*p_),cx+20,cy-int(60*p_)],
                   fill=WHITE, outline=BLACK, width=2)
        d2.rectangle([cx-18,cy-int(60*p_),cx+18,cy+int(18*p_)],
                     fill=(150,150,150), outline=BLACK, width=2)
        if p_ > 0.5:
            d2.line([cx-18,cy-int(28*p_),cx-int(50*p_),cy+int(12*p_)],
                    fill=BLACK, width=3)
            d2.line([cx+18,cy-int(28*p_),cx+int(50*p_),cy+int(12*p_)],
                    fill=BLACK, width=3)
        if p_ > 0.7:
            d2.ellipse([cx-12,cy-int(82*p_),cx-4,cy-int(74*p_)], fill=(200,150,150))
            d2.ellipse([cx+4,cy-int(82*p_),cx+12,cy-int(74*p_)], fill=(200,150,150))
        if p_ > 0.82:
            d2.line([cx-8,cy+int(18*p_),cx-16,cy+int(70*p_)], fill=BLACK, width=3)
            d2.line([cx+8,cy+int(18*p_),cx+16,cy+int(70*p_)], fill=BLACK, width=3)
        return img
    vw.animate(frame_lo, 0.8, hold=0.9)


def quadro_9_bom_dia(vw):
    """TENHA UM BOM DIA, E VOCÊ TERÁ UMA BOA VIDA."""
    vw.animate(lambda t: draw_title_animated(blank_canvas(),
               "TENHA UM BOM DIA, E VOCÊ TERÁ UMA BOA VIDA", progress=t),
               0.9, hold=0.1)
    base_t = blank_canvas()
    draw_title_animated(base_t, "TENHA UM BOM DIA, E VOCÊ TERÁ UMA BOA VIDA", progress=1.0)

    GX,GY = 252,80; SQ,GAP = 11,1; COLS,ROWS = 52,30

    def frame_grid(t):
        img = base_t.copy()
        d2 = ImageDraw.Draw(img)
        p_ = ease_in_out_cubic(t)
        total = COLS*ROWS
        n_fill = int(total*p_)
        for r_ in range(ROWS):
            for c_ in range(COLS):
                if r_*COLS+c_ >= n_fill: break
                x_ = GX+c_*(SQ+GAP); y_ = GY+r_*(SQ+GAP)
                d2.rectangle([x_,y_,x_+SQ,y_+SQ], outline=(190,190,190), width=1)
        d2.text((GX+COLS*(SQ+GAP)//2, 68), "SEMANA DO ANO →",
                font=font(14,bold=True), fill=BLUE, anchor="mm")
        for yr in [0,10,20,29]:
            d2.text((GX-35, GY+yr*(SQ+GAP)+5), str(yr*2), font=font(11), fill=GRAY_DARK)
        return img
    vw.animate(frame_grid, 1.5, hold=0.08)
    base_grid = frame_grid(1.0)

    def frame_emojis(t):
        img = base_grid.copy()
        d2 = ImageDraw.Draw(img)
        p_ = ease_in_out_cubic(t)
        n_fill = int(COLS*2*p_)
        for idx in range(n_fill):
            r_ = idx//COLS; c_ = idx%COLS
            x_ = GX+c_*(SQ+GAP); y_ = GY+r_*(SQ+GAP)
            d2.ellipse([x_,y_,x_+SQ,y_+SQ], fill=YELLOW, outline=BLACK, width=1)
            d2.ellipse([x_+2,y_+2,x_+4,y_+4], fill=BLACK)
            d2.ellipse([x_+7,y_+2,x_+9,y_+4], fill=BLACK)
            d2.arc([x_+2,y_+5,x_+9,y_+9], 0,180, fill=BLACK, width=1)
        return img
    vw.animate(frame_emojis, 1.2, hold=0.15)
    base_em = frame_emojis(1.0)

    # Emoji gigante pop-in
    emoji_big = Image.new("RGBA", (W,H), (0,0,0,0))
    deb = ImageDraw.Draw(emoji_big)
    draw_smiley(deb, 942,382, r=122, progress=1.0)

    def frame_ebig(t):
        return apply_pop_in(base_em, emoji_big, (942,382), t)
    vw.animate(frame_ebig, 0.8, hold=0.25)
    base_ebig = frame_ebig(1.0)

    # Homem cinza
    def frame_gray(t):
        img = base_ebig.copy()
        d2 = ImageDraw.Draw(img)
        p_ = ease_out_quad(t)
        gs = int(155*p_)
        draw_stick_figure(d2, 102,562, scale=0.75, shirt=(gs,gs,gs),
                          hair=(gs,gs,gs), progress=t)
        if p_ > 0.82:
            d2.text((58,668), "50 SEMANAS", font=font(16,bold=True), fill=GRAY_DARK)
        return img
    vw.animate(frame_gray, 0.8, hold=0.18)
    base_gray = frame_gray(1.0)

    # Homem eufórico
    def frame_happy(t):
        img = base_gray.copy()
        d2 = ImageDraw.Draw(img)
        draw_stick_figure(d2, 222,558, scale=0.8, shirt=ORANGE,
                          hair=YELLOW, pose="arms_up", progress=t)
        if t > 0.82:
            d2.text((222,662), "2 SEMANAS!", font=font(16,bold=True),
                    fill=BLACK, anchor="mm")
        return img
    vw.animate(frame_happy, 0.7, hold=0.18)
    base_happy = frame_happy(1.0)

    def frame_sat(t):
        img = base_happy.copy()
        d2 = ImageDraw.Draw(img)
        draw_on_text(d2, "ENCONTRE SATISFAÇÃO NO SIMPLES",
                     (1022,322), size=22, bold=True, color=BLACK, progress=t, max_chars=22)
        return img
    vw.animate(frame_sat, 1.0, hold=0.18)
    base_sat = frame_sat(1.0)

    # Trabalhador feliz
    def frame_worker(t):
        img = base_sat.copy()
        d2 = ImageDraw.Draw(img)
        p_ = ease_out_back(t)
        x_off = int(40*(1-p_))
        d2.rectangle([1002+x_off,492,1232,622], fill=(30,30,100), outline=BLACK, width=2)
        d2.rectangle([1012+x_off,502,1222,612], fill=(20,20,80))
        pts_w = [(1015+x_off,602),(1045+x_off,572),(1082+x_off,555),
                 (1115+x_off,572),(1145+x_off,545),(1160+x_off,565)]
        d2.line(pts_w, fill=GREEN, width=3)
        draw_stick_figure(d2, 1102,485, scale=0.72, shirt=(80,102,182),
                          hair=YELLOW, pose="neutral", progress=t)
        return img
    vw.animate(frame_worker, 0.8, hold=0.8)


def quadro_10_final(vw):
    """Zoom-out do painel + Logo animado."""
    # Visão geral mini
    overview = blank_canvas()
    d = ImageDraw.Draw(overview)
    px,py,pw,ph = 222,52,842,605
    d.rounded_rectangle([px,py,px+pw,py+ph], radius=12, outline=BLUE, width=4)
    d.text((px+pw//2, py+28), "EXPERIÊNCIA, REFLEXÃO E CONSELHOS",
           font=font(22,bold=True), fill=BLUE, anchor="mm")
    labels = ["1 SAÚDE","2 AMBIENTE","3 SER VOCÊ","4 LEITURA","5 ENERGIA","6 BOM DIA"]
    mini_colors = [RED,GREEN,ORANGE,BLUE,GREEN,YELLOW]
    for i,(lbl,mc) in enumerate(zip(labels,mini_colors)):
        c_,r_ = i%2, i//2
        sw_ = (pw-50)//2; sh_ = (ph-90)//3
        rx_ = px+20+c_*(sw_+10); ry_ = py+55+r_*(sh_+10)
        d.rounded_rectangle([rx_,ry_,rx_+sw_-10,ry_+sh_-10],
                             radius=6, outline=BLACK, width=2, fill=(250,250,250))
        d.text((rx_+12,ry_+12), lbl, font=font(18,bold=True), fill=mc)
    draw_stick_figure(d, 122,362, scale=1.05, shirt=RED, hair=YELLOW,
                      pose="pointing", progress=1.0)

    def frame_ov(t):
        p_ = ease_in_out_cubic(t)
        return Image.blend(blank_canvas(), overview, p_)
    vw.animate(frame_ov, 1.5, hold=1.5)

    def frame_fade(t):
        return Image.blend(overview, blank_canvas(), ease_in_out_cubic(t))
    vw.animate(frame_fade, 1.0, hold=0.08)

    # LOGO animado
    logo_base = blank_canvas()
    dl = ImageDraw.Draw(logo_base)
    bx, by = 362, 362
    dl.ellipse([bx-78,by-115,bx+78,by+58], fill=WHITE, outline=BLACK, width=4)
    dl.rectangle([bx-30,by+58,bx+30,by+105], fill=(200,200,200), outline=BLACK, width=3)
    dl.line([bx-22,by+105,bx+22,by+105], fill=BLACK, width=3)
    dl.line([bx-16,by+115,bx+16,by+115], fill=BLACK, width=2)
    draw_brain(dl, bx,by-22, r=64, progress=1.0)

    def frame_logo(t):
        img = logo_base.copy()
        d2 = ImageDraw.Draw(img)
        p_ = ease_out_back(t, s=1.3)
        # Raios de luz
        if p_ > 0.1:
            for ang in range(0,360,45):
                rad = math.radians(ang)
                r1 = 92; r2 = int(92+32*p_)
                d2.line([bx+int(r1*math.cos(rad)),by-22+int(r1*math.sin(rad)),
                         bx+int(r2*math.cos(rad)),by-22+int(r2*math.sin(rad))],
                        fill=YELLOW, width=max(1,int(3*p_)))
        # Texto logo
        txt_full = "SejaUmaPessoaMelhor"
        n_ = max(0, int(len(txt_full)*ease_in_out_cubic(t)))
        visible = txt_full[:n_]
        d2.text((bx+115, by-38), visible, font=font(44,bold=True), fill=BLACK)
        # Subtexto
        if t > 0.7:
            tp = (t-0.7)/0.3
            d2.text((bx+115, by+22), "seja uma pessoa melhor",
                    font=font(22,False), fill=GRAY_DARK)
        return img

    vw.animate(frame_logo, 2.2, hold=2.8)


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════

def main():
    out_path = os.path.join(OUT, "video_sejaumapessoamelhor.mp4")
    vw = VideoWriter(out_path)

    print("🎬 VERSÃO TURBINADA — SejaUmaPessoaMelhor")
    print("   Easing: cubic/back/bounce/elastic | Reveals: wipe/radial/pop/slide")
    t0 = time.time()

    steps = [
        ("Intro — personagem draw-on",        quadro_1_intro),
        ("Painel + borda animada",             quadro_2_panel),
        ("Números pop-in elástico",            None),
        ("SAÚDE NÃO É UM LUXO",               quadro_4_saude),
        ("CONTROLE SEU AMBIENTE",              quadro_5_ambiente),
        ("NÃO MINTA PARA SI MESMO",            quadro_6_mentira),
        ("LEIA SEMPRE",                        quadro_7_leitura),
        ("GERENCIE SUA ENERGIA",               quadro_8_energia),
        ("TENHA UM BOM DIA",                   quadro_9_bom_dia),
        ("Logo final animado",                 quadro_10_final),
    ]

    print(f"\n  [1/10] {steps[0][0]}...")
    quadro_1_intro(vw)

    print(f"  [2/10] {steps[1][0]}...")
    rects, base_panel = quadro_2_panel(vw)

    print(f"  [3/10] {steps[2][0]}...")
    quadro_3_numbers(vw, rects, base_panel)

    for i, (name, fn) in enumerate(steps[3:], 4):
        print(f"  [{i}/10] {name}...")
        fn(vw)

    vw.release()
    elapsed = time.time() - t0
    size_mb = os.path.getsize(out_path) / (1024*1024)
    print(f"\n✅  Vídeo salvo: {out_path}")
    print(f"    Frames: {vw.frame_count}  |  Duração: ~{vw.frame_count/FPS:.0f}s  |  Tempo de render: {elapsed:.1f}s  |  Tamanho: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
