"""Builds the art for scene 14 (the Mountaintop Bridge).

    python -I build_scene14.py <package dir>

Writes Art14Bridge.txt: the Mountaintop Bridge, the game's Cross the Bridge far below, the Stream of the Silent with
the figures and chests it carries up, and him with his ∆ and Ice Sword.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_scene1 import Grid, Exporter, frames_of, CHAR, TEX, ROCKC
from build_scene7 import SNOW, SNOW_DIM, SNOW_BACK, crop
import bridge_frames as BF
import grand_bridge as GB

WW, WH = 340, 104
X0, Y0 = 30, 13                   # first span: its first back post, top of its cap
SPANS = 6                         # spans after the first, each 43 columns
RAIL, FEET, EDGE = Y0 + 6, Y0 + 11, Y0 + 14     # deck: back rail, where he walks, front edge
BEAM_X, BEAM_W = 186, 9           # the Stream of the Silent, in front of the middle of a span
LEDGE = 30                        # where the mountain ends and the bridge begins
X0B, Y0B = 109, 80                # the game's Cross the Bridge far below, its first span

CAP = "#c8b08a"
CABLE = "#a89070"
HANGER = "#6e604a"
RAILC = "#8a7660"
PLANK = "#5f5142"
EDGEC = "#8a7660"
FRONT = "#c0a882"
FRONT_HANGER = "#8a7a5e"
WOOD_TRIM = "#8a7660"
ICE_BLADE = "#ff2222"             # Ice Sword +15 in the game's Legendary red, same as scene 13
LAMP = "#e8c070"                  # lanterns on the front posts, pennants on the back
FLAG = "#c0503c"
# the game's bridge, in blizzard colors
G_CAP, G_CABLE, G_HANGER, G_RAIL, G_PLANK, G_EDGE, G_FRONT = ("#9aa6b2", "#7c8a96", "#55606a", "#6c7884", "#4a535c",
                                                         "#6c7884", "#8e9ca8")
G_SNOW, G_LAND = "#9aa6ac", "#5a646c"
G_WHITE = "#d0d8de"               # the silent in the Stream, white like the game's


def stamp(g, rows, x0, y0, cfn):
    """Stamps a game piece: `#` and past a line's end are see-through, spaces are solid."""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "#":
                continue
            x, y = x0 + i, y0 + j
            if ch == " ":
                g.blank(x, y, x, y, TEX)
            else:
                g.set(x, y, ch, cfn(i, j, ch))


def back_color(i, j, ch):
    if j <= 1 and ch in "()¯":
        return CAP
    if j <= 5:
        return HANGER if ch == "|" else CABLE
    if j == 6:
        return RAILC
    if j >= 14:
        return EDGEC if j == 14 else HANGER
    return PLANK


def front_color(i, j, ch):
    if ch in "()¯" and j <= 1:
        return CAP
    if ch == "|":
        return FRONT_HANGER
    return FRONT


def build_bridge():
    """The back of the bridge and its front railing (drawn over whoever's crossing), span by span."""
    back = Grid(WW, WH)
    front = Grid(WW, WH)
    stamp(back, BF.FIRST, X0, Y0, back_color)
    for k in range(SPANS):
        stamp(back, BF.SPAN, X0 + 44 + 43 * k, Y0, back_color)
    stamp(front, BF.FIRST_FRONT, X0, Y0 + 8, front_color)
    for k in range(SPANS):
        stamp(front, BF.SPAN_FRONT, X0 + 44 + 43 * k, Y0 + 8, front_color)
    # a lantern on every front post, a pennant over every back one
    lamps, flags = [], []
    for p in [X0 + 8] + [X0 + 51 + 43 * k for k in range(SPANS)]:
        y = Y0 + 8
        front.text(p - 1, y - 3, " _ ", LAMP)
        front.text(p - 1, y - 2, "[ ]", LAMP)
        front.text(p - 1, y - 1, " ┴ ", WOOD_TRIM)
        lamps.append((p, y - 2))
    for p in [X0 + 1] + [X0 + 44 + 43 * k for k in range(SPANS)]:
        for y in range(Y0 - 3, Y0):
            back.set(p, y, "|", WOOD_TRIM)
        flags.append((p + 1, Y0 - 3))
    return back, front, lamps, flags


