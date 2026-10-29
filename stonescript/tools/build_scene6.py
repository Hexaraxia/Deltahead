"""Builds the art for scene 6 (the legend spreads).

    python -I build_scene6.py <package dir>

Writes Art6Mountain.txt: the closing shot of the whole mountain at night, the mine at its foot, a trail up through
the cloud, and a speck still climbing at the top. The mine shot before it reuses scene 1's art.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_scene1 import Grid, Exporter, frames_of, FAR, BACK, MIDG, GROUND, TEX

MW, MH = 150, 80
PEAK = (75, 8)                       # the summit
SHOULDERS = ((38, 34, 1.1), (116, 30, 1.0))   # lesser peaks either side: x, top row, steepness
SNOWLINE = 27
CLOUD = (36, 45)                     # cloud band rows, where the Perilous Climb is
MINE = (75, 74)                      # mine mouth center column, floor row
TRAIL = [(75, 73), (56, 66), (86, 58), (60, 50), (89, 42), (66, 34), (87, 26), (72, 19), (79, 13)]
MOON = (44, 3)

ROCK = "#1b1f25"                     # the mountain's dark body
LIT = "#7a8492"                      # moonlit face, moon's on the left
SHADED = "#3a414b"
EDGE = "#8c96a4"
SNOW = "#d8e0e6"
SNOW_DIM = "#8f9aa4"
FOG = "#7c8692"
FOG_DIM = "#4e5662"
STAR = "#c8ccd4"
LAMP = "#ffb35c"
TRAILC = "#8a929c"


def top(x):
    """Skyline row at column x."""
    px, py = PEAK
    h = py + abs(x - px) * 0.95 + 1.2 * math.sin(x * 0.31) + 0.8 * math.sin(x * 0.13 + 1)
    for sx, sy, k in SHOULDERS:
        h = min(h, sy + abs(x - sx) * k + 0.8 * math.sin(x * 0.4))
    return h


def build():
    r = random.Random(61)
    g = Grid(MW, MH)
    # the sky behind is the shared one in ArtSky.txt
    # dark rock, moonlit face stippled lighter, far face in shadow, snow on top
    for x in range(MW):
        t = top(x)
        for y in range(int(math.ceil(t)), MH):
            g.blank(x, y, x, y, ROCK)
            lit_side = x < PEAK[0] - (y - PEAK[1]) * 0.15
            depth = y - t
            p = r.random()
            if y < SNOWLINE + 2 * math.sin(x * 0.27) and depth < 9:
                if p < 0.55 - depth * 0.04:
                    g.set(x, y, r.choice(".:'`"), SNOW if lit_side and depth < 4 else SNOW_DIM)
            elif lit_side and p < 0.2:
                g.set(x, y, r.choice(".'`"), LIT)
            elif not lit_side and p < 0.08:
                g.set(x, y, ".", SHADED)
    # the skyline itself, snow-edged up high
    for x in range(MW):
        y = int(math.ceil(top(x)))
        dy = int(math.ceil(top(x + 1))) - y
        ch = "_" if dy == 0 else ("\\" if dy > 0 else "/")
        if 0 <= y < MH:
            g.set(x, y, ch, SNOW if y < SNOWLINE + 3 else EDGE)
    g.text(PEAK[0] - 1, PEAK[1], "/\\", "#ffffff")
    # ridges running down from the summit and the shoulders
    for sx, sy, dx, n in ((PEAK[0], PEAK[1] + 1, -0.45, 30), (PEAK[0] + 1, PEAK[1] + 1, 0.55, 26),
                          (38, 35, 0.35, 14), (116, 31, -0.4, 16), (PEAK[0] - 8, PEAK[1] + 12, -0.2, 20)):
        x = float(sx)
        for k in range(n):
            y = sy + k
            x += dx + r.uniform(-0.3, 0.3)
            if 0 <= int(x) < MW and y < MH and y > top(int(x)) + 0.5:
                g.set(int(x), y, "\\" if dx > 0 else "/", SNOW_DIM if y < SNOWLINE else SHADED)
    # the trail switching back up the face, dotted
    for (x0, y0), (x1, y1) in zip(TRAIL, TRAIL[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0) * 2)
        for k in range(0, n + 1, 2):
            x = int(round(x0 + (x1 - x0) * k / n))
            y = int(round(y0 + (y1 - y0) * k / n))
            g.set(x, y, "." if y > SNOWLINE else "'", TRAILC if y > SNOWLINE else SNOW_DIM)
    # mine mouth: dark arch, a lamp either side, rails going in
    mx, my = MINE
    arch = ["  _.-'¯¯'-._  ", " /          \\ ", "|            |", "|            |"]
    for j, row in enumerate(arch):
        y = my - 3 + j
        g.blank(mx - 7, y, mx + 6, y, "#000000")
        g.rows(mx - 7, y, [row], MIDG)
    for x in range(mx - 30, mx + 31):
        g.set(x, my + 1, "=" if mx - 6 <= x <= mx + 5 else ("-" if x % 2 else "_"), BACK if abs(x - mx) > 6 else MIDG)
    g.set(mx - 8, my - 2, "*", LAMP)
    g.set(mx + 7, my - 2, "*", LAMP)
    # the foothills in front of it all
    for x in range(MW):
        y = MH - 3 + int(round(1.2 * math.sin(x * 0.09) + 0.6 * math.sin(x * 0.23)))
        for yy in range(y, MH):
            g.blank(x, yy, x, yy, "#0e1013")
        g.set(x, y, r.choice("_.-'"), TEX)
    return g


def build_clouds():
    """Cloud wisps round the mountain's middle, drawn over it and drifted sideways by the scene."""
    r = random.Random(62)
    c = Grid(MW + 40, CLOUD[1] - CLOUD[0] + 1)
    for y in range(c.h):
        mid = abs(y - c.h / 2) / (c.h / 2)
        for x in range(c.w):
            w = 0.5 + 0.5 * math.sin(x * 0.07 + y * 0.6)
            if r.random() < 0.5 * w * (1 - mid):
                c.set(x, y, r.choice("~-._~"), FOG if mid < 0.4 else FOG_DIM)
    return c


def main():
    pkg = sys.argv[1]
    head = "// Generated by tools/build_scene6.py. Don't edit by hand; change the script and rebuild.\n"
    ex = Exporter(head)
    ex.piece("mountain", [build()])
    ex.piece("clouds", [build_clouds()])
    ex.value("w", MW)
    ex.value("h", MH)
    ex.value("peakX", PEAK[0])
    ex.value("peakY", PEAK[1])
    ex.value("cloudY", CLOUD[0])
    ex.value("trailX", [x for x, _ in TRAIL])
    ex.value("trailY", [y for _, y in TRAIL])
    ex.value("mineX", MINE[0])
    ex.value("mineY", MINE[1])
    # him at the top of the trail, Pushers going into the mine, the lamp flicker
    ex.piece("speck", frames_of([["·"], ["."]], "#ffffff"))
    ex.piece("dot", frames_of([["o"]], "#8a8a8a"))
    ex.piece("lamp", frames_of([["*"], ["+"], ["*"], ["·"]], LAMP))
    # snow blown off the summit, the scene grays and fades each flake
    ex.piece("drift", frames_of([["'"], ["."], [","]], "#ffffff"))
    # a shooting star: its head, then its trail
    ex.piece("glint", frames_of([["*"], ["+"], ["-"], ["."]], "#ffffff"))
    n = ex.write(os.path.join(pkg, "Art6Mountain.txt"))
    print(f"Art6Mountain {n} bytes")


if __name__ == "__main__":
    main()
