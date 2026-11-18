from motor import *
import importlib
_c = importlib.import_module("video_cargador-caliente")
cable, flow, heat_waves, thermometer = _c.cable, _c.flow, _c.heat_waves, _c.thermometer
OK_BG, BAD_BG, INFO_BG = _c.OK_BG, _c.BAD_BG, _c.INFO_BG

# ---------- objetos ----------
def phone_cable_pts(cx, cy, s):
    return [(cx, cy + 360 * s), (cx, cy + 440 * s), (cx + 50 * s, cy + 520 * s), (cx + 70 * s, H + 80)]

def phone(ctx, cx, cy, s, t, pct, charging=True, show_pct=True, heat=0.0, cable_on=True):
    hw, hh = 180 * s, 360 * s
    if heat > .02: glow(ctx, cx, cy, 520 * s, (1, .35, .15), .5 * heat)
    if cable_on: cable(ctx, phone_cable_pts(cx, cy, s), s)
    ctx.new_path(); rrect(ctx, cx - hw, cy - hh, 2 * hw, 2 * hh, 56 * s)
    ctx.set_source(hgrad(cx - hw, cx + hw, (.12, .12, .16), (.4, .41, .48))); ctx.fill()
    sx, sy, sw, sh = cx - hw + 16 * s, cy - hh + 16 * s, 2 * hw - 32 * s, 2 * hh - 32 * s
    ctx.new_path(); rrect(ctx, sx, sy, sw, sh, 44 * s)
    g = cairo.LinearGradient(0, sy, 0, sy + sh); g.add_color_stop_rgb(0, .07, .1, .2); g.add_color_stop_rgb(1, .02, .03, .07)
    ctx.set_source(g); ctx.fill()
    ctx.set_source_rgb(0, 0, 0); rrect(ctx, cx - 50 * s, sy + 18 * s, 100 * s, 26 * s, 13 * s); ctx.fill()
    bw, bh = 130 * s, 250 * s; bx, by = cx - bw / 2, cy - bh / 2 - 40 * s
    ctx.set_source_rgba(1, 1, 1, .85); ctx.set_line_width(8 * s); ctx.new_path(); rrect(ctx, bx, by, bw, bh, 18 * s); ctx.stroke()
    rrect(ctx, cx - 30 * s, by - 22 * s, 60 * s, 20 * s, 6 * s); ctx.fill()
    p = clamp(pct); col = GREEN if p > .5 else (YELLOW if p > .2 else RED)
    fh = max(2, (bh - 24 * s) * p)
    ctx.set_source_rgb(*col); rrect(ctx, bx + 12 * s, by + bh - 12 * s - fh, bw - 24 * s, fh, 8 * s); ctx.fill()
    if charging:
        bc = by + bh / 2; k = 1.3 * s
        ctx.new_path()
        for i, (x, y) in enumerate([(10, -62), (-34, 8), (-2, 8), (-12, 62), (34, -10), (2, -10)]):
            (ctx.move_to if i == 0 else ctx.line_to)(cx + x * k, bc + y * k)
        ctx.close_path(); ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve()
        ctx.set_source_rgba(0, 0, 0, .5); ctx.set_line_width(3 * s); ctx.stroke()
    if show_pct:
        font(ctx, 66 * s); txt = f"{round(p * 100)}%"; e = ctx.text_extents(txt)
        ctx.set_source_rgb(1, 1, 1); ctx.move_to(cx - e.x_advance / 2, by + bh + 100 * s); ctx.show_text(txt); ctx.new_path()
    ctx.save(); ctx.new_path(); rrect(ctx, cx - hw, cy - hh, 2 * hw, 2 * hh, 56 * s); ctx.clip()
    if heat > .02:
        gg = cairo.RadialGradient(cx, cy, 0, cx, cy, 400 * s)
        gg.add_color_stop_rgba(0, 1, .3, .1, .45 * heat); gg.add_color_stop_rgba(1, 1, .4, .1, .1 * heat)
        ctx.set_source(gg); ctx.paint()
    shine(ctx, cx - 120 * s, cy - hh, 50 * s, 2 * hh, .18)
    ctx.restore()

def phone_lying(ctx, cx, cy, s, t, pct, heat=0.0):
    """Celu acostado (cable sale a la derecha)."""
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(-math.pi / 2); ctx.translate(-cx, -cy)
    phone(ctx, cx, cy, s, t, pct, charging=True, show_pct=False, heat=heat, cable_on=False)
    ctx.restore()
    cable(ctx, [(cx + 360 * s, cy), (cx + 440 * s, cy), (cx + 520 * s, cy + 40 * s), (W + 80, cy + 60 * s)], s)

