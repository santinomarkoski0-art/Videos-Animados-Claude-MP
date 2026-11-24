from motor import *
from functools import partial

PINK, CYAN = (1, .3, .75), (.3, .9, 1)
OK_BG, BAD_BG, INFO_BG = (.1, .5, .25, .85), (.6, .1, .1, .85), (.35, .1, .55, .85)
OVER = {"malo": (.6, 0, .05, .22), "bueno": (0, .4, .2, .18), "info": (0, .15, .5, .2), "cierre": (.3, 0, .4, .15)}

# ---------- fondo estilo Miami retro ----------
def palm(ctx, x, base, h, lean, t, side=1):
    sway = .04 * math.sin(t * 1.3 + x)
    top = (x + lean * h * .35 + sway * 200, base - h)
    pts = catmull([(x, base), (x + lean * h * .1, base - h * .5), top], 8)
    ctx.set_source_rgb(.09, .02, .12); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(len(pts) - 1):
        ctx.set_line_width(34 - 16 * i / len(pts)); ctx.new_path(); ctx.move_to(*pts[i]); ctx.line_to(*pts[i + 1]); ctx.stroke()
    cx, cy = top
    for k in range(8):
        a = -math.pi / 2 + (k - 3.5) * .42 + sway * 2; L = 230 + 30 * (k % 2)
        tx, ty = cx + math.cos(a) * L, cy + math.sin(a) * L * .55 + 90
        mx, my = cx + math.cos(a) * L * .5, cy + math.sin(a) * L * .5 - 30
        nx, ny = -math.sin(a) * 26, math.cos(a) * 26
        ctx.new_path(); ctx.move_to(cx, cy)
        ctx.curve_to(mx + nx, my + ny, mx + nx, my + ny, tx, ty)
        ctx.curve_to(mx - nx, my - ny + 20, mx - nx, my - ny + 20, cx, cy); ctx.fill()

def vice_bg(ctx, t, tint=None):
    g = cairo.LinearGradient(0, 0, 0, H)
    for st, c in ((0, (.06, .02, .14)), (.4, (.22, .05, .3)), (.62, (.75, .25, .45)), (.76, (1, .55, .35)), (.8, (.25, .05, .3)), (1, (.05, .01, .1))):
        g.add_color_stop_rgb(st, *c)
    ctx.set_source(g); ctx.paint()
    rnd = random.Random(3)
    for i in range(30):
        ctx.new_path(); ctx.set_source_rgba(1, 1, 1, .15 + .15 * math.sin(t * 2 + i))
        ctx.arc(rnd.uniform(0, W), rnd.uniform(0, 900), rnd.uniform(1.5, 3.5), 0, 2 * math.pi); ctx.fill()
    sy, R = 1450, 290  # sol retro
    glow(ctx, 540, sy, 600, (1, .45, .5), .35)
    ctx.save(); ctx.new_path(); ctx.arc(540, sy, R, 0, 2 * math.pi); ctx.clip()
    sg = cairo.LinearGradient(0, sy - R, 0, sy + R); sg.add_color_stop_rgb(0, 1, .92, .45); sg.add_color_stop_rgb(1, 1, .3, .55)
    ctx.set_source(sg); ctx.paint(); ctx.set_source_rgb(.55, .15, .42)
    for i in range(9):
        y = sy - 10 + i * 34 + (t * 18) % 34; ctx.rectangle(240, y, 600, 3 + i * 1.8); ctx.fill()
    ctx.restore()
    rnd = random.Random(11); x = -20  # skyline
    while x < W + 20:
        bw = rnd.uniform(50, 120); bh = rnd.uniform(90, 380) * (1.4 if abs(x - 540) > 330 else .8)
        ctx.set_source_rgb(.11, .03, .16); ctx.rectangle(x, 1560 - bh, bw - 6, bh + 10); ctx.fill()
        for wy in range(int(1560 - bh + 20), 1540, 28):
            for wx in range(int(x + 10), int(x + bw - 16), 22):
                if rnd.random() < .3:
                    c = PINK if rnd.random() < .5 else CYAN
                    ctx.set_source_rgba(*c, .5 + .4 * math.sin(t * 3 + wx * .1 + wy)); ctx.rectangle(wx, wy, 8, 12); ctx.fill()
        x += bw
    wg = cairo.LinearGradient(0, 1560, 0, H); wg.add_color_stop_rgb(0, .3, .08, .3); wg.add_color_stop_rgb(1, .04, .01, .08)
    ctx.set_source(wg); ctx.rectangle(0, 1560, W, H - 1560); ctx.fill()
    for i in range(14):  # reflejos en el agua
        y = 1580 + i * 24; w = 420 - i * 22 + 30 * math.sin(t * 2 + i)
        ctx.set_source_rgba(1, .6, .5, .35 - i * .02); ctx.rectangle(540 - w / 2 + 20 * math.sin(t + i), y, w, 5); ctx.fill()
    palm(ctx, 60, 1960, 900, .35, t); palm(ctx, 1030, 1960, 820, -.4, t); palm(ctx, 170, 1990, 600, .5, t + 2)
    if tint in OVER: ctx.set_source_rgba(*OVER[tint]); ctx.paint()
    vg = cairo.RadialGradient(W / 2, H * .55, 300, W / 2, H * .55, H * .8)
    vg.add_color_stop_rgba(0, 0, 0, 0, 0); vg.add_color_stop_rgba(1, 0, 0, 0, .55)
    ctx.set_source(vg); ctx.paint()