def build_game_bridge():
    """The game's Cross the Bridge with its backdrop, in blizzard colors. Nobody crosses it, so it's one piece."""
    g = Grid(WW, WH)
    stamp(g, BF.BACKDROP, X0B - 57, Y0B - 8, lambda i, j, ch: G_SNOW if ch in "_/´`:.'·^" and j < 5 else G_LAND)
    def back(i, j, ch):
        if j <= 1 and ch in "()¯":
            return G_CAP
        if j <= 5:
            return G_HANGER if ch == "|" else G_CABLE
        if j == 6:
            return G_RAIL
        if j >= 14:
            return G_EDGE if j == 14 else G_HANGER
        return G_PLANK
    def front(i, j, ch):
        if ch in "()¯" and j <= 1:
            return G_CAP
        return G_HANGER if ch == "|" else G_FRONT
    stamp(g, BF.FIRST, X0B, Y0B, back)
    for k in range(SPANS):
        stamp(g, BF.SPAN, X0B + 44 + 43 * k, Y0B, back)
    stamp(g, BF.FIRST_FRONT, X0B, Y0B + 8, front)
    for k in range(SPANS):
        stamp(g, BF.SPAN_FRONT, X0B + 44 + 43 * k, Y0B + 8, front)
    return g


FAR = "#5e6a76"
FAR_DIM = "#333c45"


def build_far_bridge():
    """The game's Cross the Bridge, small and far below, with the Stream going up past it."""
    span = 15
    n = 6
    w = span * n + 2
    rows = ["", "", "", ""]
    for k in range(n):
        rows[0] += "()" + " " * (span - 2)
        rows[1] += "|`-.,_" + " " * (span - 11) + "_,.-´"
        rows[2] += "|" + "".join("'" if i % 3 == 2 else "¯" for i in range(span - 1))
        rows[3] += "!'" + " " * (span - 2)
    rows[0] += "()"
    rows[1] += "|"
    rows[2] += "|"
    rows[3] += "!'"
    g = Grid(w, 4)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != " ":
                g.set(x, y, ch, FAR if y < 3 else FAR_DIM)
    return g


