"""Motor de reels explicativos 9:16 (pycairo + ffmpeg). No editar por video: importar desde video_<slug>.py."""
import cairo, math, os, re, sys, random, subprocess
from multiprocessing import Pool

W, H, FPS = 1080, 1920, 30
FONT = "Poppins" if "Poppins" in subprocess.run(["fc-list"], capture_output=True, text=True).stdout else "DejaVu Sans"
YELLOW = (1.0, 0.82, 0.12)
GREEN, RED, BLUE = (0.2, 0.8, 0.4), (0.9, 0.25, 0.25), (0.25, 0.55, 1.0)
TINTS = {"neutro": (0.12, 0.16, 0.32), "bueno": (0.08, 0.2, 0.18), "malo": (0.25, 0.08, 0.1),
         "info": (0.06, 0.14, 0.3), "cierre": (0.18, 0.12, 0.3)}

# ---------- tiempo ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in_out(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def ease_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def prog(t, start, dur): return clamp((t - start) / dur)
def pop(t, start, dur=0.35):
    """Escala segura para aparecer con rebote (nunca 0)."""
    return max(0.02, ease_back(prog(t, start, dur)))
def slide_in(t, start=0, dur=0.5, dist=300):
    """Offset vertical para que algo entre desde abajo."""
    return (1 - ease_out(prog(t, start, dur))) * dist

# ---------- fondo y luz ----------
def background(ctx, t, tint="neutro"):
    tint = TINTS.get(tint, tint)
    g = cairo.RadialGradient(W / 2, H * 0.52, 80, W / 2, H * 0.52, H * 0.75)
    g.add_color_stop_rgb(0, *tint); g.add_color_stop_rgb(1, 0.025, 0.03, 0.07)
    ctx.set_source(g); ctx.paint()
    rnd = random.Random(7)
    for i in range(40):
        x = rnd.uniform(0, W); y = (rnd.uniform(0, H) - t * rnd.uniform(8, 25)) % H
        ctx.new_path(); ctx.set_source_rgba(1, 1, 1, 0.06 + 0.06 * math.sin(t * 2 + i))
        ctx.arc(x, y, rnd.uniform(1.5, 4), 0, 2 * math.pi); ctx.fill()

def floor_shadow(ctx, cx, y, w, alpha=0.45):
    ctx.save(); ctx.translate(cx, y); ctx.scale(1, 0.18)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, w)
    g.add_color_stop_rgba(0, 0, 0, 0, alpha); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(g); ctx.new_path(); ctx.arc(0, 0, w, 0, 2 * math.pi); ctx.fill(); ctx.restore()

def glow(ctx, cx, cy, r, color=(1, 0.85, 0.3), a=0.35):
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, r)
    g.add_color_stop_rgba(0, *color, a); g.add_color_stop_rgba(1, *color, 0)
    ctx.set_source(g); ctx.new_path(); ctx.arc(cx, cy, r, 0, 2 * math.pi); ctx.fill()

def hgrad(x0, x1, dark, light):
    """Degradé horizontal oscuro-claro-oscuro: da volumen a cilindros/objetos."""
    g = cairo.LinearGradient(x0, 0, x1, 0)
    g.add_color_stop_rgb(0, *dark); g.add_color_stop_rgb(0.42, *light); g.add_color_stop_rgb(1, *dark)
    return g

def shine(ctx, x, top, w, h, a=0.5):
    """Reflejo blanco vertical (usar dentro de un clip del objeto)."""
    g = cairo.LinearGradient(x, 0, x + w, 0)
    g.add_color_stop_rgba(0, 1, 1, 1, 0); g.add_color_stop_rgba(0.5, 1, 1, 1, a); g.add_color_stop_rgba(1, 1, 1, 1, 0)
    ctx.set_source(g); ctx.rectangle(x, top, w, h); ctx.fill()

# ---------- formas ----------
def rrect(ctx, x, y, w, h, r):
    r = max(0.5, min(r, w / 2, h / 2)); ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()

