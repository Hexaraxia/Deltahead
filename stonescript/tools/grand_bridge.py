"""The Mountaintop Bridge for scene 14 (our own, not the game's): stone towers either side of the Stream with beacons,
pennants and ∆ banners, gold cables with a ∆ medallion over the Stream, and a deck on arches that stops at the gap.

build(ww) returns the Grid behind whoever's crossing and the one in front (row 0 is world row TOP), and where its
lanterns, pennants and medallion are.
"""
import math

from build_scene1 import Grid, TEX

TOP = -8                       # the grids' first row, in world rows (the towers go up out of the picture)
RAIL, FEET, EDGE = 19, 24, 27  # the deck: its back balustrade, where he walks, its front edge
BEAM = 186                     # the Stream's middle
GAP = (182, 190)               # where the deck stops for it
TOWERS = [100, 164, 208, 272]
DECK = (40, 330)

STONE = "#9a9488"
STONE_DIM = "#5e5a52"
STONE_DARK = "#3a3732"
GOLD = "#d8b060"
GOLD_DIM = "#8a7040"
BALUS = "#a8a090"
PAVE = "#4a463e"
BANNER = "#a8382c"
EMBLEM = "#e8c070"
LAMP = "#e8c070"


def cable_char(slope):
    a = abs(slope)
    if a > 0.9:
        return "\\" if slope > 0 else "/"
    if a > 0.45:
        return "`" if slope > 0 else "´"
    if a > 0.2:
        return "-"
    if a > 0.07:
        return "." if slope > 0 else ","
    return "_"


def arch_char(slope):
    a = abs(slope)
    if a > 0.9:
        return "/" if slope > 0 else "\\"
    if a > 0.45:
        return "´" if slope > 0 else "`"
    if a > 0.2:
        return "-"
    return "_"


