"""Builds the art for scene 3 (the World Fountain).

    python -I build_scene3.py <package dir>

Writes Art3Fountain.txt and Art3Sprites.txt, with build_scene1.py's format, helpers and grays. The crystals are lit
white and drawn like the game's Ki crystals.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_scene1 import (Grid, Exporter, frames_of, mirror, edge_line, ribs, stipple, edge_glyph, FAR, BACK, MIDG,
                          GROUND, NEAR, CHAR, TEX, FARC, ROCKC)

# the crystal's and the Ki's whites, and the pool it stands in
CRYS_HI = "#eef3f8"        # lit edges and the ridge
CRYS_EDGE = "#a9b4be"      # the shadowed edge
CRYS_LIT = "#87939e"       # marks on the face toward us
CRYS_DARK = "#525c66"      # marks on the face turned away
CRYS_FAR = "#3a4148"       # crystals far off in the dark
KI = "#f2f7ff"
WATER = "#8a9cae"
WATER_DIM = "#4e5a66"
STEEL = "#c9d1d6"

# the world in cells. the floor band is the passage's (back edge, his feet, front edge) 63 rows down, at the bottom
# of a shaft too tall to see the top of
WW, WH = 200, 100
BACK_EDGE, FLOOR, FRONT_EDGE = 86, 89, 92
CRYSTAL = (58, 16, 52)                  # the World Fountain: x of its point, half-width, row its sides go straight
LESSER = ((20, 5, 78),)                 # a lesser crystal off to one side, the same way
LEANING = ((45, 10, 4, -1), (72, 13, 5, 1))   # crystals growing aslant out of its foot: x at the floor, length,
                                              # width, which way they lean (-1 left, 1 right)
POOL = (54, 87, (20, 28, 32, 28, 20))   # the pool round its foot: center x, top row, half-width of each row
LAND_X = 34                             # where he comes down (his head's column)
LEFT_WALL = 6                           # the shaft's walls
RIGHT_WALL = 112
CLEFT = (130, 148)                      # the chimney in the right wall that the Ki rises up
CLEFT_TOP = 6
MID_SPLIT = 100                         # the cavern is exported in two halves, split here
# up the chimney, ledge by ledge: where his head is and the row his feet are on when he stands on each one
LEDGES = [(142 if k % 2 else 134, FLOOR - 5 * k) for k in range(1, 16)]
CLUSTERS = ((12, 87), (29, 86), (99, 87), (106, 86), (122, 87), (153, 86), (168, 87), (186, 86))
GLINTS = ((30, 84), (100, 85), (107, 84), (154, 84))  # where light catches the small crystals


def crystal(g, cx, hw, shoulder, base, r, cols=(CRYS_HI, CRYS_EDGE, CRYS_LIT, CRYS_DARK), bands=True):
    """A crystal from the front: a Ki crystal's /\\ point on a straight column, a ridge splitting the lit face
    (streaks, a few fractures) from the face turning away (stipple). Solid, it hides what's behind it."""
    hi, edge, lit, dark = cols
    tip = shoulder - hw
    rdx = max(1, hw // 5)
    prev = cx
    marks = {}
    for x in range(cx - hw, cx + rdx):
        if r.random() < (0.18 if bands else 0.15):
            y = tip + r.randint(0, hw)
            while y < base - 1:
                n = r.randint(3, 9)
                for k in range(n):
                    marks[(x, y + k)] = ("'" if k == 0 else ("." if k == n - 1 else "|"), lit)
                y += n + r.randint(5, 16)
    if bands:
        # shine: light off the glass, in pairs of short slants down across the face toward us
        for sy in (shoulder + 3, shoulder + 16, base - 13):
            for k in range(min(9, hw)):
                marks[(cx - hw + 1 + k, sy + k)] = ("\\", hi)
                if 2 <= k < 7:
                    marks[(cx - hw + 3 + k, sy + k - 2)] = ("\\", edge)
    for y in range(tip, base + 1):
        if y < shoulder:
            k = y - tip
            xl, xr = cx - k - 1, cx + k
        else:
            xl, xr = cx - hw - 1, cx + hw
        g.blank(xl + 1, y, xr - 1, y, dark)
        g.set(xl, y, "/" if y < shoulder else "|", hi)
        g.set(xr, y, "\\" if y < shoulder else "|", edge)
        if y < tip + 1:
            continue
        u = min(1.0, (y - tip) / max(1, shoulder - tip))
        rx = int(round(cx + rdx * u))
        g.set(rx, y, "\\" if rx > prev else "|", hi)
        prev = rx
        # the face toward us
        for x in range(xl + 1, rx):
            if (x, y) in marks:
                g.set(x, y, *marks[(x, y)])
            elif x == xl + 1 and r.random() < 0.3:
                g.set(x, y, "'", lit)
            elif r.random() < 0.02:
                g.set(x, y, r.choice(".'·"), lit)
        # the face turning away
        for x in range(rx + 1, xr):
            p = 0.12 + 0.55 * (x - rx) / max(1, xr - rx)
            if r.random() < p:
                g.set(x, y, r.choice(":.'" if x < xr - 1 else "::|"), dark)
    # its foot, broken off into small crystals and grit
    for x in range(cx - hw - 3, cx + hw + 4):
        if g.get(x, base) == " " and r.random() < 0.5:
            g.set(x, base, r.choice("._,'"), lit)


def leaning_crystal(g, x, base, length, width, lean, r, cols=(CRYS_HI, CRYS_EDGE, CRYS_LIT, CRYS_DARK)):
    """A crystal growing out of the ground at 45 degrees, a ridge down it, its point where the upper side meets the
    lower one going straight up. Solid."""
    hi, edge, lit, dark = cols
    side = "/" if lean > 0 else "\\"
    near, far = (0, width) if lean > 0 else (width, 0)
    for i in range(length + width + 1):
        y = base - i
        x0 = x + lean * min(i, length)
        a, b = x0, x0 + width
        if i > length:
            # the point: the upper side keeps going, the lower one stands straight
            k = i - length
            if lean > 0:
                a = x0 + k
            else:
                b = x0 + width - k
            if a >= b:
                g.set(a if lean > 0 else b, y, side, hi)
                break
        g.blank(a + 1, y, b - 1, y, dark)
        g.set(a, y, side if (lean > 0 or i <= length) else "|", hi if lean > 0 else edge)
        g.set(b, y, side if (lean < 0 or i <= length) else "|", edge if lean > 0 else hi)
        m = (a + b) // 2
        if a < m < b and i <= length:
            g.set(m, y, side, lit)
            for xx in (range(m + 1, b) if lean > 0 else range(a + 1, m)):
                if r.random() < 0.4:
                    g.set(xx, y, r.choice(":.'"), dark)


def small_crystals(g, x, base, r, cols=(CRYS_HI, CRYS_EDGE, CRYS_LIT)):
    """A cluster of two to four little crystals growing out of the ground, like the game's Ki crystals."""
    hi, edge, lit = cols
    n = r.randint(2, 4)
    xs = sorted(r.sample(range(0, 7), n))
    for i, dx in enumerate(xs):
        h = r.randint(1, 3)
        cx = x + dx
        g.set(cx, base - h, "/", hi)
        g.set(cx + 1, base - h, "\\", edge)
        for k in range(1, h + 1):
            g.set(cx, base - h + k, "|", hi)
            g.set(cx + 1, base - h + k, "|", edge)
    g.text(x - 1, base + 1, r.choice(("`'.", ".'`,", "'.,")), lit)


def rock_face(g, x0, x1, y0, y1, r, edge_left=None, edge_right=None):
    """Solid rock with strata across it, cracks down it and grit, darker toward a side edge that turns away."""
    for y in range(y0, y1 + 1):
        a = x0 if edge_left is None else edge_left(y)
        b = x1 if edge_right is None else edge_right(y)
        if b < a:
            continue
        g.blank(a, y, b, y, TEX)
        for x in range(a, b + 1):
            # strata: lines wandering across the rock every few rows
            h = y + 1.1 * math.sin(x * 0.07 + (y // 5) * 2.3) + 0.5 * math.sin(x * 0.19 + y // 5)
            sub = h - math.floor(h)
            p = r.random()
            if int(math.floor(h)) % 5 == 0 and p < 0.4:
                g.set(x, y, "'" if sub < 0.34 else ("-" if sub < 0.67 else "_"), ROCKC if p < 0.12 else TEX)
            elif p < 0.02:
                g.set(x, y, r.choice("|!:"), TEX)
            elif p < 0.05:
                g.set(x, y, r.choice(".'`,"), TEX)


def crop(g, x0, y0, w, h):
    out = Grid(w, h)
    for y in range(h):
        for x in range(w):
            if 0 <= y0 + y < g.h and 0 <= x0 + x < g.w:
                out.c[y][x] = g.c[y0 + y][x0 + x]
    return out


def wavy(base, amp, freq, phase):
    return lambda y: base + int(round(amp * math.sin(y * freq + phase) + 0.3 * math.sin(y * freq * 2.7 + phase)))


def build_fountain():
    r = random.Random(83)
    mid = Grid(WW, WH)

    # the shaft's walls, rising out of sight; their edges catch a little of the light
    left_edge = wavy(LEFT_WALL, 1.4, 0.12, 0.5)
    rock_face(mid, 0, 0, 0, BACK_EDGE - 1, r, edge_right=left_edge)
    for y in range(0, BACK_EDGE):
        e = left_edge(y)
        mid.set(e, y, edge_glyph(left_edge(y - 1), e, left_edge(y + 1), False), GROUND)
        for d in range(1, 4):
            stipple(mid, e - d, y, d, TEX, r)
    right_edge = wavy(RIGHT_WALL, 1.8, 0.1, 1.9)

    def right_from(y):
        # the wall's foot flares out onto the floor
        return right_edge(y) - max(0, y - (BACK_EDGE - 6)) * 2

    rock_face(mid, 0, WW - 1, 0, BACK_EDGE - 1, r, edge_left=right_from)
    for y in range(0, BACK_EDGE):
        e = right_from(y)
        mid.set(e, y, edge_glyph(right_from(y - 1), e, right_from(y + 1), True), GROUND)
        for d in range(1, 4):
            stipple(mid, e + d, y, d, ROCKC, r)

    # the chimney the Ki rises up: open from the floor to out of sight, a dim back wall inside, ledges up it
    c0, c1 = CLEFT
    cl = wavy(c0, 0.9, 0.15, 0.2)
    cr = wavy(c1, 0.9, 0.13, 2.4)
    for y in range(CLEFT_TOP - 6, BACK_EDGE):
        a, b = cl(y), cr(y)
        mid.blank(a + 1, y, b - 1, y, TEX)
        for x in range(a + 1, b):
            if r.random() < 0.015:
                mid.set(x, y, r.choice(".'`"), TEX)
        mid.set(a, y, edge_glyph(cl(y - 1), a, cl(y + 1), False), GROUND)
        mid.set(b, y, edge_glyph(cr(y - 1), b, cr(y + 1), True), GROUND)
        for d in range(1, 3):
            stipple(mid, a - d, y, d, TEX, r)
    for k, (hx, feet) in enumerate(LEDGES):
        y = feet + 1
        # a shelf of rock out of one wall: its top just under his feet, its underside sloping back into the wall
        top = "".join(r.choice("¯¯¯¯-'") for _ in range(12))
        if hx > (c0 + c1) // 2:
            a, b = hx - 3, cr(y)
            mid.set(a, y, ".", NEAR)
            mid.text(a + 1, y, top[: b - a - 1], NEAR)
            for j, dx in enumerate((1, 3, 5)):
                if a + dx < b:
                    mid.blank(a + dx + 1, y + 1 + j, b - 1, y + 1 + j, TEX)
                    mid.text(a + dx, y + 1 + j, "\\" if j == 0 else "`-", MIDG)
                    if a + dx + 3 < b and r.random() < 0.6:
                        mid.set(a + dx + 3, y + 1 + j, r.choice(":.'"), ROCKC)
        else:
            a, b = cl(y), hx + 4
            mid.text(a + 1, y, top[: b - a - 1], NEAR)
            mid.set(b, y, ".", NEAR)
            for j, dx in enumerate((1, 3, 5)):
                if b - dx > a:
                    mid.blank(a + 1, y + 1 + j, b - dx - 1, y + 1 + j, TEX)
                    mid.text(b - dx - (0 if j == 0 else 1), y + 1 + j, "/" if j == 0 else "-´", MIDG)
                    if b - dx - 3 > a and r.random() < 0.6:
                        mid.set(b - dx - 3, y + 1 + j, r.choice(":.'"), ROCKC)

    # the World Fountain, and two lesser crystals at its feet
    cx, hw, sh = CRYSTAL
    for lx, lhw, lsh in LESSER:
        crystal(mid, lx, lhw, lsh, BACK_EDGE, r)
    for lx, ln, lw, lean in LEANING:
        leaning_crystal(mid, lx, BACK_EDGE, ln, lw, lean, r)
    crystal(mid, cx, hw, sh, BACK_EDGE, r)

    # the floor: grit and small crystals, darker toward the back; its front edge a ledge over the dark
    ramp = {86: "#484848", 87: "#484848", 88: "#484848", 89: "#5e5e5e", 90: "#5e5e5e", 91: "#5e5e5e"}
    for x in range(WW):
        if mid.get(x, BACK_EDGE) == " " and mid.c[BACK_EDGE][x] is None and r.random() < 0.6:
            mid.set(x, BACK_EDGE, r.choice("_.-,'"), ramp[BACK_EDGE])
    for y in range(BACK_EDGE, FRONT_EDGE):
        for x in range(WW):
            if mid.c[y][x] is None:
                mid.blank(x, y, x, y, TEX)
                p = r.random()
                if y > BACK_EDGE and p < 0.05:
                    mid.set(x, y, r.choice(".,'`"), ramp[y])
                elif y > BACK_EDGE and p < 0.062:
                    mid.set(x, y, r.choice("o°"), ramp[y])
    for x, y in CLUSTERS:
        small_crystals(mid, x, y, r)
    edge_line(mid, 0, WW - 1, FRONT_EDGE, r, GROUND)
    for y in range(FRONT_EDGE + 1, WH):
        mid.blank(0, y, WW - 1, y, TEX)
    ribs(mid, 0, WW - 1, FRONT_EDGE + 1, 3, r, MIDG)
    for y in range(FRONT_EDGE + 4, WH):
        for x in range(WW):
            if r.random() < 0.012:
                mid.set(x, y, r.choice(".`'"), TEX)

    # the pool round its foot: still water, the crystal's light lying in it
    pcx, ptop, widths = POOL
    pool_front = Grid(WW, WH)
    for j, w in enumerate(widths):
        y = ptop + j
        for x in range(pcx - w, pcx + w + 1):
            for g in ([mid, pool_front] if y >= FLOOR else [mid]):
                g.blank(x, y, x, y, WATER_DIM)
                p = r.random()
                if abs(x - (cx + 2)) <= hw - 3 and r.random() < 0.3:
                    g.set(x, y, r.choice("|:'") if (x - cx) % 3 else ":", CRYS_LIT)
                elif p < 0.16:
                    g.set(x, y, r.choice("~-~_"), WATER)
                elif p < 0.24:
                    g.set(x, y, r.choice("-~"), WATER_DIM)
        for g in ([mid, pool_front] if y >= FLOOR else [mid]):
            g.set(pcx - w - 1, y, "(" if 0 < j < len(widths) - 1 else ("." if j == 0 else "`"), MIDG)
            g.set(pcx + w + 1, y, ")" if 0 < j < len(widths) - 1 else ("." if j == 0 else "´"), MIDG)

    # far: the shaft's far side in the dark, and crystals standing down at its foot, dim
    far = Grid(150, 78)
    for y in range(far.h):
        for x in range(far.w):
            p = r.random()
            if (y * 2 + x // 11) % 7 == 0 and p < 0.18:
                far.set(x, y, r.choice("-_'"), FAR)
            elif p < 0.012:
                far.set(x, y, r.choice(".'`"), FAR)
    horizon = 58
    edge_line(far, 0, far.w - 1, horizon, r, "#3a3a3a")
    for y in range(horizon + 1, far.h):
        far.blank(0, y, far.w - 1, y, FAR)
    for fx in (16, 47, 66, 101, 127):
        h = r.randint(3, 6)
        crystal(far, fx, h, horizon - r.randint(0, 3), horizon, r, cols=(CRYS_FAR, CRYS_FAR, FAR, FAR), bands=False)

    # near the camera: rock spires and crystal shards along the bottom (all solid), one tall spire
    front = Grid(240, WH)

    def spire(x, top, half, col_lit, col_dark):
        # a stalagmite: a point, then sides wandering as it widens to its foot, shaded round like the columns
        def side(y, s):
            w = min(half, 1 + (y - top) // 3)
            return x + s * w + int(round(0.8 * math.sin(y * (0.41 if s < 0 else 0.33) + x)))
        for y in range(top, WH):
            a, b = side(y, -1), side(y, 1)
            front.blank(a, y, b, y, TEX)
            front.set(a, y, edge_glyph(side(y - 1, -1), a, side(y + 1, -1), True), col_lit)
            front.set(b, y, edge_glyph(side(y - 1, 1), b, side(y + 1, 1), False), col_dark)
            t = a + int(round((b - a) * 0.6))
            if a < t < b and y > top + 1:
                front.set(t, y, "┊", MIDG)
            for xx in range(t + 1, b):
                if r.random() < 0.55:
                    front.set(xx, y, r.choice(":.'"), TEX)

    spire(140, 70, 4, NEAR, MIDG)
    spire(200, 80, 3, NEAR, MIDG)
    for fx, top in ((2, 93), (60, 95), (128, 94), (190, 93), (226, 92)):
        crystal(front, fx, 2, top + 2, WH - 1, r, cols=(NEAR, MIDG, GROUND, TEX), bands=False)
    for rx in (24, 88, 172, 206):
        front.solid(rx, WH - 4, ["    /\\  _", "  _/ :`-' `._", "_/ ,  :  '   `\\", "  .  '  :   .  `-._"], NEAR)
    return far, mid, pool_front, front


def build_sprites(ex):
    # a mote of Ki: the scene colors each one (bright near, dim far); the last frame is the game's Ki mark
    ex.piece("mote", frames_of([["·"], ["'"], ["."], ["♦"]], KI))
    # him hitting the water: a column thrown up, falling back in drops, rings left on the surface
    splash = [["", "", "    :    ", "  '.:.'  ", " ~-' '-~ "],
              ["    .    ", "  . : .  ", " '  :  ' ", "  \\ : /  ", "~-'   '-~"],
              [" .  '  . ", "'   .   '", "  .   .  ", " .     . ", "~-._ _.-~"],
              ["         ", ".       .", "  '   '  ", "         ", "~ - _ - ~"],
              ["         ", "         ", "'       '", "         ", "  ~   ~  "]]
    ex.piece("splash", frames_of(splash, KI, cmap={"~": WATER, "-": WATER, "_": WATER}))
    # the Ki surging up inside the crystal: a streak of light
    ex.piece("surge", frames_of([["'", "|", ":", "."]], "#ffffff"))
    # a ring spreading on the water, seen low
    ex.piece("ripple", frames_of([["    -    "], ["   (-)   "], ["  (   )  "], [" (     ) "], ["(       )"],
                                  ["'       '"]], WATER))
    # climbing with the sword in his belt (facing right, mirrored for left): jump, hang, forearms up, hang kicking,
    # forearms up kicking, then straining with his head at the edge (two leg poses)
    climb = [["\\O/ ", " |│ ", " /\\ "],
             ["┐ ┌ ", "\\O/ ", " |│ ", "/ \\ "],
             ["_O_ ", " |│ ", " /\\ "],
             ["┐ ┌ ", "\\O/ ", " |│ ", " |\\ "],
             ["_O_ ", " |│ ", " |\\ "],
             ["┘O└ ", " |│ ", "/ \\ "],
             ["┘O└ ", " |│ ", " |\\ "]]
    g = frames_of(climb, CHAR, {"│": STEEL})
    ex.piece("climbR", g)
    ex.piece("climbL", mirror(g))


def main():
    pkg = sys.argv[1]
    os.makedirs(pkg, exist_ok=True)
    head = "// Generated by tools/build_scene3.py. Don't edit by hand; change the script and rebuild.\n"

    far, mid, pool_front, front = build_fountain()
    ex = Exporter(head)
    ex.value("floor", FLOOR)
    ex.value("backEdge", BACK_EDGE)
    ex.value("landX", LAND_X)
    ex.value("crystalX", CRYSTAL[0])
    ex.value("crystalTip", CRYSTAL[2] - CRYSTAL[1])
    ex.value("crystalHW", CRYSTAL[1])
    ex.value("poolX0", POOL[0] - max(POOL[2]))
    ex.value("poolX1", POOL[0] + max(POOL[2]))
    ex.value("cleftX0", CLEFT[0])
    ex.value("cleftX1", CLEFT[1])
    ex.value("ledgeX", [x for x, _ in LEDGES])
    ex.value("ledgeY", [y for _, y in LEDGES])
    ex.value("glintX", [x for x, _ in GLINTS])
    ex.value("glintY", [y for _, y in GLINTS])
    ex.piece("far", [far])
    ex.value("midSplit", MID_SPLIT)
    ex.piece("midL", [crop(mid, 0, 0, MID_SPLIT, WH)])
    ex.piece("midR", [crop(mid, MID_SPLIT, 0, WW - MID_SPLIT, WH)])
    ex.piece("poolFront", [pool_front])
    ex.piece("front", [front])
    n1 = ex.write(os.path.join(pkg, "Art3Fountain.txt"))

    ex = Exporter(head)
    build_sprites(ex)
    n2 = ex.write(os.path.join(pkg, "Art3Sprites.txt"))
    print(f"Art3Fountain {n1}, Art3Sprites {n2} bytes")


if __name__ == "__main__":
    main()