def catmull(points, n=8):
    out = []; pts = [points[0]] + points + [points[-1]]
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n):
            u = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u * u
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u ** 3) for j in range(2)))
    out.append(points[-1]); return out

def profile_path(ctx, cx, by, s, prof):
    """Silueta simétrica (botellas, vasos, frascos). prof=[(altura, medio_ancho)] de la base hacia arriba."""
    right = catmull([(cx + hw * s, by - y * s) for y, hw in prof])
    left = [(2 * cx - x, y) for x, y in reversed(right)]
    ctx.new_path(); ctx.move_to(*right[0])
    for p in right[1:] + left: ctx.line_to(*p)
    ctx.close_path()

def arrow(ctx, x1, y1, x2, y2, alpha=1.0, color=YELLOW, w=6):
    if alpha <= 0: return
    ctx.set_source_rgba(*color, alpha); ctx.set_line_width(w); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.new_path(); ctx.move_to(x1, y1); ctx.line_to(x2, y2); ctx.stroke()
    a = math.atan2(y2 - y1, x2 - x1); L = 26
    ctx.move_to(x2, y2); ctx.line_to(x2 - L * math.cos(a - .45), y2 - L * math.sin(a - .45))
    ctx.line_to(x2 - L * math.cos(a + .45), y2 - L * math.sin(a + .45)); ctx.close_path(); ctx.fill()

def badge(ctx, x, y, r, p, ok=True):
    """Tilde verde (ok=True) o cruz roja. p = progreso 0..1 de aparición."""
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); s = max(0.02, ease_back(p)); ctx.scale(s, s)
    ctx.set_source_rgb(*(GREEN if ok else RED)); ctx.new_path(); ctx.arc(0, 0, r, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(r * .22); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if ok: ctx.move_to(-r * .45, 0); ctx.line_to(-r * .1, r * .38); ctx.line_to(r * .5, -r * .38)
    else:
        ctx.move_to(-r * .38, -r * .38); ctx.line_to(r * .38, r * .38)
        ctx.move_to(r * .38, -r * .38); ctx.line_to(-r * .38, r * .38)
    ctx.stroke(); ctx.restore()

def gauge(ctx, value, name="GAS", y=1770, alpha=1.0):
    """Barra de nivel abajo (value 0..1, pasa de verde a rojo)."""
    x0, bw, bh = 180, 800, 34
    label(ctx, name, 110, y + 17, 34, alpha=alpha, bg=(0, 0, 0, 0))
    ctx.set_source_rgba(1, 1, 1, 0.15 * alpha); rrect(ctx, x0, y, bw, bh, 17); ctx.fill()
    v = clamp(value)
    ctx.set_source_rgba(0.3 + 0.6 * (1 - v), 0.2 + 0.6 * v, 0.4 * v, alpha); rrect(ctx, x0, y, max(bw * v, 34), bh, 17); ctx.fill()

def particles(ctx, t, n, box, seed=1, colors=None, r=9, speed=50, clip=None):
    """Partículas que rebotan dentro de box=(x0,y0,x1,y1). clip: función que define el path de recorte."""
    colors = colors or [(1, .55, .2), (1, .85, .2), (.95, .35, .6), (.4, .9, .5)]
    x0, y0, x1, y1 = box; rnd = random.Random(seed); ctx.save()
    if clip: clip(); ctx.clip()
    for i in range(n):
        w, h = x1 - x0, y1 - y0
        x = rnd.uniform(0, w) + rnd.uniform(-speed, speed) * t; y = rnd.uniform(0, h) + rnd.uniform(-speed, speed) * t
        x = w - abs(x % (2 * w) - w); y = h - abs(y % (2 * h) - h)
        ctx.set_source_rgba(*colors[i % len(colors)], .9); ctx.new_path(); ctx.arc(x0 + x, y0 + y, r, 0, 2 * math.pi); ctx.fill()
    ctx.restore()

def bubbles(ctx, t, cx, bottom, height, half_w, n=24, seed=1, alpha=0.75, clip=None):
    """Burbujas que suben (gaseosa, agua hirviendo, aire)."""
    rnd = random.Random(seed); ctx.save()
    if clip: clip(); ctx.clip()
    ctx.set_line_width(2)
    for i in range(n):
        x0 = rnd.uniform(-half_w, half_w); sp = rnd.uniform(60, 140); ph = rnd.uniform(0, 10); r = rnd.uniform(3, 8)
        y = ((t + ph) * sp) % height
        ctx.set_source_rgba(1, 1, 1, alpha * (0.4 + 0.6 * y / height)); ctx.new_path()
        ctx.arc(cx + x0 + 6 * math.sin(t * 3 + i), bottom - y - 10, r, 0, 2 * math.pi); ctx.stroke()
    ctx.restore()

def podium(ctx, t, items, base=1700):
    """Ranking. items=[(x, alto, '1', draw_obj(ctx,x,y_top,t), delay)]. draw_obj dibuja el objeto parado en (x, y_top)."""
    cols = {"1": (1, .8, .2), "2": (.8, .82, .88), "3": (.85, .55, .3)}
    for x, hgt, num, draw_obj, d in items:
        hh = max(1, hgt * ease_out(prog(t, d, .6)))
        col = cols.get(num, (.6, .6, .7)); g = cairo.LinearGradient(0, base - hh, 0, base)
        g.add_color_stop_rgb(0, *col); g.add_color_stop_rgb(1, *(c * .5 for c in col))
        ctx.set_source(g); rrect(ctx, x - 150, base - hh, 300, hh + 40, 18); ctx.fill()
        if hh > 130:
            font(ctx, 110); ctx.set_source_rgba(.1, .08, .05, .8)
            e = ctx.text_extents(num); ctx.move_to(x - e.x_advance / 2, base - hh + 130); ctx.show_text(num); ctx.new_path()
        s = pop(t, d + .4, .5)
        if s > .03:
            ctx.save(); ctx.translate(x, base - hh); ctx.scale(s, s); draw_obj(ctx, 0, 0, t); ctx.restore()

# ---------- texto ----------
def font(ctx, size, bold=True):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)