# ---------- joystick ----------
CTRL_R = [(0, -175), (190, -185), (300, -165), (365, -110), (395, -10), (415, 110), (425, 215), (400, 285),
          (340, 300), (285, 255), (225, 165), (130, 125), (0, 125)]
SYM = {"x": (.55, .7, 1), "o": (1, .4, .45), "sq": (1, .5, .8), "tri": (.3, .9, .8)}

def ctrl_path(ctx, cx, cy, s):
    right = [(cx + x * s, cy + y * s) for x, y in CTRL_R]
    left = [(2 * cx - x, y) for x, y in reversed(right)][1:-1]
    pts = catmull(right + left + [right[0]], 6)
    ctx.new_path(); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path()

def stick(ctx, x, y, s, pressed=0.0, lit=0.0):
    r = 58 * s
    if lit > 0: glow(ctx, x, y, r * 3.2, CYAN, .8 * lit)
    ctx.set_source_rgb(.04, .04, .06); ctx.new_path(); ctx.arc(x, y, r * 1.18, 0, 2 * math.pi); ctx.fill()
    k = 1 - .14 * pressed
    g = cairo.RadialGradient(x - 15 * s, y - 18 * s, 2, x, y, r * k)
    g.add_color_stop_rgb(0, .5, .5, .56); g.add_color_stop_rgb(1, .1, .1, .13)
    ctx.set_source(g); ctx.new_path(); ctx.arc(x, y, r * k, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgba(*(CYAN if lit > .3 else (.35, .35, .4)), 1); ctx.set_line_width(4 * s)
    ctx.new_path(); ctx.arc(x, y, r * k * .72, 0, 2 * math.pi); ctx.stroke()

def face_btn(ctx, x, y, s, kind, pressed=0.0, lit=0.0):
    r = 31 * s * (1 - .12 * pressed); col = SYM[kind]
    if lit > 0: glow(ctx, x, y, 110 * s, col, .85 * lit)
    g = cairo.RadialGradient(x - 8 * s, y - 8 * s, 1, x, y, r)
    g.add_color_stop_rgb(0, .32, .32, .38); g.add_color_stop_rgb(1, .08, .08, .1)
    ctx.set_source(g); ctx.new_path(); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(*col); ctx.set_line_width(5 * s); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.new_path()
    q = r * .45
    if kind == "x": ctx.move_to(x - q, y - q); ctx.line_to(x + q, y + q); ctx.move_to(x + q, y - q); ctx.line_to(x - q, y + q)
    elif kind == "o": ctx.arc(x, y, q * 1.05, 0, 2 * math.pi)
    elif kind == "sq": ctx.rectangle(x - q * .9, y - q * .9, q * 1.8, q * 1.8)
    else: ctx.move_to(x, y - q * 1.1); ctx.line_to(x + q, y + q * .7); ctx.line_to(x - q, y + q * .7); ctx.close_path()
    ctx.stroke()

def controller(ctx, cx, cy, s, t, l3=(0, 0), x=(0, 0)):
    """l3/x = (presionado 0..1, brillo 0..1)."""
    floor_shadow(ctx, cx, cy + 320 * s, 420 * s, .5)
    for sx in (-1, 1):  # gatillos
        ctx.set_source_rgb(.15, .15, .18); rrect(ctx, cx + sx * 275 * s - 85 * s, cy - 215 * s, 170 * s, 60 * s, 24 * s); ctx.fill()
    ctrl_path(ctx, cx, cy, s)
    ctx.set_source(hgrad(cx - 430 * s, cx + 430 * s, (.78, .8, .86), (1, 1, 1))); ctx.fill_preserve()
    ctx.set_source_rgb(.6, .62, .7); ctx.set_line_width(4 * s); ctx.stroke()
    ctx.set_source_rgb(.1, .1, .13); rrect(ctx, cx - 215 * s, cy - 30 * s, 430 * s, 165 * s, 70 * s); ctx.fill()
    ctx.set_source_rgb(.93, .94, .97); rrect(ctx, cx - 145 * s, cy - 172 * s, 290 * s, 150 * s, 26 * s); ctx.fill_preserve()
    ctx.set_source_rgb(.75, .77, .83); ctx.set_line_width(3 * s); ctx.stroke()
    ctx.set_source_rgba(.35, .55, 1, .8); ctx.set_line_width(5 * s)  # luz azul
    ctx.new_path(); ctx.move_to(cx - 150 * s, cy - 175 * s); ctx.line_to(cx - 150 * s, cy - 30 * s); ctx.stroke()
    ctx.new_path(); ctx.move_to(cx + 150 * s, cy - 175 * s); ctx.line_to(cx + 150 * s, cy - 30 * s); ctx.stroke()
    dx, dy = cx - 275 * s, cy - 55 * s  # cruceta
    ctx.set_source_rgb(.25, .26, .3)
    for ox, oy, w, h in ((-14, -62, 28, 44), (-14, 18, 28, 44), (-62, -14, 44, 28), (18, -14, 44, 28)):
        rrect(ctx, dx + ox * s, dy + oy * s, w * s, h * s, 7 * s); ctx.fill()
    bx, by = cx + 275 * s, cy - 55 * s; o = 60 * s
    face_btn(ctx, bx, by - o, s, "tri"); face_btn(ctx, bx + o, by, s, "o"); face_btn(ctx, bx - o, by, s, "sq")
    face_btn(ctx, bx, by + o, s, "x", *x)
    stick(ctx, cx - 125 * s, cy + 60 * s, s, *l3); stick(ctx, cx + 125 * s, cy + 60 * s, s)
    ctx.save(); ctrl_path(ctx, cx, cy, s); ctx.clip(); shine(ctx, cx - 330 * s, cy - 200 * s, 60 * s, 520 * s, .5); ctx.restore()

def x_pos(cx, cy, s): return cx + 275 * s, cy + 5 * s
def l3_pos(cx, cy, s): return cx - 125 * s, cy + 60 * s

def tap(t, rate=5):
    return 1.0 if (t * rate) % 1 < .35 else 0.0

def ring(ctx, x, y, t, rate=5, color=CYAN, r0=40):
    u = (t * rate) % 1
    ctx.set_source_rgba(*color, 1 - u); ctx.set_line_width(6); ctx.new_path(); ctx.arc(x, y, r0 + 70 * u, 0, 2 * math.pi); ctx.stroke()

# ---------- muñequito (pictograma) ----------
def runner(ctx, x, y, s, t, mode="run", color=(1, 1, 1)):
    freq = {"walk": 5, "run": 12}.get(mode, 0); amp = {"walk": .45, "run": 1.0}.get(mode, .12)
    ph = t * freq; dy = -abs(math.sin(t * 5)) * 150 if mode == "jump" else 0
    lean = .3 if mode == "run" else 0
    floor_shadow(ctx, x, y + 5, 110 * s * (1 - .4 * abs(dy) / 150), .5)
    if mode == "run":
        for i in range(4):
            u = (t * 2.5 + i * .25) % 1; yy = y - 260 * s + i * 55 * s
            ctx.set_source_rgba(*CYAN, .7 * (1 - u)); ctx.set_line_width(8 * s); ctx.new_path()
            ctx.move_to(x - 120 * s - u * 200 * s, yy); ctx.line_to(x - 220 * s - u * 260 * s, yy); ctx.stroke()
    ctx.save(); ctx.translate(x, y + dy); ctx.scale(s, s)
    glow(ctx, 0, -170, 260, PINK, .35)
    ctx.set_source_rgb(*color); ctx.set_line_width(26); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    hip = (0, -120); sh = (lean * 90, -250)
    def limb(base, a, b, L1, L2):
        k = (base[0] + L1 * math.sin(a), base[1] + L1 * math.cos(a))
        f = (k[0] + L2 * math.sin(b), k[1] + L2 * math.cos(b))
        ctx.new_path(); ctx.move_to(*base); ctx.line_to(*k); ctx.line_to(*f); ctx.stroke()
    for side in (-1, 1):
        if mode == "jump": a, b = .55 * side, .05 * side
        else:
            a = amp * .8 * math.sin(ph + (side > 0) * math.pi); b = a - amp * .9 * (.5 + .5 * math.sin(ph + (side > 0) * math.pi + 1.6))
        limb(hip, a, b, 62, 62)
        aa = -amp * .9 * math.sin(ph + (side > 0) * math.pi) if mode != "jump" else 2.4 * side
        limb(sh, aa, aa + (1.4 if mode == "run" else .4), 50, 48)
    ctx.new_path(); ctx.move_to(*hip); ctx.line_to(*sh); ctx.stroke()
    ctx.new_path(); ctx.arc(lean * 110, -305, 36, 0, 2 * math.pi); ctx.fill()
    ctx.restore()

# ---------- extras ----------
def neon_text(ctx, text, cx, cy, size, color=PINK, a=1.0):
    if a <= 0: return
    font(ctx, size); e = ctx.text_extents(text); x = cx - e.x_advance / 2
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for lw, al in ((30, .12), (16, .25), (7, .7)):
        ctx.new_path(); ctx.move_to(x, cy); ctx.text_path(text)
        ctx.set_source_rgba(*color, al * a); ctx.set_line_width(lw); ctx.stroke()
    ctx.new_path(); ctx.move_to(x, cy); ctx.text_path(text); ctx.set_source_rgba(1, .95, 1, a); ctx.fill(); ctx.new_path()

def flicker(t, on=.3):
    if t < on: return 0
    if t < on + .5: return 1.0 if int(t * 25) % 3 else .2
    return .9 + .1 * math.sin(t * 9)

def menu(ctx, t, switch_at, a=1.0):
    """Panel de Ajustes > Controles con selector Predeterminado -> Clásico."""
    if a <= 0: return
    ctx.push_group()
    ctx.set_source_rgba(.05, .02, .1, .85); rrect(ctx, 120, 760, 840, 460, 36); ctx.fill_preserve()
    ctx.set_source_rgba(*PINK, .9); ctx.set_line_width(4); ctx.stroke()
    font(ctx, 44); ctx.set_source_rgb(*CYAN); ctx.move_to(180, 850); ctx.show_text("AJUSTES  ·  CONTROLES"); ctx.new_path()
    ctx.set_source_rgba(1, 1, 1, .15); ctx.rectangle(180, 885, 720, 3); ctx.fill()
    font(ctx, 46, bold=False); ctx.set_source_rgb(1, 1, 1); ctx.move_to(180, 990); ctx.show_text("Esquema"); ctx.new_path()
    ctx.set_source_rgba(1, 1, 1, .4); ctx.move_to(180, 1120); ctx.show_text("Vibración"); ctx.new_path()
    font(ctx, 44); ctx.move_to(720, 1120); ctx.show_text("Sí"); ctx.new_path()
    on = t > switch_at; sw = pop(t, switch_at, .35) if on else 1
    ctx.set_source_rgba(*(YELLOW if on else (.3, .3, .4)), 1); rrect(ctx, 470, 940, 450, 76, 38); ctx.fill()
    txt = "Clásico" if on else "Predeterminado"; font(ctx, 42); e = ctx.text_extents(txt)
    ctx.save(); ctx.translate(695, 992); ctx.scale(sw, sw)
    ctx.set_source_rgb(*((.07, .07, .1) if on else (1, 1, 1))); ctx.move_to(-e.x_advance / 2, 0); ctx.show_text(txt); ctx.new_path(); ctx.restore()
    for sx in (-1, 1):
        ax = 695 + sx * 195; ctx.set_source_rgb(*((.07, .07, .1) if on else (1, 1, 1)))
        ctx.new_path(); ctx.move_to(ax + sx * 14, 978); ctx.line_to(ax - sx * 6, 966); ctx.line_to(ax - sx * 6, 990); ctx.close_path(); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

# ---------- escenas reutilizables ----------
def scene_x(ctx, t, T, caps, tint="malo"):
    """La X ahora salta."""
    vice_bg(ctx, t, tint)
    cx, cy, s = 540, 1380 + slide_in(t, 0, .5, 600), 1.1
    p = tap(t)
    controller(ctx, cx, cy, s, t, x=(p, .5 + .5 * p))
    xx, xy = x_pos(cx, cy, s); ring(ctx, xx, xy, t, color=SYM["x"])
    runner(ctx, 540, 1050, .85, t, "jump" if t > .3 else "idle")
    label(ctx, "X = saltar", 830, 900, 50, alpha=prog(t, 2.2, .3), bg=BAD_BG)
    badge(ctx, 250, 880, 66, prog(t, 4.0, .4), ok=False)
    captions(ctx, t, caps)

def scene_l3(ctx, t, T, caps, tint="bueno"):
    """Correr = hundir el stick izquierdo (L3)."""
    vice_bg(ctx, t, tint)
    cx, cy, s = 540, 1400, 1.1
    press_t = 2.0
    pr = 1.0 if press_t < t < press_t + .35 else 0.0
    lit = prog(t, press_t - .4, .3)
    controller(ctx, cx, cy, s, t, l3=(pr, lit))
    lx, ly = l3_pos(cx, cy, s)
    if t > press_t: ring(ctx, lx, ly, t - press_t, rate=1.5, r0=70)
    runner(ctx, 560, 1040, .85, t, "run" if t > press_t else "walk")
    pa = prog(t, press_t, .3)
    label(ctx, "L3 = correr", 250, 1130, 50, alpha=pa, bg=OK_BG); arrow(ctx, 260, 1180, lx - 30, ly - 70, alpha=pa, color=CYAN)
    badge(ctx, 860, 880, 66, prog(t, 4.2, .4), ok=True)
    captions(ctx, t, caps)

def scene_clasico(ctx, t, T, caps, tint="info"):
    vice_bg(ctx, t, tint)
    menu(ctx, t, 2.8, a=prog(t, .1, .3))
    cx, cy, s = 540, 1530, .6
    on = t > 3.4
    p = tap(t, 4) if on else 0
    controller(ctx, cx, cy, s, t, x=(p, 1.0 if on else 0))
    label(ctx, "X = correr", 820, 1350, 46, alpha=prog(t, 3.6, .3), bg=OK_BG)
    badge(ctx, 220, 1330, 56, prog(t, 3.8, .4), ok=True)
    captions(ctx, t, caps)

def scene_markpoint(ctx, t, T, caps):
    vice_bg(ctx, t, "cierre")
    f = flicker(t, .3)
    neon_text(ctx, "MARKPOINT", 540, 820, 140, PINK, f)
    ctx.set_source_rgba(*CYAN, .8 * f); rrect(ctx, 200, 860, 680, 8, 4); ctx.fill()
    for sx in (-1, 1):  # spots
        g = cairo.LinearGradient(0, 880, 0, 1600); g.add_color_stop_rgba(0, 1, 1, 1, .22 * f); g.add_color_stop_rgba(1, 1, 1, 1, 0)
        ctx.set_source(g); ctx.new_path(); ctx.move_to(540 + sx * 300, 880); ctx.line_to(540 + sx * 40, 880)
        ctx.line_to(540 - sx * 260, 1600); ctx.line_to(540 + sx * 120, 1600); ctx.close_path(); ctx.fill()
    py = 1520 + slide_in(t, .5, .6, 500)
    ctx.set_source(hgrad(260, 820, (.15, .05, .2), (.45, .2, .5))); rrect(ctx, 260, py, 560, 220, 20); ctx.fill()
    ctx.set_source_rgba(*PINK, .9); rrect(ctx, 260, py, 560, 10, 5); ctx.fill()
    s = .82 * pop(t, .9, .5); cy = py - 210 + 12 * math.sin(t * 2.5)
    glow(ctx, 540, cy, 480, PINK, .25)
    ctx.save(); ctx.translate(540, cy); ctx.rotate(.05 * math.sin(t * 1.7)); ctx.translate(-540, -cy)
    controller(ctx, 540, cy, s, t); ctx.restore()
    label(ctx, "PS5 original", 540, py + 110, 54, alpha=prog(t, 1.6, .3), bg=(0, 0, 0, .0), color=YELLOW)
    captions(ctx, t, caps)

# ---------- escenas propias del video ----------
def s1(ctx, t, T):
    vice_bg(ctx, t)
    hook_title(ctx, t, [("¿Cómo se corre", 84), ("en [GTA 6]", 124), ("de verdad?", 84)])
    cy = 1380 + slide_in(t, .2, .6, 900)
    controller(ctx, 540, cy, 1.0, t, l3=(0, .5 + .5 * math.sin(t * 5)))
    runner(ctx, 540, cy - 320, .7, t, "run")

def s2(ctx, t, T):
    vice_bg(ctx, t)
    z = 1 + .25 * ease_in_out(prog(t, 0, T))
    ctx.save(); ctx.translate(540, 1300); ctx.scale(z, z); ctx.translate(-540, -1300)
    controller(ctx, 540, 1300, 1.0, t, x=(0, .4), l3=(0, .4))
    ctx.restore()
    captions(ctx, t, [(0, 1.6, "Casi nadie lo [sabe]"), (1.6, T, "cambió el [botón]")])

def s7(ctx, t, T):
    vice_bg(ctx, t, "cierre")
    runner(ctx, 540, 1300 + 10 * math.sin(t * 3), 1.1, t, "run")
    captions(ctx, t, [(0, 1.8, "Guardalo para correr"), (1.8, T, "por [Vice City]")], y=420, size=96)

SCENES = [
    dict(name="s1_gancho", draw=s1, dur=3.5, voz="¿Cómo se corre en GTA 6 de verdad?", check=2.5),
    dict(name="s2_regancho", draw=s2, dur=3.2, voz="Casi nadie lo sabe: cambió el botón.", check=2.4),
    dict(name="s3_x", draw=partial(scene_x, caps=[(0, 2.2, "Antes: [X] sin parar"), (2.2, 4.0, "Ahora la X"), (4.0, 6.0, "sirve para [saltar]")]),
         dur=6.0, voz="Antes corrías apretando X sin parar. Ahora, la X sirve para saltar.", check=4.6),
    dict(name="s4_l3", draw=partial(scene_l3, caps=[(0, 2.0, "Para [correr]"), (2.0, 4.2, "hundí el [stick izquierdo]"), (4.2, 7.5, "el famoso [L3]")]),
         dur=7.5, voz="Para correr, hundí el stick izquierdo: el famoso L3. Lo apretás y tu personaje arranca.", check=5.0),
    dict(name="s5_clasico", draw=partial(scene_clasico, caps=[(0, 2.4, "¿Extrañás lo [viejo]?"), (2.4, 4.6, "Ajustes: modo [Clásico]"), (4.6, 6.8, "y la X vuelve a [correr]")]),
         dur=6.8, voz="¿Extrañás lo viejo? En Ajustes elegí el modo Clásico y la X vuelve a correr.", check=5.0),
    dict(name="s6_markpoint", draw=partial(scene_markpoint, caps=[(0, 2.4, "¿Tu joystick no [responde]?"), (2.4, 4.8, "El mejor PS5 [original]"), (4.8, 7.0, "está en [MARKPOINT]")]),
         dur=7.0, voz="Y si tu joystick ya no responde, el mejor joystick de PS5 original está en Markpoint.", check=5.5),
    dict(name="s7_cta", draw=s7, dur=4.0, voz="Guardalo para cuando salgas a correr por Vice City.", check=3.0),
]

if __name__ == "__main__":
    make_video("gta6-correr", "¿Cómo se corre en GTA 6?", SCENES)