def pillow(ctx, cx, cy, s, t):
    w, h = 300 * s, 150 * s
    floor_shadow(ctx, cx, cy + h, w * 1.1, .5)
    ctx.new_path(); rrect(ctx, cx - w, cy - h, 2 * w, 2 * h, 130 * s)
    g = cairo.LinearGradient(0, cy - h, 0, cy + h)
    g.add_color_stop_rgb(0, .95, .95, 1); g.add_color_stop_rgb(1, .62, .64, .78)
    ctx.set_source(g); ctx.fill_preserve(); ctx.set_source_rgb(.5, .52, .65); ctx.set_line_width(4 * s); ctx.stroke()
    ctx.set_source_rgba(.5, .52, .65, .7); ctx.set_line_width(3 * s); ctx.set_dash([14 * s, 10 * s])
    ctx.new_path(); rrect(ctx, cx - w + 30 * s, cy - h + 30 * s, 2 * w - 60 * s, 2 * h - 60 * s, 100 * s); ctx.stroke()
    ctx.set_dash([])

def moon(ctx, x, y, r, alpha=1.0):
    if alpha <= 0: return
    glow(ctx, x, y, r * 2.6, (1, .95, .7), .25 * alpha)
    ctx.push_group(); ctx.new_path(); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.set_source_rgba(1, .93, .65, 1); ctx.fill()
    ctx.set_operator(cairo.OPERATOR_CLEAR); ctx.new_path(); ctx.arc(x + r * .45, y - r * .25, r * .85, 0, 2 * math.pi); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha)

def chip(ctx, x, y, a):
    if a <= 0: return
    ctx.set_source_rgba(.75, .75, .8, a); ctx.set_line_width(6)
    for i in range(4):
        d = -36 + i * 24
        for sx, sy, ex, ey in ((x + d, y - 60, x + d, y - 40), (x + d, y + 40, x + d, y + 60),
                               (x - 60, y + d, x - 40, y + d), (x + 40, y + d, x + 60, y + d)):
            ctx.new_path(); ctx.move_to(sx, sy); ctx.line_to(ex, ey); ctx.stroke()
    ctx.set_source_rgba(.08, .08, .1, a); rrect(ctx, x - 48, y - 48, 96, 96, 10); ctx.fill()
    ctx.set_source_rgba(.3, .9, .5, a); rrect(ctx, x - 22, y - 22, 44, 44, 6); ctx.fill()

# ---------- escenas ----------
def s1(ctx, t, T):  # GANCHO (mito)
    background(ctx, t)
    hook_title(ctx, t, [("Tu batería se gasta…", 80), ("y no es por [CARGARLA]", 108), ("toda la noche", 84)])
    cy = 1270 + slide_in(t, .2, .6, 900)
    moon(ctx, 880, 860, 60, prog(t, .8, .4))
    glow(ctx, 540, cy, 420, a=.15 + .06 * math.sin(t * 4))
    phone(ctx, 540, cy, .95, t, .35 + .55 * prog(t, 0, T))

def s2(ctx, t, T):  # RE-GANCHO
    background(ctx, t)
    z = 1 + .2 * ease_in_out(prog(t, 0, T))
    ctx.save(); ctx.translate(540, 1200); ctx.scale(z, z); ctx.translate(-540, -1200)
    glow(ctx, 540, 1200, 450, a=.2)
    phone(ctx, 540, 1200, .95, t, .9)
    ctx.restore()
    captions(ctx, t, [(0, 1.5, "Y no es"), (1.5, T, "lo que [pensás]")])

def s3(ctx, t, T):  # CORTA SOLO AL 100
    background(ctx, t, "bueno")
    cx, cy, s = 540, 1150, 1.0
    cut = t > 2.6
    ctx.save(); ctx.translate(0, slide_in(t))
    phone(ctx, cx, cy, s, t, .9 + .1 * prog(t, 0, 2.3), charging=not cut)
    flow(ctx, t, phone_cable_pts(cx, cy, s), n=5, speed=-.35, color=(.4, .9, 1), r=9, alpha=1 - prog(t, 2.4, .3))
    ctx.restore()
    pc = prog(t, 4.6, .4)
    chip(ctx, 870, 1430, pc); arrow(ctx, 810, 1400, 700, 1340, alpha=pc)
    label(ctx, "chip de carga", 870, 1560, 44, alpha=pc, bg=INFO_BG)
    badge(ctx, 840, 900, 70, prog(t, 2.7, .4))
    label(ctx, "carga cortada", 840, 1010, 44, alpha=prog(t, 2.8, .3), bg=OK_BG)
    captions(ctx, t, [(0, 2.3, "Al llegar al [100%]"), (2.3, 4.6, "el celu [corta] la carga"),
                      (4.6, T, "lo controla un [chip]")])