def build_ledge():
    """The end of the mountain the bridge starts from: snowfield out to the edge, rock under it."""
    r = random.Random(142)
    w = LEDGE + 2
    g = Grid(w, WH)
    for x in range(w):
        top = RAIL - 1
        g.set(x, top, "_" if r.random() < 0.7 else r.choice("-.,"), SNOW_BACK)
        for y in range(top + 1, EDGE):
            g.blank(x, y, x, y, TEX)
            if r.random() < 0.1:
                g.set(x, y, r.choice("_-.'`"), SNOW_DIM)
        g.set(x, EDGE, "¯", SNOW)
        depth = 12 + int(4 * math.sin(x * 0.2))
        for y in range(EDGE + 1, min(WH, EDGE + depth)):
            g.blank(x, y, x, y, TEX)
            if r.random() < 0.15:
                g.set(x, y, r.choice("|'!:."), ROCKC)
    # the edge, going down under the bridge's first span
    for y in range(EDGE + 1, WH):
        d = y - EDGE
        e = w - 1 - min(6, d // 3)
        g.set(e, y, r.choice("|)\\"), ROCKC if d < 10 else "#2a2a2a")
        for x in range(e + 1, w):
            g.c[y][x] = None
    return g


# the game's chests and their colors
CHESTS = [
    ([" ___ ", "├─•─┤", "└───┘"], "#d8d4cc"),          # Humble
    (["┌-─-┐", "╞╤8╤╡", "└┴─┴┘"], "#b89870"),          # Giant
    ([" ___ ", "┼┬Ω┬┼", "└┴─┴┘"], "#ffe08a"),          # Omega
    (["  ___ ", "ε╪=o=╪3", " └───┘"], "#e8e0c8"),     # Bone
    (["┌-─-┐", "╞╤♥╤╡", "└┴─┴┘"], "#ff9a9a"),          # vigor
    (["┌-─-┐", "╞╤❄╤╡", "└┴─┴┘"], "#a8d8f0"),          # ice
    (["┌-─-┐", "╞╤∞╤╡", "└┴─┴┘"], "#c8a8ff"),          # aether
    ([" ___ ", "├─o─┤", "└───┘"], "#d8d4cc"),          # Humble, the other
    (["┌-─-┐", "╞╤φ╤╡", "└┴─┴┘"], "#a8e080"),          # poison
    ([" ___ ", "╞─∆─╡", "└───┘"], "#ffffff"),          # Delta, drawn in rainbow
]


# him facing right with the Ice Sword: walking, standing, leaning out to look down, and the hop into the light
HERO = [
    ["   │  ", " O ❄  ", "/|\\T  ", " >\\   "],
    ["   │  ", " O ❄  ", "/|\\T  ", " |\\   "],
    ["   │  ", " O ❄  ", "/|\\T  ", " |>   "],
    ["   │  ", " O ❄  ", "/|\\T  ", "/ \\   "],
    ["   │  ", " O ❄  ", "/|\\T  ", "/ \\   "],     # 4 standing
    ["    │ ", "  O ❄ ", " /|\\T ", "/ \\   "],     # 5 leaning out to look down
    ["   │  ", " O ❄  ", "/|\\T  ", " />   "],     # 6 the hop
]


def main():
    pkg = sys.argv[1]
    os.makedirs(pkg, exist_ok=True)
    head = "// Generated by tools/build_scene14.py. Don't edit by hand; change the script and rebuild.\n"
    ex = Exporter(head)
    ex.value("ww", WW)
    ex.value("rail", RAIL)
    ex.value("feet", FEET)
    ex.value("edge", EDGE)
    ex.value("beamX", BEAM_X)
    ex.value("beamW", BEAM_W)
    # the Mountaintop Bridge, behind him and in front. split by color, the scene puts them back together
    back, front, lamps, flags, medal = GB.build(WW)
    half = WW // 2
    ex.piece("bridgeA", [crop(back, 0, 0, half, back.h)], split=True)
    ex.piece("bridgeB", [crop(back, half, 0, WW - half, back.h)], split=True)
    ex.piece("frontA", [crop(front, 0, 0, half, front.h)], split=True)
    ex.piece("frontB", [crop(front, half, 0, WW - half, front.h)], split=True)
    ex.value("half", half)
    ex.value("top", GB.TOP)
    ex.value("gapX0", GB.GAP[0])
    ex.value("gapX1", GB.GAP[1])
    ex.value("lampX", [x for x, _ in lamps])
    ex.value("lampY", [y for _, y in lamps])
    ex.value("flagX", [x for x, _ in flags])
    ex.value("flagY", [y for _, y in flags])
    ex.value("medalX", medal[0])
    ex.value("medalY", medal[1])
    ex.piece("flag", frames_of([["~="], ["=~"], ["-~"], ["~-"]], FLAG))
    ex.piece("flame", frames_of([["*"], ["+"], ["*"], ["·"]], "#ffd890"))
    # the game's own, far below
    game = build_game_bridge()
    gy = Y0B - 10
    ex.piece("gameA", [crop(game, 0, gy, half, 30)], split=True)
    ex.piece("gameB", [crop(game, half, gy, WW - half, 30)], split=True)
    ex.value("gameTop", gy)
    ex.value("gameY0", Y0B)
    ex.value("gameX0", X0B)
    for i, n in enumerate(range(-4, 5)):
        ex.piece(f"sc{i}", frames_of([[r.replace("#", " ") for r in fr] for fr in BF.STREAM[n]], "#9ff0b8"))
        ex.piece(f"sp{i}", frames_of([[r.replace("#", " ") for r in fr] for fr in BF.STREAM_P[n]], "#dff8e8"))
    for k, (rows, col) in enumerate(CHESTS):
        # no crop for the Delta, the game's rainbow runs across the whole page
        ex.piece(f"chest{k}", frames_of([rows], col), crop=k < len(CHESTS) - 1)
    ex.value("chestN", len(CHESTS))
    # each figure the Stream carries up: its row in the strip, how far left of the middle it starts, its height
    figs = []
    j = 0
    while j < len(BF.BODIES):
        if not BF.BODIES[j]:
            j += 1
            continue
        k = j
        while k < len(BF.BODIES) and BF.BODIES[k]:
            k += 1
        rows = [r.replace("#", " ") for r in BF.BODIES[j:k]]
        left = min(len(r) - len(r.lstrip(" ")) for r in rows)
        figs.append((j, left - 4, [r[left:] for r in rows]))
        j = k
    for i, (_, _, rows) in enumerate(figs):
        ex.piece(f"fig{i}", frames_of([rows], G_WHITE))
    ex.value("figR", [r for r, _, _ in figs])
    ex.value("figX", [dx for _, dx, _ in figs])
    ex.value("figH", [len(rows) for _, _, rows in figs])
    ex.piece("streak", frames_of([["|", "|"], ["|", "'"], ["'", "."]], "#ffffff"))
    xs, ys = [], []
    for f in HERO:
        for y, row in enumerate(f):
            if "O" in row:
                xs.append(row.index("O"))
                ys.append(y)
                break
    blade = {"│": ICE_BLADE, "❄": ICE_BLADE, "T": ICE_BLADE}
    ex.piece("hero", frames_of([[row.replace("O", " ") for row in f] for f in HERO], CHAR, blade))
    # his sword on its own, drawn over the railing so a hanger or post can't hide it (it's one cell wide)
    ex.piece("heroSword", frames_of([["".join(c if c in blade else " " for c in row) for row in f] for f in HERO],
                                    ICE_BLADE))
    # but not over a tower, those stand in front of the deck
    ex.value("swordCol", [min(row.index(c) for row in f for c in row if c in blade) for f in HERO])
    ex.value("towerX", GB.TOWERS)
    ex.value("headX", xs)
    ex.value("headY", ys)
    n = ex.write(os.path.join(pkg, "Art14Bridge.txt"))
    print(f"Art14Bridge {n} bytes")


if __name__ == "__main__":
    main()
