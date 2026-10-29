"""Builds the art for scene 4 (paths through the dark).

    python -I build_scene4.py <package dir>

Writes Art4Passage.txt and Art4Sprites.txt: Hans's shipping passage through the caves with its haul line, glowing
cyan mushrooms and painted arrows, and the Hunter with his whip.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_scene1 import (Grid, Exporter, frames_of, mirror, edge_line, ribs, stipple, edge_glyph, FAR, BACK, MIDG,
                          GROUND, NEAR, CHAR, TEX, FARC, ROCKC, DIMC)
from build_scene3 import crop
import controller_frames as CTRLF

CYAN = "#7fe3de"           # the tier: the Hunter's whip, the mushrooms' light
CYAN_DIM = "#3f7f7b"       # painted arrows, mushroom stalks lit from above
STALK = "#64706e"
ROPE = "#8a7a60"           # hemp
WOOD = "#6e6a62"
CRATE = "#8f8064"
CHESTC = "#a08a64"         # the Giant chest's wood, like the Humble's
STONE = "#b8b4aa"          # plain stone gear
CLOAK = "#02e5ff"          # the Hunter. the game tints foes in their tier color, cyan at 6-10 stars

# world size in cells. the floor band is scene 1's (back edge, feet, front edge)
WW, WH = 200, 40
BACK_EDGE, FLOOR, FRONT_EDGE = 23, 26, 29
HOLE = (19, 29)                     # the chimney opening in the floor, x0 to x1
PULLEYS = (40, 104, 168)            # where the haul line hangs from the ceiling
ROPE_ROW = 9                        # line height at a pulley, it sags between
CHEST_X = 104                       # Giant chest's left edge
MUSHROOMS = ((34, 23), (52, 22), (78, 23), (118, 23), (131, 22), (160, 23), (186, 22))
ARROWS = ((30, 16), (88, 15), (146, 16))
FISSURES = ((66, 9), (140, 8))
MID_SPLIT = 100


def ceiling(x):
    return 4 + int(round(1.4 * math.sin(x * 0.11) + 0.9 * math.sin(x * 0.27 + 1)))


def rope_y(x):
    """The haul line's row at x: up at each pulley, sagging most halfway between."""
    xs = sorted(PULLEYS)
    if x <= xs[0]:
        u = 1 - min(1.0, (xs[0] - x) / 40)
        return ROPE_ROW + 2.2 * math.sin(math.pi * (0.5 + 0.5 * u))
    if x >= xs[-1]:
        u = min(1.0, (x - xs[-1]) / 40)
        return ROPE_ROW + 2.2 * math.sin(math.pi * 0.5 * u)
    for a, b in zip(xs, xs[1:]):
        if a <= x <= b:
            return ROPE_ROW + 2.2 * math.sin(math.pi * (x - a) / (b - a))


