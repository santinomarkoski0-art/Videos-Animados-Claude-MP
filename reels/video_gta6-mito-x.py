from motor import *
from functools import partial
import importlib
g = importlib.import_module("video_gta6-correr")
vice_bg, controller, runner, x_pos, tap, ring, SYM = g.vice_bg, g.controller, g.runner, g.x_pos, g.tap, g.ring, g.SYM

def stamp(ctx, t, start, x, y, text="MITO"):
    p = prog(t, start, .3)
    if p <= 0: return
    s = max(.02, 2.2 - 1.2 * ease_out(p))
    ctx.save(); ctx.translate(x, y); ctx.rotate(-.18); ctx.scale(s, s)
    font(ctx, 110); e = ctx.text_extents(text); w, h = e.x_advance + 70, 150
    ctx.set_source_rgba(*RED, .9 * p); ctx.set_line_width(12); rrect(ctx, -w / 2, -h / 2, w, h, 20); ctx.stroke()
    ctx.move_to(-e.x_advance / 2, 40); ctx.show_text(text); ctx.new_path(); ctx.restore()

def s1(ctx, t, T):  # GANCHO mito
    vice_bg(ctx, t)
    hook_title(ctx, t, [("“En GTA 6 se corre", 80), ("con la [X]", 124), ("como siempre”", 84)])
    cy = 1420 + slide_in(t, .2, .6, 900)
    p = tap(t)
    controller(ctx, 540, cy, 1.0, t, x=(p, .5 + .5 * p))
    xx, xy = x_pos(540, cy, 1.0); ring(ctx, xx, xy, t, color=SYM["x"])
    stamp(ctx, t, 2.8, 540, 960)

def s2(ctx, t, T):
    vice_bg(ctx, t)
    z = 1 + .25 * ease_in_out(prog(t, 0, T))
    ctx.save(); ctx.translate(540, 1300); ctx.scale(z, z); ctx.translate(-540, -1300)
    controller(ctx, 540, 1300, 1.0, t, x=(0, .6), l3=(0, .6))
    ctx.restore()
    captions(ctx, t, [(0, 1.5, "[Spoiler]:"), (1.5, T, "cambió, y [mucho]")])

def s7(ctx, t, T):
    vice_bg(ctx, t, "cierre")
    runner(ctx, 540, 1300, 1.1, t, "jump")
    captions(ctx, t, [(0, 2.3, "Mandáselo al que"), (2.3, T, "sigue [saltando]")], y=420, size=96)

SCENES = [
    dict(name="s1_gancho", draw=s1, dur=4.8, voz="En GTA 6 se corre con la X, como siempre… ¿seguro?", check=3.6),
    dict(name="s2_regancho", draw=s2, dur=3.2, voz="Spoiler: cambió, y mucho.", check=2.4),
    dict(name="s3_x", draw=partial(g.scene_x, caps=[(0, 2.0, "Apretás [X] sin parar"), (2.0, 4.0, "y tu personaje…"), (4.0, 6.0, "[salta]")]),
         dur=6.0, voz="Si apretás X sin parar, tu personaje no corre: salta.", check=4.6),
    dict(name="s4_l3", draw=partial(g.scene_l3, caps=[(0, 2.0, "Ahora correr es"), (2.0, 4.2, "hundir el [stick izquierdo]"), (4.2, 6.5, "o sea, [L3]")]),
         dur=6.5, voz="En el control nuevo, correr es hundir el stick izquierdo: L3.", check=5.0),
    dict(name="s5_clasico", draw=partial(g.scene_clasico, caps=[(0, 2.4, "¿No te [acostumbrás]?"), (2.4, 4.6, "Ajustes: modo [Clásico]"), (4.6, 7.0, "y la X vuelve a [correr]")]),
         dur=7.0, voz="Si no te acostumbrás, en Ajustes poné el modo Clásico y la X vuelve a correr.", check=5.0),
    dict(name="s6_markpoint", draw=partial(g.scene_markpoint, caps=[(0, 2.4, "Para jugarlo [en serio]"), (2.4, 4.8, "el mejor PS5 [original]"), (4.8, 7.0, "está en [MARKPOINT]")]),
         dur=7.0, voz="Y para jugarlo en serio: el mejor joystick de PS5 original está en Markpoint.", check=5.5),
    dict(name="s7_cta", draw=s7, dur=4.8, voz="Mandáselo a tu amigo que sigue saltando en vez de correr.", check=3.5),
]

if __name__ == "__main__":
    make_video("gta6-mito-x", "Mito: en GTA 6 se corre con la X", SCENES)
