from motor import *

ORANGE = (1, .5, .15)

# ---------- objetos ----------
def heat_waves(ctx, t, cx, top, w, n=3, h=220, a=.55, color=(1, .6, .3)):
    ctx.save(); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * w / max(1, n - 1)
        ph = (t * .8 + i * .37) % 1
        y0 = top - ph * 120; al = a * math.sin(ph * math.pi)
        ctx.set_source_rgba(*color, al); ctx.set_line_width(9); ctx.new_path()
        for k in range(21):
            yy = y0 - k * h / 20; xx = x + 16 * math.sin(k * .6 + t * 5 + i)
            (ctx.move_to if k == 0 else ctx.line_to)(xx, yy)
        ctx.stroke()
    ctx.restore()

def cable(ctx, pts, s=1, color=(.92, .92, .95)):
    P = catmull(pts, 12); ctx.new_path(); ctx.move_to(*P[0])
    for p in P[1:]: ctx.line_to(*p)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgb(.5, .5, .55); ctx.set_line_width(24 * s); ctx.stroke_preserve()
    ctx.set_source_rgb(*color); ctx.set_line_width(16 * s); ctx.stroke()

def flow(ctx, t, pts, n=6, speed=.5, color=YELLOW, r=11, alpha=1.0):
    if alpha <= 0: return
    P = catmull(pts, 12); L = len(P)
    for k in range(n):
        u = (k / n + t * speed) % 1; x, y = P[int(u * (L - 1))]
        glow(ctx, x, y, r * 3, color, .5 * alpha)
        ctx.set_source_rgba(*color, alpha); ctx.new_path(); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()

def charger_cable_pts(cx, cy, s, end=None):
    end = end or (cx + 60 * s, H + 60)
    return [(cx, cy + 140 * s), (cx, cy + 230 * s), (cx + 40 * s, cy + 330 * s), end]

def charger_body(ctx, cx, cy, s):
    ctx.new_path(); rrect(ctx, cx - 130 * s, cy - 140 * s, 260 * s, 280 * s, 46 * s)

def charger(ctx, cx, cy, s, t, heat=0.0, cable_end=None, waves=True):
    heat = clamp(heat)
    if heat > .02: glow(ctx, cx, cy, 340 * s * (1 + .25 * heat), ORANGE, .45 * heat)
    cable(ctx, charger_cable_pts(cx, cy, s, cable_end), s)
    for dx in (-55, 55):  # patas
        x = cx + dx * s
        ctx.set_source(hgrad(x - 14 * s, x + 14 * s, (.5, .5, .55), (.97, .97, 1)))
        rrect(ctx, x - 14 * s, cy - 255 * s, 28 * s, 130 * s, 5 * s); ctx.fill()
    charger_body(ctx, cx, cy, s)
    ctx.set_source(hgrad(cx - 130 * s, cx + 130 * s, (.7, .72, .77), (.98, .98, 1))); ctx.fill_preserve()
    ctx.set_source_rgb(.55, .57, .62); ctx.set_line_width(3 * s); ctx.stroke()
    ctx.save(); charger_body(ctx, cx, cy, s); ctx.clip()
    if heat > .02:
        g = cairo.RadialGradient(cx, cy + 20 * s, 0, cx, cy + 20 * s, 220 * s)
        g.add_color_stop_rgba(0, 1, .3, .08, .6 * heat); g.add_color_stop_rgba(1, 1, .5, .2, .12 * heat)
        ctx.set_source(g); ctx.paint()
    shine(ctx, cx - 85 * s, cy - 150 * s, 40 * s, 300 * s, .6)
    ctx.restore()
    ctx.set_source_rgb(.2, .2, .24); rrect(ctx, cx - 30 * s, cy + 118 * s, 60 * s, 16 * s, 6 * s); ctx.fill()  # puerto
    if waves and heat > .05: heat_waves(ctx, t, cx, cy - 165 * s, 230 * s, a=.6 * heat)