def mushrooms(g, x, base, r):
    """A clump of glowing mushrooms: caps lit cyan, pale stalks."""
    caps = [(0, 2, ".-."), (3, 1, "o"), (5, 3, ".--."), (9, 1, ".")]
    for dx, h, cap in caps[: r.randint(2, 4)]:
        g.text(x + dx, base - h, cap, CYAN)
        for k in range(1, h):
            g.set(x + dx + len(cap) // 2, base - h + k, "|", STALK)
    g.text(x - 1, base + 1, r.choice(("`'.,", ".,'`.", "'.,")), CYAN_DIM)


def build_passage4():
    r = random.Random(97)
    mid = Grid(WW, WH)

    # fissures in the back wall, onto the cave beyond
    def in_fissure(x, y):
        for fx, fw in FISSURES:
            top, bot = ceiling(fx) + 4, BACK_EDGE - 2
            if top <= y <= bot:
                hw = fw / 2 * (0.4 + 0.6 * (y - top) / (bot - top)) + math.sin(y * 1.3 + fx) * 0.7
                if abs(x - fx) < hw:
                    return True
        return False

    # dim back wall
    for y in range(0, BACK_EDGE):
        mid.blank(0, y, WW - 1, y, TEX)
        for x in range(WW):
            h = y + 1.1 * math.sin(x * 0.07 + (y // 5) * 2.3) + 0.5 * math.sin(x * 0.19 + y // 5)
            p = r.random()
            if int(math.floor(h)) % 6 == 0 and p < 0.22:
                sub = h - math.floor(h)
                mid.set(x, y, "'" if sub < 0.34 else ("-" if sub < 0.67 else "_"), TEX)
            elif p < 0.02:
                mid.set(x, y, r.choice(".'`,:"), TEX)
    for x in range(WW):
        c = ceiling(x)
        dy = ceiling(x + 1) - c
        mid.set(x, c, "_" if dy == 0 else ("\\" if dy > 0 else "/"), MIDG)
        for y in range(c + 1, BACK_EDGE):
            if in_fissure(x, y):
                mid.c[y][x] = None
    for fx, fw in FISSURES:
        top, bot = ceiling(fx) + 4, BACK_EDGE - 2
        for y in range(top, bot + 1):
            xs = [x for x in range(fx - fw, fx + fw) if in_fissure(x, y)]
            if xs:
                mid.set(xs[0] - 1, y, r.choice("/(|"), MIDG)
                mid.set(xs[-1] + 1, y, r.choice("\\)|"), MIDG)
    # stalactites from the ceiling
    for sx in (12, 58, 96, 124, 178):
        c = ceiling(sx)
        n = r.randint(2, 4)
        for k in range(n):
            w = max(0, (n - k) // 2)
            mid.set(sx - w - 1, c + 1 + k, "\\", MIDG)
            mid.set(sx + w + 1, c + 1 + k, "/", MIDG)
            mid.blank(sx - w, c + 1 + k, sx + w, c + 1 + k, TEX)
        mid.set(sx, c + 1 + n, "V" if n > 1 else "'", MIDG)
    # painted arrows along the route
    for ax, ay in ARROWS:
        mid.text(ax, ay, "-->", CYAN_DIM)
        mid.text(ax - 1, ay + 1, "'", CYAN_DIM)

    # haul line: brackets, a pulley on each, the line sagging between
    for px in PULLEYS:
        for y in range(ceiling(px) + 1, ROPE_ROW - 1):
            mid.set(px, y, "|", WOOD)
        mid.text(px - 1, ROPE_ROW - 1, "/|\\", WOOD)
        mid.text(px - 1, ROPE_ROW, "(o)", DIMC)
    prev = None
    for x in range(WW):
        y = rope_y(x)
        row = int(math.floor(y))
        sub = y - row
        if mid.get(x, row) in ("(", "o", ")"):
            continue
        mid.set(x, row, "-" if sub < 0.5 else "_", ROPE)

    # floor grit, darker toward the back, mushrooms along the back edge
    ramp = {23: "#444444", 24: "#444444", 25: "#4e4e4e", 26: "#585858", 27: "#585858", 28: "#626262"}
    for y in range(BACK_EDGE, FRONT_EDGE):
        for x in range(WW):
            if mid.c[y][x] is None:
                mid.blank(x, y, x, y, TEX)
                p = r.random()
                if y == BACK_EDGE and p < 0.55:
                    mid.set(x, y, r.choice("_.-,'"), ramp[y])
                elif y > BACK_EDGE and p < 0.05:
                    mid.set(x, y, r.choice(".,'`"), ramp[y])
                elif y > BACK_EDGE and p < 0.062:
                    mid.set(x, y, r.choice("o°"), ramp[y])
    for mx, my in MUSHROOMS:
        mushrooms(mid, mx, my, r)
    edge_line(mid, 0, WW - 1, FRONT_EDGE, r, GROUND)
    for y in range(FRONT_EDGE + 1, WH):
        mid.blank(0, y, WW - 1, y, TEX)
    ribs(mid, 0, WW - 1, FRONT_EDGE + 1, 3, r, MIDG)

    # the hole he climbs out of. near lip is solid so he's hidden below it
    h0, h1 = HOLE
    lip = Grid(h1 - h0 + 3, 7)
    for y in range(24, WH):
        a = h0 + max(0, 24 - y + 1)
        b = h1 - max(0, 24 - y + 1)
        mid.blank(a, y, b, y, TEX)
    mid.text(h0, 24, "\\" + "_" * (h1 - h0 - 1) + "/", MIDG)
    for x in range(h0 + 1, h1):
        if r.random() < 0.3:
            mid.set(x, 25, r.choice(".'`"), TEX)
    lip_rows = ["`-.__.-'¯¯`-.", " ' :  . ' : ", "  .  '  .  ", "", "", "", ""]
    for j in range(7):
        lip.blank(0, j, lip.w - 1, j, TEX)
    for j, row in enumerate(lip_rows):
        lip.text(0, j, row, GROUND if j == 0 else TEX)

    # far: the cave beyond the fissures, with distant mushrooms
    far = Grid(150, WH)
    for y in range(far.h):
        for x in range(far.w):
            p = r.random()
            if (y * 2 + x // 9) % 7 == 0 and p < 0.16:
                far.set(x, y, r.choice("-_'"), FAR)
            elif p < 0.01:
                far.set(x, y, r.choice(".'`"), FAR)
    for fx in range(6, far.w, 17):
        far.text(fx, 19 + (fx * 7) % 4, r.choice(("o", ".o.", "°")), CYAN_DIM)
    edge_line(far, 0, far.w - 1, 21, r, "#3a3a3a")

    # near: hourglass columns (stalactite meets stalagmite) and rocks
    front = Grid(270, WH)

    def column(x, half):
        for y in range(0, WH):
            # narrowest in the middle, flaring to the ceiling and the floor
            w = 1 + int(round(half * abs(y - 15) / 15))
            a = x - w + int(round(0.7 * math.sin(y * 0.5 + x)))
            b = x + w + int(round(0.7 * math.sin(y * 0.41 + x * 0.3)))
            front.blank(a, y, b, y, TEX)
            la = x - (1 + int(round(half * abs(y - 1 - 15) / 15))) + int(round(0.7 * math.sin((y - 1) * 0.5 + x)))
            lb = x - (1 + int(round(half * abs(y + 1 - 15) / 15))) + int(round(0.7 * math.sin((y + 1) * 0.5 + x)))
            ra = x + (1 + int(round(half * abs(y - 1 - 15) / 15))) + int(round(0.7 * math.sin((y - 1) * 0.41 + x * 0.3)))
            rb = x + (1 + int(round(half * abs(y + 1 - 15) / 15))) + int(round(0.7 * math.sin((y + 1) * 0.41 + x * 0.3)))
            front.set(a, y, edge_glyph(la, a, lb, True), NEAR)
            front.set(b, y, edge_glyph(ra, b, rb, False), MIDG)
            t = a + int(round((b - a) * 0.62))
            if a < t < b:
                front.set(t, y, "┊", MIDG)
            for xx in range(t + 1, b):
                if r.random() < 0.55:
                    front.set(xx, y, r.choice(":.'"), TEX)

    for cx_, half in ((8, 3), (76, 3), (160, 3)):
        column(cx_, half)
    for rx in (40, 150, 226):
        front.solid(rx, WH - 4, ["    /\\  _", "  _/ :`-' `._", "_/ ,  :  '   `\\", "  .  '  :   .  `-._"], NEAR)
    return far, mid, lip, front


def build_sprites(ex):
    # the game's Giant chest: shut, opening, open, emptied
    giant = [[" ___ ", "╞╤8╤╡", "└┴─┴┘"], ["┌-─-┐", "╞╤8╤╡", "└┴─┴┘"], [" ___ ", "│```│", "┌┬.┬┐", "└┴─┴┘"],
             ["", "", "┌┬.┬┐", "└┴─┴┘"]]
    giant = [[""] * (4 - len(f)) + f for f in giant]
    ex.piece("giant", frames_of(giant, CHESTC, {"8": "#d8d0b0"}))
    # the heart that rises out of it, with a spark
    ex.piece("heart", frames_of([["", "  ♥  ", ""], [" .|, ", "- ♥ -", " '|` "]], "#e8e8e8"))
    # plain stone gear, lying on the ground: sword, shield, crossbow, wand, quarterstaff, runestone
    ex.piece("item", frames_of([["─┼"], ["(o)"], ["<╪─"], ["─*"], ["═══"], ["(φ)"]], STONE))
    # trolley on the haul line, and a crate on it
    ex.piece("trolley", frames_of([["(o)", " │ ", " │ "]], DIMC))
    ex.piece("crate", frames_of([[" (o) ", "  │  ", "┌─┴─┐", "│≡≡≡│", "└───┘"]], CRATE, {"(": DIMC, "o": DIMC, ")": DIMC}))
    # the Hunter, robed like the game's cultists: four steps then standing, mirrored to face right.
    # the whip is drawn on its own, but the frames keep its width so he doesn't shift
    width = max(len(r) for f in CTRLF.HUNTER for r in f)
    hunter = [[r.ljust(width) for r in f] for f in CTRLF.HUNTER_BARE + [CTRLF.HUNTER_BARE[0]]]

    g = frames_of(hunter, CLOAK)
    # fill in the robe (first six columns) so nothing shows through
    for gr in g:
        for y in range(1, gr.h):
            xs = [x for x in range(6) if gr.c[y][x]]
            for x in range(xs[0], xs[-1] + 1) if xs else ():
                if gr.c[y][x] is None:
                    gr.c[y][x] = (" ", CLOAK)
    ex.piece("hunterR", mirror(g))
    # one-color silhouette, the scene tints it as he comes into the light
    shade = []
    for m in mirror(g):
        s = Grid(m.w, m.h)
        for y in range(m.h):
            for x in range(m.w):
                if m.c[y][x]:
                    s.c[y][x] = (m.c[y][x][0], CLOAK)
        shade.append(s)
    ex.piece("hunterS", shade)
    ex.value("hunterHandX", width - 1 - CTRLF.HUNTER_HAND[0])
    ex.value("hunterHandY", CTRLF.HUNTER_HAND[1])
    # his whip dragging behind him, barbs every other cell. two sets a cell apart so the scene can
    # always line the barbs up with their marks
    import whips
    drag = []
    for p in (0, 1):
        dg, dox, doy, reach = whips.drag(n=14, speed=0.42, hand_y=-1.0, col=CLOAK, barbs=(p, CLOAK), dir=1)
        drag += dg
    ex.piece("drag", drag)
    ex.value("dragN", len(dg))
    ex.value("dragOX", dox)
    ex.value("dragOY", doy)
    ex.value("dragReach", reach)
    # fresh marks the barbs score in the rock
    ex.piece("mark", frames_of([["x_"]], CYAN))


def main():
    pkg = sys.argv[1]
    os.makedirs(pkg, exist_ok=True)
    head = "// Generated by tools/build_scene4.py. Don't edit by hand; change the script and rebuild.\n"

    far, mid, lip, front = build_passage4()
    ex = Exporter(head)
    ex.value("floor", FLOOR)
    ex.value("backEdge", BACK_EDGE)
    ex.value("holeX0", HOLE[0])
    ex.value("holeX1", HOLE[1])
    ex.value("chestX", CHEST_X)
    ex.value("midSplit", MID_SPLIT)
    ex.value("ropeY", [round(rope_y(x), 2) for x in range(WW)])
    ex.value("mushX", [x + 2 for x, _ in MUSHROOMS])
    ex.value("mushY", [y - 1 for _, y in MUSHROOMS])
    ex.piece("far", [far])
    ex.piece("midL", [crop(mid, 0, 0, MID_SPLIT, WH)])
    ex.piece("midR", [crop(mid, MID_SPLIT, 0, WW - MID_SPLIT, WH)])
    ex.piece("lip", [lip])
    ex.piece("front", [front])
    n1 = ex.write(os.path.join(pkg, "Art4Passage.txt"))

    ex = Exporter(head)
    build_sprites(ex)
    n2 = ex.write(os.path.join(pkg, "Art4Sprites.txt"))
    print(f"Art4Passage {n1}, Art4Sprites {n2} bytes")


if __name__ == "__main__":
    main()
