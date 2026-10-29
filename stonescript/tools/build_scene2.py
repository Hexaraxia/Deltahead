"""Builds the art for scene 2 (The Bomb Cart).

    python -I build_scene2.py <package dir>

Writes Art2Passage.txt, Art2Shaft.txt and Art2Sprites.txt, reusing build_scene1.py's helpers and passage pieces so
it's the same place.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_scene1 as s1
from build_scene1 import (Grid, Exporter, frames_of, mirror, edge_line, ribs, stipple, rails_row, rock_column, timber,
                          ceiling, edge_glyph, FAR, BACK, MIDG, GROUND, NEAR, CHAR, TEX, RAILC, TIEC, CART, CARGO, DIMC,
                          FIRE1, FIRE2, FIRE3, CEIL, TIP, BACK_EDGE, FRONT_EDGE, WHEELS, FLOOR_RAMP, ROCKC, FARC, HOT,
                          HOT_EDGE, DEEP)

STEEL = "#c9d1d6"          # his sword
CHESTC = "#a08a64"         # the Humble chest's wood
MARKC = "#d8d0b0"          # the mark on its front
BOMBC = "#7a7a7a"
FUSEC = "#8a6a4a"

# ------------------------------------------------------------------ the passage, further along
# same rock as scene 1, further on. an old track along the back of the floor dead-ends at an outcrop, where the
# Bomb Cart goes off
PW, PH = s1.PW + 30, s1.PH
TRACK_ROW = 24             # the old rails; a cart on them has its wheels on row 23
DEAD_X = 200               # the last rail; a buffer, then the outcrop
OUTCROP = (199, 14)        # top-left of the rock the track runs into
COLUMNS = (16, 92, 150)
FISSURES = ((60, 12), (122, 14))
SUPPORTS = ((34, False), (108, True), (172, False))
DRIPS = (38, 140)          # under high parts of the ceiling (see build_scene1's DRIPS)
VENTS = ((76, 25),)
CRACK = (180, 194)         # where the blast opens the floor, near its front (rows 27-28)
HOLE = (192, 12, 216, 25)  # the blown-open rock: x0, y0, x1, y1
CHEST_AT = (199, 19)       # where the Humble chest sits in the rock before it falls (top-left)
CHEST_FLOOR = (199, 24)    # where it comes to rest on the floor (top-left; its base on row 26, his row)
BOMB_START = 36            # where the old Bomb Cart sits in the first shot (left edge)


def build_passage2():
    r = random.Random(61)
    mid = Grid(PW, PH)
    # ceiling and its drips
    for x in range(PW):
        c = ceiling(x)
        mid.blank(x, 0, x, c - 1, BACK)
        dy = ceiling(x + 1) - c
        mid.set(x, c, "_" if dy == 0 else ("\\" if dy > 0 else "/"), MIDG)
        for d in range(1, 5):
            stipple(mid, x, c - d, d, TEX, r)
        if r.random() < 0.22:
            mid.set(x, c + 1, r.choice("V'Y`"), TEX)

    def in_fissure(x, y):
        for fx, fw in FISSURES:
            top, bot = ceiling(fx) + 3, BACK_EDGE - 1
            if top <= y <= bot:
                hw = fw / 2 * (0.35 + 0.65 * (y - top) / (bot - top)) + math.sin(y * 1.7 + fx) * 0.8
                if abs(x - fx) < hw:
                    return True
        return False

    for x in range(PW):
        for y in range(ceiling(x) + 1, BACK_EDGE):
            if not in_fissure(x, y):
                mid.blank(x, y, x, y, BACK)
    for k, base in enumerate((14, 17, 20)):
        for x in range(PW):
            h = base + 0.9 * math.sin(x * 0.07 + k * 2 + 1) + 0.5 * math.sin(x * 0.19 + k)
            row = int(math.floor(h))
            if row > ceiling(x) + 1 and not in_fissure(x, row) and r.random() < 0.7:
                sub = h - row
                mid.set(x, row, "'" if sub < 0.34 else ("-" if sub < 0.67 else "_"), ROCKC)
    for x in range(PW):
        if r.random() < 0.35:
            y0 = ceiling(x) + 2
            for k in range(r.randint(1, 4)):
                if not in_fissure(x, y0 + k) and mid.get(x, y0 + k) == " ":
                    mid.set(x, y0 + k, r.choice("||'!:"), ROCKC)
        for y in range(ceiling(x) + 2, BACK_EDGE):
            if not in_fissure(x, y) and mid.get(x, y) == " " and r.random() < 0.035:
                mid.set(x, y, r.choice(".'`,:"), TEX)
    for fx, fw in FISSURES:
        top, bot = ceiling(fx) + 3, BACK_EDGE - 1
        for y in range(top, bot + 1):
            xs = [x for x in range(fx - fw, fx + fw) if in_fissure(x, y)]
            if xs:
                mid.set(xs[0] - 1, y, r.choice("/(|"), MIDG)
                mid.set(xs[-1] + 1, y, r.choice("\\)|"), MIDG)
    for sx in list(DRIPS) + [12, 66, 100, 162, 222]:
        c = ceiling(sx)
        n = max(1, TIP - c - 1) if sx in DRIPS else r.randint(1, 3)
        for k in range(n):
            w = max(0, (n - k) // 2)
            mid.set(sx - w - 1, c + 1 + k, "\\", MIDG)
            mid.set(sx + w + 1, c + 1 + k, "/", MIDG)
            mid.blank(sx - w, c + 1 + k, sx + w, c + 1 + k, BACK)
        mid.set(sx, c + 1 + n, "V" if n > 1 else "'", MIDG)
    for x, snapped in SUPPORTS:
        timber(mid, x, snapped, r)
    for px in COLUMNS:
        rock_column(mid, px, ceiling(px) + 1, BACK_EDGE, r)

    # the outcrop the track runs into, bulging out of the wall onto the floor
    ox, oy = OUTCROP
    rock = ["      _.-'`-._", "   .-'  :  .  `-.", "  /  .   '   :   \\", " /  :  .   ,  '  .\\", "|  '   :   .   :   |",
            "|  .  '  ,   :  ' .|", "| :   .   '   .  : |", "|__.-'`-.__.-'`-.__|", " :..::...:..::...::"]
    for j, row in enumerate(rock):
        a, b = len(row) - len(row.lstrip()), len(row.rstrip()) - 1
        mid.blank(ox + a, oy + j, ox + b, oy + j, BACK)
        for i, ch in enumerate(row):
            if ch != " ":
                mid.set(ox + i, oy + j, ch, TEX if ch in ".:',`" and a < i < b else MIDG)

    # the floor: rubble and grit, darker toward the back; the old track along its back, ending in a buffer
    for x in range(PW):
        if mid.get(x, BACK_EDGE) == " " and r.random() < 0.6:
            mid.set(x, BACK_EDGE, r.choice("_.-,'"), FLOOR_RAMP[BACK_EDGE])
    for y in range(BACK_EDGE + 1, FRONT_EDGE):
        col = FLOOR_RAMP[y]
        for x in range(PW):
            if mid.get(x, y) != " ":
                continue
            p = r.random()
            if p < 0.05:
                mid.set(x, y, r.choice(".,'`"), col)
            elif p < 0.065:
                mid.set(x, y, r.choice("o°"), col)
            elif p < 0.075:
                mid.set(x, y, r.choice("_/\\"), TEX)
    for x in range(0, DEAD_X):
        if r.random() < 0.9:
            mid.set(x, TRACK_ROW, "." if x % 3 == 0 else "_", TIEC)
        if r.random() < 0.6:
            mid.set(x, TRACK_ROW + 1, "`" if x % 3 == 1 else "¯", FAR)
    mid.text(DEAD_X - 1, TRACK_ROW - 1, "]=", MIDG)
    mid.text(DEAD_X - 1, TRACK_ROW, "]", MIDG)
    for lx, ly in ((24, 26), (64, 27), (130, 26), (158, 27)):
        mid.text(lx, ly, r.choice((".-.", "_.-._", ".o.")), MIDG)
    for vx, vy in VENTS:
        mid.text(vx - 3, vy, "_.-' `-._", MIDG)
    for dx in DRIPS:
        mid.text(dx - 1, TIP + 15, "~-~", MIDG)
    edge_line(mid, 0, PW - 1, FRONT_EDGE, r, GROUND)
    ribs(mid, 0, PW - 1, FRONT_EDGE + 1, 3, r, MIDG)
    for x in range(PW):
        if r.random() < 0.12:
            mid.set(x, FRONT_EDGE + 1, r.choice("VY'"), TEX)
    for y in range(FRONT_EDGE + 4, PH):
        for x in range(PW):
            if r.random() < 0.015:
                mid.set(x, y, r.choice(".`'"), DEEP if r.random() < 0.4 else FARC)

    # far: the deep cavern beyond the fissures
    far = Grid(180, PH)
    for x in range(far.w):
        if r.random() < 0.3:
            far.set(x, 9 + r.randint(0, 3), r.choice("V'Y`"), FARC)
    for px in range(14, far.w, 26):
        for y in range(10, 21):
            a = px - 2 + int(round(math.sin(y * 0.5 + px)))
            far.set(a, y, "(" if y % 3 else "|", FARC)
            far.set(a + 5, y, ")" if y % 3 else "|", FARC)
    edge_line(far, 0, far.w - 1, 21, r, "#3a3a3a")
    for x in range(far.w):
        if r.random() < 0.06:
            far.set(x, 22, r.choice(".'"), DEEP)

    # near the camera: a rock column and stalactites, rocks along the bottom (all solid)
    front = Grid(260, PH)
    rock_column(front, 60, 0, 35, r, near=True)
    rock_column(front, 150, 0, 35, r, near=True)
    for sx in (30, 104, 196):
        front.solid(sx, 0, ["\\     /", " \\ : /", "  \\:/", "   V", "   '"], NEAR)
    for rx in (10, 120, 210):
        front.solid(rx, FRONT_EDGE + 3, ["    /\\  _", "  _/ :`-' `._", "_/ ,  :  '   `\\", "  .  '  :   .  `-._"], NEAR)
    return far, mid, front


def build_aftermath():
    """What the blast leaves: the blown-open rock with the chest lodged in it, rubble, the glowing crack in the
    floor, and the solid lip in front of the crack so he can drop out of sight."""
    r = random.Random(7)
    x0, y0, x1, y1 = HOLE
    hole = Grid(x1 - x0 + 1, y1 - y0 + 1)
    cx = (x1 - x0) / 2
    for y in range(hole.h):
        for x in range(hole.w):
            # a ragged hollow, the rest solid rock with rubble on it
            depth = (hole.h - y) / hole.h
            if abs(x - cx) < (cx - 1) * (0.55 + 0.45 * math.sin(math.pi * min(1, y / (hole.h * 0.8)))) and y < hole.h - 3:
                hole.blank(x, y, x, y, BACK)
            else:
                hole.blank(x, y, x, y, BACK)
                if r.random() < 0.25:
                    hole.set(x, y, r.choice(".:',`"), TEX)
    for y in range(hole.h - 3):
        xs = [x for x in range(hole.w) if abs(x - cx) < (cx - 1) * (0.55 + 0.45 * math.sin(math.pi * min(1, y / (hole.h * 0.8))))]
        if xs:
            hole.set(xs[0], y, r.choice("/(|"), MIDG)
            hole.set(xs[-1], y, r.choice("\\)|"), MIDG)
    for x in range(hole.w):
        if r.random() < 0.8:
            hole.set(x, 0, r.choice("_.-'"), MIDG)
    # rubble spilled out of it over the end of the track
    pile = ["    _.,-'`-.,_.   ", "  .'o .  ,  o `.  ", " /. ' o  .  ' . \\ ", "/_,.-o-.,_.-'-.,_\\"]
    for j, row in enumerate(pile):
        a, b = len(row) - len(row.lstrip()), len(row.rstrip()) - 1
        yy = hole.h - len(pile) + j
        hole.blank(a + 2, yy, b + 2, yy, MIDG)
        hole.rows(2, yy, [row], MIDG)

    c0, c1 = CRACK
    crack = Grid(c1 - c0 + 1, 9)        # rows 27..35 of the passage
    lip = Grid(c1 - c0 + 1, 9)
    for x in range(crack.w):
        u = x / (crack.w - 1)
        w = math.sin(math.pi * u)
        open_rows = [0, 1] if w > 0.35 else ([1] if w > 0.12 else [])
        for y in open_rows:
            crack.blank(x, y, x, y, HOT_EDGE)
            if r.random() < 0.5:
                crack.set(x, y, r.choice(",.'"), HOT_EDGE)
        crack.set(x, 0 if w > 0.35 else 1, r.choice("_/\\") if w > 0.12 else "_", HOT)
        # in front of the opening, the floor's own lip and the ledge under it, solid
        for y in range(2, lip.h):
            lip.blank(x, y, x, y, MIDG)
        lip.set(x, 2, r.choice("_.-'") if r.random() < 0.6 else "_", GROUND)
        if r.random() < 0.5:
            lip.set(x, 3, r.choice("|'!"), MIDG)
    return hole, crack, lip


# ------------------------------------------------------------------ the drop: down the burning fissure
SHAFT_W, SHAFT_H = 90, 150


def build_shaft():
    """Inside the crack as he falls: ragged rock walls getting hotter and redder deeper down, then the dark."""
    r = random.Random(13)
    g = Grid(SHAFT_W, SHAFT_H)
    mx = SHAFT_W // 2
    for y in range(SHAFT_H):
        hw = 7 + 3 * math.sin(y * 0.06) + 1.5 * math.sin(y * 0.23 + 1)
        a = int(round(mx - hw + math.sin(y * 0.11) * 3))
        b = int(round(mx + hw + math.sin(y * 0.09 + 2) * 3))
        heat = min(1.0, y / (SHAFT_H * 0.55))
        edge = HOT if heat > 0.75 else (FIRE3 if heat > 0.5 else (HOT_EDGE if heat > 0.25 else MIDG))
        for x in range(SHAFT_W):
            if x < a or x > b:
                # nothing's ever behind the shaft, so the rock needs no fill
                d = a - x if x < a else x - b
                if d <= 4 and r.random() < [0, 0.5, 0.3, 0.15, 0.06][d]:
                    g.set(x, y, r.choice(":.'`"), HOT_EDGE if heat > 0.4 and d <= 2 else TEX)
                elif r.random() < 0.02:
                    g.set(x, y, r.choice("|'!"), ROCKC)
        pa, pb = (int(round(mx - (7 + 3 * math.sin((y - 1) * 0.06) + 1.5 * math.sin((y - 1) * 0.23 + 1)) + math.sin((y - 1) * 0.11) * 3)),
                  int(round(mx + (7 + 3 * math.sin((y - 1) * 0.06) + 1.5 * math.sin((y - 1) * 0.23 + 1)) + math.sin((y - 1) * 0.09 + 2) * 3)))
        g.set(a, y, "|" if a == pa else ("/" if a < pa else "\\"), edge)
        g.set(b, y, "|" if b == pb else ("\\" if b > pb else "/"), edge)
    # veins of heat running through the rock, more of them deeper down
    for k in range(26):
        y = r.randint(20, SHAFT_H - 10)
        side = r.choice((-1, 1))
        x = mx + side * r.randint(12, 40)
        for _ in range(r.randint(3, 7)):
            if 0 <= x < SHAFT_W and g.get(x, y) == " ":
                g.set(x, y, r.choice("/\\_"), HOT if y > SHAFT_H * 0.5 else HOT_EDGE)
            x += r.choice((-1, 1))
            y += r.choice((0, 1))
    # the bottom: the glow gives out into the dark
    for y in range(SHAFT_H - 20, SHAFT_H):
        for x in range(SHAFT_W):
            if g.c[y][x] and r.random() < (y - (SHAFT_H - 20)) / 20:
                g.c[y][x] = None
    return g


# ------------------------------------------------------------------ sprites
def build_sprites(ex):
    # the old Bomb Cart like the game's, a fused bomb in a cart, solid
    bomb = [" .-\"-. ", "/,    \\", "\\    ;/", "│¯¯¯¯¯│", "└()-()┘"]
    bmap = {"\"": FUSEC, ",": "#9a9a9a", ";": "#9a9a9a"}

    def bcol(x, y, ch):
        return bmap.get(ch, BOMBC) if y < 3 else ("#8a8a8a" if ch in "()" else CART)
    ex.piece("bombCart", frames_of([bomb, bomb[:4] + ["└()=()┘"]], BOMBC, cfn=bcol, solid=True))
    # its lit fuse, spitting sparks like the game's
    ex.piece("fuse", frames_of([[" + "], ["-:-"], [" * "], [".:'"]], FIRE1, {"-": FIRE2, ".": FIRE2, "'": FIRE2, ":": FIRE1}))

    # the blast: a flash, a ring of fire (the game's shape), a column of debris, then smoke
    W = 21
    flash = ["", "", "    \\  |  /", "  --  -*-  --", "    /  |  \\", "", ""]
    ring = ["      _.-----._", "   .-'         `-.", "  :               :", "  !               !",
            "   `.           .'", "     `-._____.-'", ""]
    ring2 = ["   _.-'```````'-._", " .'               `.", ":                   :", "!                   !",
             " `.               .'", "   `-.__     __.-'", "        `'''´"]
    column = ["         !", "        .|.", "     ( .|. )", "    (  ' '  )", "   ( .-'-._  )", "  (_.-'   `-._)", ""]
    smoke = ["      .  ( )", "   (    .   ( )", "  ( )  .  (   )", "    .  ( )   .", "      '   .", "", ""]
    smoke2 = ["       .", "    (     ( )", "      .     .", "   '     .", "", "", ""]

    def xcol(k):
        return lambda x, y, ch: (FIRE1 if k == 0 or ch in "*!|" else (FIRE2 if k in (1, 2) else
                                 (FIRE3 if k == 3 and y < 3 else "#8a8a8a")))
    frames = []
    for k, f in enumerate([flash, ring, ring2, column, smoke, smoke2]):
        g = Grid(W, 7)
        for y, row in enumerate(f):
            for x, ch in enumerate(row):
                if ch != " ":
                    g.set(x, y, ch, xcol(k)(x, y, ch))
        frames.append(g)
    ex.piece("blast", frames)
    # a piece of debris: whichever glyph the scene picks for it
    ex.piece("debris", frames_of([["o"], ["."], ["'"], [","], ["°"]], GROUND))

    # his cart, blown over: tipping, on its back with a wheel gone; the wheel on its own
    ex.piece("cartWreck", frames_of([[" .;;, ", "│¯¯¯¯│", "└()()┘"], ["   ,  ", " /¯¯¯/", "/()()/"],
                                     ["  () ", "┌────┐", "└────┘"]], CART, {"(": CARGO, ")": CARGO, ";": CARGO, ",": CARGO, ".": CARGO}))
    ex.piece("wheel", frames_of([["()"], ["<>"]], CARGO))
    ex.piece("ore", frames_of([[".;:,"]], CARGO))

    # the Pusher without his cart, facing right (the scene mirrors him). the pulls keep his body over braced legs
    # like the game's own pull pose
    man = [["    ", " O  ", "/|\\ ", " >\\ "], ["    ", " O  ", "/|\\ ", " |\\ "], ["    ", " O  ", "/|\\ ", " |> "],
           ["    ", " O  ", "/|\\ ", "/ \\ "],                                     # 0-3 walking
           ["    ", " O  ", "/|\\ ", "/ \\ "],                                     # 4 standing
           ["\\O/ ", " |  ", "/ \\ ", "    "],                                     # 5 thrown
           ["    ", "    ", " O  ", "/|__"],                                      # 6 sitting
           ["    ", "   O", " ¯/|", " |\\ "],                                     # 7 getting up (the game's bend)
           ["    ", "  O ", " /¯ ", "/|  "], ["    ", "  O ", " /¯ ", " |\\ "],     # 8-9 pushing
           ["     ", "     ", "  _\\O", " |\\/ "],                                   # 10 crouching (the game's pickup)
           ["\\O/ ", " |  ", "/ \\ ", "    "], [" O  ", "\\|/ ", " /\\ ", "    "],  # 11-12 falling
           ["    ", "   O", "  /─", " / >"],                                      # 13 straining
           ["    ", "   O", " ¯/|", " |\\ "],                                     # 14 bending to the lid
           ["    ", " O┐ ", "/|  ", "/ \\ "],                                     # 15 gripping its edge
           ["    ", "O─┐ ", "/|  ", " |\\ "],                                     # 16 pulling (the game's pull)
           ["    ", "O──┐", "\\|  ", " \\\\ "],                                    # 17 pulling hard, leaning back
           ["    ", "  O ", " /¯ ", "/ \\ "],                                     # 18 leaning in to look
           ["    ", "    ", "    ", "O<─<"]]                                      # 19 lying flat (the game's shape)
    g = frames_of(man, CHAR)
    ex.piece("manR", g)
    ex.piece("manL", mirror(g))

    # with his sword. bent over like the game's pickup pose, legs always on the ground
    sw = {"│": STEEL, "┼": STEEL, "─": STEEL}
    hero = [["      ", " O │  ", "/|\\┼  ", " >\\   "], ["      ", " O │  ", "/|\\┼  ", " |\\   "],
            ["      ", " O │  ", "/|\\┼  ", " |>   "], ["      ", " O │  ", "/|\\┼  ", "/ \\   "],   # 0-3 walking
            ["      ", " O │  ", "/|\\┼  ", "/ \\   "],                                            # 4 standing
            [" O │  ", "/|\\┼  ", " />   ", "      "],                                             # 5 the hop
            ["  │   ", " O┼   ", "/|    ", "/ \\   "],                                            # 6 raise
            ["      ", " O    ", "/|┼───", "/ \\   "],                                            # 7 strike
            ["      ", " O │  ", "/|\\┼  ", "/ \\   "],                                           # 8 recover
            ["      ", "   O  ", " ¯/|┼ ", " |\\ │ "],                                         # 9 bent over, sword hanging
            ["   /  ", " O┼   ", "/|    ", "/ \\   "],                                           # 10 the swing
            ["      ", "      ", "│ _\\O ", "┼|\\/  "]]                                         # 11 bent low (the game's pickup)
    g = frames_of(hero, CHAR, sw)
    ex.piece("heroR", g)
    ex.piece("heroL", mirror(g))

    # the Humble chest (the game's shape): shut, lid coming up, open, lid straining at the corner he pulls
    cmap = {"•": MARKC}
    ex.piece("chest", frames_of([[" ___ ", "├─•─┤", "└───┘"], [".───.", "├─•─┤", "└───┘"],
                                 ["     ", "┌─.─┐", "└───┘"], [".__  ", "'─•─┤", "└───┘"]], CHESTC, cmap))
    # its lid, pried off and tumbling away
    ex.piece("lid", frames_of([[".───."], ["  /  "], ["`───´"], ["  \\  "]], CHESTC))
    ex.piece("sword", frames_of([["│"], ["┼"]], STEEL))
    ex.piece("glint", frames_of([["·"], [" "], ["'"]], "#e8e8e8"))

    # the Controller's horn on its own, knocked off and tumbling (his frames are scene 1's ctrlL/ctrlR)
    ex.piece("horn", frames_of([["┘"], ["┐"], ["┌"], ["└"]], "#e7e3da"))
    # the spark where the sword snaps it off
    ex.piece("spark", frames_of([["\\|/", "-*-", "/|\\"], [" ' ", "' '", " . "]], "#f4f0e6"))
    # his lash, simulated in tools/whips.py: down from over his head, sweeping the floor, cracking at the tip, then
    # reeled back in
    import whips
    g, ox, oy, crack = whips.lash(hand_y=-1.0, dir=1, col=CHAR, keep=9)
    ex.piece("lash", g)
    ex.value("lashOX", ox)
    ex.value("lashOY", oy)
    ex.value("lashCrack", crack)
    ex.value("lashN", len(g))


def main():
    pkg = sys.argv[1]
    os.makedirs(pkg, exist_ok=True)
    head = "// Generated by tools/build_scene2.py. Don't edit by hand; change the script and rebuild.\n"

    far, mid, front = build_passage2()
    hole, crack, lip = build_aftermath()
    ex = Exporter(head)
    ex.value("wheels", WHEELS)
    ex.value("trackRow", TRACK_ROW)
    ex.value("deadX", DEAD_X)
    ex.piece("far", [far])
    ex.piece("mid", [mid])
    ex.piece("front", [front])
    ex.piece("hole", [hole])
    ex.value("holeX", HOLE[0])
    ex.value("holeY", HOLE[1])
    ex.piece("crack", [crack])
    ex.piece("lip", [lip])
    ex.value("crackX", CRACK[0])
    ex.value("crackY", 27)
    ex.value("chestX", CHEST_AT[0])
    ex.value("chestY", CHEST_AT[1])
    ex.value("chestFloorY", CHEST_FLOOR[1])
    ex.value("bombStart", BOMB_START)
    ex.value("dripX", list(DRIPS))
    ex.value("dripTop", TIP + 1)
    ex.value("ventX", [v[0] for v in VENTS])
    ex.value("ventY", [v[1] for v in VENTS])
    n1 = ex.write(os.path.join(pkg, "Art2Passage.txt"))

    ex = Exporter(head)
    ex.piece("shaft", [build_shaft()])
    ex.value("w", SHAFT_W)
    ex.value("h", SHAFT_H)
    n2 = ex.write(os.path.join(pkg, "Art2Shaft.txt"))

    ex = Exporter(head)
    build_sprites(ex)
    n3 = ex.write(os.path.join(pkg, "Art2Sprites.txt"))
    print(f"Art2Passage {n1}, Art2Shaft {n2}, Art2Sprites {n3} bytes")


if __name__ == "__main__":
    main()