def s4(ctx, t, T):  # CARGA OPTIMIZADA
    background(ctx, t, "info")
    morning = prog(t, 4.6, .5)
    moon(ctx, 190, 820, 60, 1 - morning)
    glow(ctx, 190, 820, 160, (1, .8, .3), .5 * morning)
    label(ctx, "06:50" if t > 4.6 else "03:00", 880, 820, 56, bg=(0, 0, 0, .6))
    pct = .8 + .2 * ease_in_out(prog(t, 4.8, 1.5)) if t > 2 else .7 + .1 * prog(t, 0, 2)
    phone(ctx, 540, 1180, .95, t, pct, charging=True)
    label(ctx, "pausa en 80%", 540, 1700, 50, alpha=prog(t, 1.6, .3) * (1 - morning), bg=INFO_BG)
    label(ctx, "listo al despertar", 540, 1700, 50, alpha=prog(t, 5.6, .3), bg=OK_BG)
    captions(ctx, t, [(0, 2.4, "Los nuevos frenan en [80%]"), (2.4, 4.8, "y completan justo"),
                      (4.8, T, "antes de que te [despiertes]")])

def s5(ctx, t, T):  # CALOR = ENEMIGO
    background(ctx, t, "malo")
    heat = ease_in_out(prog(t, 2, 4))
    phone_lying(ctx, 540, 1470, .8, t, .7, heat=heat)
    py = 1340 - (1 - ease_out(prog(t, 2.2, .5))) * 1100
    pillow(ctx, 540, py, 1.0, t)
    if heat > .05: heat_waves(ctx, t, 540, 1150, 420, n=4, a=.7 * heat)
    thermometer(ctx, 120, 860, 1250, heat, alpha=prog(t, .2, .4))
    badge(ctx, 880, 900, 70, prog(t, 5, .4), ok=False)
    captions(ctx, t, [(0, 2.4, "El enemigo real: el [CALOR]"), (2.4, 5, "bajo la [almohada]"), (5, T, "eso [sí] la daña")])

def s6(ctx, t, T):  # REVELACIÓN: dónde cargarlo
    background(ctx, t, "bueno")
    ya = slide_in(t, 0, .5); yb = slide_in(t, .2, .5)
    ctx.set_source(hgrad(100, 500, (.35, .2, .1), (.6, .4, .22))); rrect(ctx, 100, 1420 + ya, 400, 40, 10); ctx.fill()
    phone(ctx, 300, 1215 + ya, .55, t, 1.0, charging=False, cable_on=False)
    phone_lying(ctx, 790, 1400 + yb, .48, t, .8, heat=.7)
    pillow(ctx, 790, 1330 + yb, .6, t)
    heat_waves(ctx, t, 790, 1230 + yb, 220, n=3, a=.5)
    badge(ctx, 300, 900, 62, prog(t, .6, .4), ok=True)
    badge(ctx, 790, 1000, 62, prog(t, .9, .4), ok=False)
    label(ctx, "superficie dura", 300, 1560, 44, alpha=prog(t, 1, .3), bg=OK_BG)
    label(ctx, "almohada", 790, 1560, 44, alpha=prog(t, 1.2, .3), bg=BAD_BG)
    captions(ctx, t, [(0, 2.4, "Cargalo [tranquilo]"), (2.4, T, "sobre algo [duro]")])

def s7(ctx, t, T):  # CTA
    background(ctx, t, "cierre")
    cy = 1230 + 20 * math.sin(t * 2.5)
    glow(ctx, 540, cy, 520, a=.18 + .06 * math.sin(t * 4))
    phone(ctx, 540, cy, .9, t, 1.0, charging=False)
    captions(ctx, t, [(0, 1.9, "Mandáselo a quien"), (1.9, T, "se levanta a [desenchufarlo]")], y=420, size=96)

SCENES = [
    dict(name="s1_gancho", draw=s1, dur=4.8, voz="Tu batería se gasta… y no es por cargarla toda la noche.", check=2.5),
    dict(name="s2_regancho", draw=s2, dur=3.0, voz="Y no es lo que pensás.", check=2.0),
    dict(name="s3_corta", draw=s3, dur=7.0, voz="Al llegar al 100 por ciento, el celu corta la carga solo: lo controla un chip.", check=6.0),
    dict(name="s4_80", draw=s4, dur=7.5, voz="Y los celulares nuevos frenan en 80 por ciento y completan justo antes de que te despiertes.", check=6.5),
    dict(name="s5_calor", draw=s5, dur=7.5, voz="El verdadero enemigo es el calor: cargarlo bajo la almohada o con funda gruesa sí la daña.", check=6.0),
    dict(name="s6_donde", draw=s6, dur=5.0, voz="Así que cargalo tranquilo, pero sobre algo duro y ventilado.", check=4.0),
    dict(name="s7_cta", draw=s7, dur=4.0, voz="Mandáselo a quien se levanta a desenchufar el celu.", check=3.0),
]

if __name__ == "__main__":
    make_video("cargar-de-noche", "¿Cargar el celu toda la noche arruina la batería?", SCENES)