def charger_inside(ctx, cx, cy, s, t, p):
    """Corte interior que se abre (p 0..1)."""
    if p <= .01: return
    ctx.save(); charger_body(ctx, cx, cy, s); ctx.clip()
    w = 230 * s * p; ctx.rectangle(cx - w / 2, cy - 125 * s, w, 250 * s); ctx.clip()
    ctx.set_source_rgb(.05, .28, .15); ctx.paint()
    ctx.set_source_rgba(.6, .85, .3, .5); ctx.set_line_width(3 * s)
    for i in range(7):
        ctx.new_path(); ctx.move_to(cx - 120 * s, cy - 110 * s + i * 36 * s)
        ctx.line_to(cx + 120 * s, cy - 110 * s + i * 36 * s + (i % 2) * 18 * s); ctx.stroke()
    ctx.set_source_rgb(.12, .12, .15); rrect(ctx, cx - 95 * s, cy - 95 * s, 120 * s, 125 * s, 8 * s); ctx.fill()
    ctx.set_source(hgrad(cx - 85 * s, cx + 15 * s, (.6, .38, .05), (1, .78, .3)))
    rrect(ctx, cx - 85 * s, cy - 78 * s, 100 * s, 90 * s, 10 * s); ctx.fill()  # transformador
    ctx.set_source_rgba(.45, .25, .03, .8); ctx.set_line_width(2 * s)
    for i in range(9):
        y = cy - 72 * s + i * 10 * s; ctx.new_path(); ctx.move_to(cx - 85 * s, y); ctx.line_to(cx + 15 * s, y); ctx.stroke()
    for dx, dy in ((62, -60), (62, 15)):  # capacitores
        x, y = cx + dx * s, cy + dy * s
        ctx.set_source(hgrad(x - 24 * s, x + 24 * s, (.05, .15, .4), (.35, .55, 1)))
        rrect(ctx, x - 24 * s, y - 32 * s, 48 * s, 64 * s, 12 * s); ctx.fill()
    ctx.set_source_rgb(.06, .06, .08); rrect(ctx, cx - 80 * s, cy + 50 * s, 80 * s, 50 * s, 5 * s); ctx.fill()  # chip
    rnd = random.Random(int(t * 20))
    for k in range(4):
        glow(ctx, cx + rnd.uniform(-100, 100) * s, cy + rnd.uniform(-100, 100) * s, 34 * s, (1, .9, .4), .85)
    ctx.restore()

def thermometer(ctx, x, top, bottom, level, alpha=1.0):
    if alpha <= 0: return
    ctx.push_group()
    ctx.set_source_rgba(1, 1, 1, .9); rrect(ctx, x - 26, top - 6, 52, bottom - top + 6, 26); ctx.fill()
    ctx.new_path(); ctx.arc(x, bottom + 20, 50, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(.2, .2, .25); rrect(ctx, x - 16, top + 4, 32, bottom - top, 16); ctx.fill()
    col = (1, .3 + .4 * (1 - level), .15)
    hh = max(10, (bottom - top - 10) * clamp(level))
    ctx.set_source_rgb(*col); rrect(ctx, x - 14, bottom - hh, 28, hh + 10, 14); ctx.fill()
    ctx.new_path(); ctx.arc(x, bottom + 20, 38, 0, 2 * math.pi); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha)

INFO_BG = (.1, .3, .7, .85)
OK_BG, BAD_BG = (.1, .5, .25, .85), (.6, .1, .1, .85)

# ---------- escenas ----------
def s1(ctx, t, T):  # GANCHO
    background(ctx, t)
    hook_title(ctx, t, [("¿Por qué tu", 84), ("[CARGADOR]", 130), ("se calienta?", 84)])
    cy = 1300 + slide_in(t, .2, .6, 900)
    charger(ctx, 540, cy, 1.25, t, heat=.65 + .2 * math.sin(t * 4))

def s2(ctx, t, T):  # RE-GANCHO
    background(ctx, t)
    z = 1 + .2 * ease_in_out(prog(t, 0, T))
    ctx.save(); ctx.translate(540, 1200); ctx.scale(z, z); ctx.translate(-540, -1200)
    charger(ctx, 540, 1200, 1.3, t, heat=.85)
    ctx.restore()
    captions(ctx, t, [(0, 1.4, "No está [roto]"), (1.4, T, "Es [física]")])

def s3(ctx, t, T):  # 220 V -> 5 V
    background(ctx, t, "info")
    cx, cy, s = 540, 1180, 1.1
    ctx.save(); ctx.translate(0, slide_in(t))
    charger(ctx, cx, cy, s, t, heat=.15)
    flow(ctx, t, charger_cable_pts(cx, cy, s), n=5, speed=.35, color=(.4, .9, 1), r=9, alpha=prog(t, 2.5, .4))
    ctx.restore()
    pa = prog(t, .5, .4)
    label(ctx, "220 V del enchufe", 330, 800, 46, alpha=pa, bg=BAD_BG); arrow(ctx, 330, 850, 470, 920, alpha=pa)
    pb = prog(t, 2.6, .4)
    label(ctx, "5 V al celu", 830, 1560, 46, alpha=pb, bg=OK_BG); arrow(ctx, 760, 1510, 640, 1460, alpha=pb)
    captions(ctx, t, [(0, 2.5, "Del enchufe: [220 V]"), (2.5, 4.3, "pero tu celu"), (4.3, T, "usa solo [5 V]")])