def draw_line(ctx, text, cx, cy, size=88, alpha=1.0, scale=1.0):
    """Línea centrada; [palabra] = resaltada en caja amarilla."""
    words = [(m.group(1), True) if m.group(1) else (m.group(2), False) for m in re.finditer(r"\[([^\]]+)\]|(\S+)", text)]
    font(ctx, size); space = ctx.text_extents(" ").x_advance * 1.1; pad = size * .16
    widths = [ctx.text_extents(w).x_advance + (2 * pad if hl else 0) for w, hl in words]
    total = sum(widths) + space * (len(words) - 1)
    fit = min(1.0, 980 / total) if total else 1
    ctx.save(); ctx.translate(cx, cy); s = max(0.02, scale * fit); ctx.scale(s, s)
    x = -total / 2; asc = size * .72
    for (w, hl), ww in zip(words, widths):
        ctx.new_path()
        if hl:
            ctx.set_source_rgba(*YELLOW, alpha); rrect(ctx, x, -asc - pad * .9, ww, asc + size * .28 + pad * 1.6, size * .16); ctx.fill()
            ctx.set_source_rgba(.07, .07, .1, alpha); ctx.move_to(x + pad, 0); ctx.show_text(w)
        else:
            ctx.set_source_rgba(0, 0, 0, .55 * alpha); ctx.move_to(x + 4, 5); ctx.show_text(w)
            ctx.set_source_rgba(1, 1, 1, alpha); ctx.move_to(x, 0); ctx.show_text(w)
        x += ww + space
    ctx.new_path(); ctx.restore()

def captions(ctx, t, chunks, y=330, size=88):
    """Subtítulos: chunks=[(inicio, fin, 'texto con [clave]')] en segundos locales de la escena."""
    for s, e, txt in chunks:
        if s <= t < e:
            p = prog(t, s, .18); out = prog(t, e - .08, .08)
            draw_line(ctx, txt, W / 2, y, size, alpha=p * (1 - out), scale=.82 + .18 * ease_back(p))