def build(ww):
    h = 54
    back = Grid(ww, h)
    front = Grid(ww, h)
    Y = lambda y: y - TOP

    def put(g, x, y, ch, col):
        g.set(x, Y(y), ch, col)

    def text(g, x, y, s, col):
        for i, ch in enumerate(s):
            if ch != " ":
                put(g, x + i, y, ch, col)

    def blank(g, x, y):
        g.blank(x, Y(y), x, Y(y), TEX)

    in_gap = lambda x: GAP[0] <= x <= GAP[1]
    in_tower = lambda x: any(abs(x - t) <= 3 for t in TOWERS)

    # the deck: back balustrade, paving, front balustrade and its coping; the cut ends at the gap
    for x in range(DECK[0], DECK[1]):
        if in_gap(x):
            continue
        put(back, x, RAIL, "╤" if x % 4 == 0 else "═", BALUS)
        put(back, x, RAIL + 1, "│" if x % 2 == 0 else " ", STONE_DIM)
        if x % 2:
            blank(back, x, RAIL + 1)
        for y in range(RAIL + 2, EDGE - 1):
            blank(back, x, y)
            if (x + 2 * y) % 8 in (0, 1, 2):
                put(back, x, y, "─", PAVE)
        put(front, x, EDGE - 2, "╤" if x % 4 == 0 else "═", BALUS)
        put(front, x, EDGE - 1, "│" if x % 4 == 0 else " ", STONE_DIM)
        if x % 4:
            blank(front, x, EDGE - 1)
        put(front, x, EDGE, "╧" if x % 4 == 0 else "═", STONE)
    for x, ch in ((GAP[0] - 1, "╣"), (GAP[1] + 1, "╠")):
        for y in range(RAIL, EDGE + 1):
            put(front, x, y, "║", STONE)
        put(front, x, RAIL, "╦", STONE)
        put(front, x, EDGE, "╩", STONE)

    # under the deck: its underside, an arcade of arches between the piers, the gap open through it
    piers = sorted(set(TOWERS + [t + 32 for t in TOWERS[:-1]]))
    for x in range(DECK[0], DECK[1]):
        if not in_gap(x):
            put(back, x, EDGE + 1, "¯", STONE_DIM)
    for a, b in zip(piers, piers[1:]):
        m, hw = (a + b) / 2.0, (b - a) / 2.0 - 2
        for x in range(a + 2, b - 1):
            if in_gap(x):
                continue
            u = (x - m) / hw
            y = EDGE + 2 + 3.0 * u * u
            yn = EDGE + 2 + 3.0 * ((x + 1 - m) / hw) ** 2
            for yy in range(EDGE + 2, int(round(y))):
                blank(back, x, yy)
                if (x * 3 + yy) % 7 == 0:
                    put(back, x, yy, ".", STONE_DARK)
            put(back, x, int(round(y)), arch_char(yn - y), STONE_DIM)
    for p in piers:
        for y in range(EDGE + 2, 46):
            col = STONE_DIM if y < 38 else STONE_DARK
            put(back, p - 1, y, "║", col)
            put(back, p + 1, y, "║", col)
            blank(back, p, y)
            if y % 4 == 0:
                put(back, p, y, "═", col)

    # the towers: spire, beacon room, the shaft with its banner, and the face in front of the deck
    lamps, flags = [], []
    for c in TOWERS:
        x0 = c - 3
        text(back, x0, -7, "   |   ", STONE)
        text(back, x0, -6, "   ^   ", GOLD)
        text(back, x0, -5, "  / \\  ", STONE)
        text(back, x0, -4, " /___\\ ", STONE)
        text(back, x0, -3, " |   | ", STONE)
        text(back, x0, -2, " |[ ]| ", STONE)
        put(back, c - 1, -2, "[", LAMP)
        put(back, c + 1, -2, "]", LAMP)
        blank(back, c, -2)
        text(back, x0, -1, " |___| ", STONE)
        text(back, x0, 0, "/=====\\", STONE)
        lamps.append((c, -2))
        flags.append((c + 1, -7))
        for y in range(1, RAIL):
            course = y % 5 == 0
            text(back, x0, y, "║──┼──║" if course else "║  │  ║", STONE if not course else STONE_DIM)
            for x in range(x0 + 1, x0 + 6):
                if back.c[Y(y)][x] is None:
                    blank(back, x, y)
        # the banner: hung from the cornice, the ∆ on it
        text(back, c - 1, 2, "╤═╤", BANNER)
        for y in range(3, 9):
            put(back, c - 1, y, "│", BANNER)
            put(back, c + 1, y, "│", BANNER)
            blank(back, c, y)
        put(back, c, 4, "∆", EMBLEM)
        text(back, c - 1, 9, "\\ /", BANNER)
        put(back, c, 10, "V", BANNER)
        # its face in front of the deck
        for y in range(RAIL, EDGE + 1):
            text(front, x0, y, "║  │  ║", STONE)
            for x in range(x0 + 1, x0 + 6):
                if front.c[Y(y)][x] is None:
                    blank(front, x, y)
        text(front, x0, EDGE, "╩══╧══╩", STONE)

    # two cables sagging from tower to tower, hangers down to the balustrade
    medal = None
    for a, b in zip(TOWERS, TOWERS[1:]):
        x1, x2 = a + 4, b - 4
        m, hw = (x1 + x2) / 2.0, (x2 - x1) / 2.0
        sag = 7
        for x in range(x1, x2 + 1):
            u = (x - m) / hw
            y = 1 + sag * (1 - u * u)
            yn = 1 + sag * (1 - ((x + 1 - m) / hw) ** 2)
            put(back, x, int(round(y)), cable_char(yn - y), GOLD)
            put(back, x, int(round(y)) - 1, cable_char(yn - y), GOLD_DIM)
            if (x - x1) % 4 == 2 and not in_gap(x) and not in_tower(x) and abs(x - m) < hw - 3:
                for yy in range(int(round(y)) + 1, RAIL):
                    put(back, x, yy, "│", GOLD_DIM)
        if a < BEAM < b:
            # the medallion over the Stream, on a short chain from the cables' lowest point
            low = int(round(1 + sag))
            put(back, BEAM, low + 1, "│", GOLD)
            text(back, BEAM - 1, low + 2, "( )", GOLD)
            medal = (BEAM, low + 2)
    # lanterns either side of the gap, on the back balustrade
    for x in (GAP[0] - 3, GAP[1] + 3):
        text(back, x - 1, RAIL - 3, " _ ", LAMP)
        put(back, x - 1, RAIL - 2, "[", LAMP)
        put(back, x + 1, RAIL - 2, "]", LAMP)
        blank(back, x, RAIL - 2)
        put(back, x, RAIL - 1, "┴", STONE)
        lamps.append((x, RAIL - 2))
    return back, front, lamps, flags, medal