def s4(ctx, t, T):  # CORTE INTERIOR
    background(ctx, t, "malo")
    cx, cy, s = 540, 1150, 1.6
    charger(ctx, cx, cy, s, t, heat=.35, waves=False)
    charger_inside(ctx, cx, cy, s, t, ease_out(prog(t, .4, .8)))
    pa = prog(t, 2.2, .4)
    label(ctx, "convertidor", 840, 820, 46, alpha=pa, bg=INFO_BG); arrow(ctx, 820, 870, 540, 1030, alpha=pa)
    label(ctx, "220 V → 5 V", 540, 1560, 48, alpha=prog(t, 4.4, .4), bg=BAD_BG)
    captions(ctx, t, [(0, 2.2, "Adentro, un [convertidor]"), (2.2, 4.4, "baja el [voltaje]"),
                      (4.4, T, "[miles] de veces por segundo")])

def s5(ctx, t, T):  # PÉRDIDA = CALOR
    background(ctx, t, "malo")
    cx, cy, s = 580, 1130, 1.2
    heat = .2 + .8 * ease_in_out(prog(t, 1.5, 4))
    charger(ctx, cx, cy, s, t, heat=heat)
    flow(ctx, t, charger_cable_pts(cx, cy, s), n=5, speed=.35, color=(.4, .9, 1), r=9)
    thermometer(ctx, 150, 900, 1400, heat, alpha=prog(t, .3, .4))
    pa = prog(t, 4.4, .4)
    label(ctx, "pérdida", 600, 760, 50, alpha=pa, bg=BAD_BG)
    label(ctx, "energía útil", 850, 1580, 44, alpha=prog(t, 2.3, .4), bg=OK_BG)
    captions(ctx, t, [(0, 2.3, "Ninguna conversión es [perfecta]"), (2.3, 4.4, "una parte de la [energía]"),
                      (4.4, T, "se pierde como [CALOR]")])

def s6(ctx, t, T):  # REVELACIÓN: carga rápida
    background(ctx, t, "info")
    charger(ctx, 290, 1300 + slide_in(t, 0, .5), .75, t, heat=.12)
    charger(ctx, 740, 1240 + slide_in(t, .2, .5), 1.15, t, heat=.85 + .1 * math.sin(t * 5))
    label(ctx, "5 W", 290, 1560, 52, alpha=prog(t, .4, .3), bg=OK_BG)
    label(ctx, "carga rápida", 740, 1600, 52, alpha=prog(t, .6, .3), bg=BAD_BG)
    badge(ctx, 290, 900, 60, prog(t, 3.2, .4), ok=True)
    badge(ctx, 860, 800, 60, prog(t, 4.6, .4), ok=False)
    captions(ctx, t, [(0, 1.6, "Carga [rápida]"), (1.6, 3.2, "= más [calor]"), (3.2, 4.6, "Tibio es [normal]"),
                      (4.6, T, "si quema, [desenchufalo]")])

def s7(ctx, t, T):  # CTA
    background(ctx, t, "cierre")
    cy = 1250 + 20 * math.sin(t * 2.5)
    glow(ctx, 540, cy, 520, a=.18 + .06 * math.sin(t * 4))
    charger(ctx, 540, cy, 1.2, t, heat=.5)
    captions(ctx, t, [(0, 1.9, "Mandáselo a quien"), (1.9, T, "creía que estaba [roto]")], y=420, size=96)

SCENES = [
    dict(name="s1_gancho", draw=s1, dur=3.5, voz="¿Por qué tu cargador se calienta?", check=2.0),
    dict(name="s2_regancho", draw=s2, dur=3.0, voz="No está roto: es pura física.", check=2.0),
    dict(name="s3_voltaje", draw=s3, dur=6.0, voz="Del enchufe salen 220 voltios, pero tu celu solo usa 5.", check=5.0),
    dict(name="s4_adentro", draw=s4, dur=6.5, voz="Adentro, un convertidor baja ese voltaje miles de veces por segundo.", check=5.5),
    dict(name="s5_calor", draw=s5, dur=6.5, voz="Ninguna conversión es perfecta: una parte de la energía se pierde como calor.", check=5.5),
    dict(name="s6_rapida", draw=s6, dur=6.0, voz="Por eso la carga rápida calienta más. Tibio es normal; si quema, desenchufalo.", check=5.2),
    dict(name="s7_cta", draw=s7, dur=4.0, voz="Mandáselo a quien creía que su cargador estaba roto.", check=3.0),
]

if __name__ == "__main__":
    make_video("cargador-caliente", "¿Por qué se calienta el cargador?", SCENES)