def hook_title(ctx, t, lines):
    """Gancho apilado. lines=[('texto', tamaño)], ej. [('¿Por qué la gaseosa',84),('en [VIDRIO]',120),('sabe mejor?',84)]."""
    y = 300
    for i, (txt, size) in enumerate(lines):
        d = i * .25
        draw_line(ctx, txt, W / 2, y, size, alpha=prog(t, d, .2), scale=.75 + .25 * ease_back(prog(t, d, .35)))
        y += size * 1.6

def label(ctx, text, x, y, size=46, alpha=1.0, color=(1, 1, 1), bg=(0, 0, 0, .55)):
    """Etiqueta tipo píldora. Fondos útiles: (0.1,0.5,0.25,0.85) verde, (0.6,0.1,0.1,0.85) rojo."""
    if alpha <= 0: return
    font(ctx, size); e = ctx.text_extents(text); w = e.x_advance + 44; h = size * 1.45
    ctx.set_source_rgba(bg[0], bg[1], bg[2], bg[3] * alpha); rrect(ctx, x - w / 2, y - h / 2, w, h, h / 2); ctx.fill()
    ctx.set_source_rgba(*color, alpha); ctx.move_to(x - e.x_advance / 2, y + size * .36); ctx.show_text(text); ctx.new_path()

# ---------- render ----------
def _frame(draw, t, dur):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    ctx.set_source_rgb(0, 0, 0); ctx.paint(); draw(ctx, t, dur); surf.flush(); return surf

def _render(args):
    draw, dur, path = args; n = round(dur * FPS); tmp = path[:-4] + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "19", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(bytes(_frame(draw, i / FPS, dur).get_data()))
    p.stdin.close()
    if p.wait() != 0: raise RuntimeError("ffmpeg falló: " + path)
    os.replace(tmp, path); return path

def write_guion(slug, title, scenes, folder):
    """guion.txt: tabla con tiempos + texto corrido para la app de voz."""
    lines = [f"GUION – {title}", ""]; t0 = 0.0; voz = []
    for sc in scenes:
        t1 = t0 + sc["dur"]
        lines.append(f"[{int(t0//60)}:{int(t0%60):02d}–{int(t1//60)}:{int(t1%60):02d}] {sc['voz']}")
        voz.append(sc["voz"]); t0 = t1
    lines += ["", "TEXTO PARA LA VOZ EN OFF (copiar y pegar):", "", " ".join(voz), "",
              f"Duración: {t0:.0f} s · palabras: {len(' '.join(voz).split())}"]
    txt = "\n".join(lines); open(f"{folder}/{slug}_guion.txt", "w").write(txt); return txt

def make_video(slug, title, scenes):
    """scenes=[{'name','draw','dur','voz','check'}]. CLI: python video_x.py stills | render"""
    folder = f"salida/{slug}"; os.makedirs(folder + "/tmp", exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "render"
    if mode == "stills":
        from PIL import Image
        thumbs = []
        for sc in scenes:
            f = f"{folder}/tmp/{sc['name']}.png"; _frame(sc["draw"], sc.get("check", sc["dur"] * .7), sc["dur"]).write_to_png(f)
            thumbs.append(Image.open(f).convert("RGB").resize((270, 480)))
        cols = 4; sheet = Image.new("RGB", (270 * cols, 480 * ((len(thumbs) + cols - 1) // cols)), "white")
        for i, im in enumerate(thumbs): sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
        sheet.save(f"{folder}/tmp/hoja.png"); print(f"{folder}/tmp/hoja.png"); return
    jobs = [(sc["draw"], sc["dur"], f"{folder}/tmp/{sc['name']}.mp4") for sc in scenes]
    with Pool(os.cpu_count() or 2) as p: p.map(_render, jobs)
    with open(f"{folder}/tmp/list.txt", "w") as f:
        for sc in scenes: f.write(f"file '{sc['name']}.mp4'\n")
    out = f"{folder}/{slug}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{folder}/tmp/list.txt",
                    "-c", "copy", "-movflags", "+faststart", out], check=True)
    print(out); print(write_guion(slug, title, scenes, folder))
