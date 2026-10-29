"""Builds the art for scene 9 (a quiet moment).

    python -I build_scene9.py <package dir>

Writes Art9Ledge.txt: the ledge over the drop, the mountain's lower slopes, and his sprites. The sky, far ranges and
cloud are scene 7's.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_scene1 import Grid, Exporter, frames_of, mirror, MIDG, TEX, ROCKC, CHAR
from build_scene7 import SNOW, SNOW_DIM, SNOW_BACK, FOG_DIM
import kifoe_frames as K
from build_scene8 import game_piece

STEEL = "#c9d1d6"           # his sword
MOONLIT = "#b8c2ca"         # rock the moon catches
ROCK_DARK = "#2a3036"
FILL = "#090b0d"
GOLD = "#d7af42"            # the glint far below, in the game's Monarch gold

LW, LH = 60, 26             # the ledge
SEAT = 6                    # row his seat (or feet, standing) is on
LIP = 50                    # column where the drop begins
FW, FH = 90, 12             # the mountain below


def build_ledge():
    """The ledge from the side: snowy top, rock under it, and the moonlit lip with drips under the overhang."""
    r = random.Random(91)
    g = Grid(LW, LH)
    far, front = SEAT - 2, SEAT + 2
    for x in range(LIP + 1):
        # the top: deeper toward the left, where the ledge joins the mountain
        g.set(x, far, "_" if r.random() < 0.75 else r.choice("-_."), SNOW_BACK)
        for y in range(far + 1, front):
            g.blank(x, y, x, y, TEX)
            if r.random() < 0.1:
                g.set(x, y, r.choice("_-¯.'`"), SNOW_BACK if y < SEAT else SNOW_DIM)
        g.set(x, front, "¯" if x < LIP else "'", SNOW)
        # the rock face under it, ribs fading downward
        for y in range(front + 1, LH):
            g.blank(x, y, x, y, FILL)
            d = y - front
            p = r.random()
            if d == 1 and p < 0.55:
                g.set(x, y, r.choice(".:'"), SNOW_DIM)
            elif d < 5 and p < 0.25 / d:
                g.set(x, y, r.choice("|'!:"), ROCKC)
            elif p < 0.03:
                g.set(x, y, r.choice(".'`"), TEX)
        if r.random() < 0.05 and x < LIP - 6:
            g.text(x, far - 1, r.choice((".-.", "_.~._", ",.-.")), SNOW_BACK)
    # the lip, with a snow cornice curling over it
    for y in range(far, front + 1):
        g.set(LIP, y, ":" if y % 2 else "|", MOONLIT)
    g.text(LIP - 2, far - 1, "_.-,", SNOW)
    # the drop under the lip: moonlit edge going back under the overhang into the dark, drips hanging off it
    for y in range(front + 1, LH):
        d = y - front
        edge = LIP - min(4, d // 2) + int(1.2 * math.sin(d * 0.9))
        for x in range(edge - 3, edge):
            if 0 <= x < LW and r.random() < 0.5 - d * 0.02:
                g.set(x, y, r.choice(".:'"), MOONLIT if d < 6 else ROCK_DARK)
        g.set(edge, y, r.choice("|\\|)") if d > 1 else "\\", MOONLIT if d < 8 else ROCK_DARK)
        for x in range(edge + 1, LW):
            g.c[y][x] = None
    for x, n in ((LIP - 1, 2), (LIP - 3, 1), (LIP - 6, 2)):
        for k in range(n):
            g.set(x, front + 1 + k, "V" if k == n - 1 else "|", SNOW_DIM)
    return g


def build_flank():
    """The mountain's lower slopes going down to the right into the cloud sea, a little moonlit snow on the ridges."""
    r = random.Random(92)
    g = Grid(FW, FH)
    tops = []
    for x in range(FW):
        t = 0.5 + x * 0.09 + 0.7 * math.sin(x * 0.21 + 1.5) + 0.4 * math.sin(x * 0.5)
        tops.append(t)
    for x in range(FW):
        t = int(round(tops[x]))
        nxt = int(round(tops[min(FW - 1, x + 1)]))
        for y in range(max(0, t + 1), FH):
            g.blank(x, y, x, y, FILL)
            d = y - t
            if d == 1 and r.random() < 0.35:
                g.set(x, y, r.choice(".:'"), SNOW_DIM if x < 60 else SNOW_BACK)
            elif r.random() < 0.025:
                g.set(x, y, r.choice(".'`"), ROCK_DARK)
        if 0 <= t < FH:
            g.set(x, t, "_" if nxt == t else ("\\" if nxt > t else "/"), MIDG if x < 70 else ROCK_DARK)
    return g, tops


def build_sprites(ex):
    """His frames, seven wide and six tall with his feet (or seat) on the fourth row, plus his sword in the rock, the
    bud, his breath, a star and the glint far below."""
    sw = {"│": STEEL, "┼": STEEL, "─": STEEL}
    pad = lambda rows: [r.ljust(7) for r in rows] + ["       "] * (6 - len(rows))
    walk = [["      ", " O │  ", "/|\\┼  ", " >\\   "], ["      ", " O │  ", "/|\\┼  ", " |\\   "],
            ["      ", " O │  ", "/|\\┼  ", " |>   "], ["      ", " O │  ", "/|\\┼  ", "/ \\   "]]
    frames = [pad(f) for f in walk]                                                          # 0-3 walking
    frames += [pad(["      ", " O │  ", "/|\\┼  ", "/ \\   "]),                                # 4 standing
               pad(["  │   ", " O┼   ", "/|    ", "/ \\   "]),                                # 5 raising it
               pad(["      ", " O    ", "/|\\_  ", "/ \\┼  "]),                               # 6 driving it in
               pad(["      ", " O    ", "/|\\   ", "/ \\   "]),                                # 7 empty-handed
               # sitting the way the game draws it (head over body and thigh), legs over the drop not drawn
               ["       ", "       ", "   O   ", "  /|_  ", "       ", "       "],               # 8 sitting
               ["       ", "       ", "   O   ", "  /|_  ", "       ", "       "],               # 9 (the same)
               ["       ", "       ", "   O   ", "  >|_  ", "       ", "       "],               # 10 a hand inside his coat
               pad(["      ", " O/   ", "/|    ", "/ \\   "]),                                # 11 standing, holding it up
               pad(["      ", "  O   ", " /|\\  ", "/ \\   "]),                                # 12 leaning out: feet put, head and body over
               pad(["      ", "   O  ", " ¯/|  ", " |\\   "]),                                # 13 getting up
               pad(["      ", "   O  ", " ¯/|_ ", " |\\ ┼ "]),                              # 14 reaching for it
               pad(["      ", " O    ", "/|\\   ", " >\\   "]),                               # 15-16 walking, empty-handed
               pad(["      ", " O    ", "/|\\   ", " |\\   "]),
               pad(["      ", " O    ", "/|¯   ", "/ \\   "]),                                # 17 holding it out in front, looking at it
               pad(["      ", " O    ", "<|\\   ", "/ \\   "])]                               # 18 a hand into his coat, standing
    g = frames_of(frames, CHAR, sw)
    ex.piece("hero", g)
    ex.piece("heroL", mirror(g))
    ex.piece("sword", frames_of([["┼", "│"]], STEEL))
    bloom, _ = game_piece([K.BLOOM], "#c8e0b0")
    ex.piece("bloom", bloom)
    ex.value("bloomW", bloom[0].w)
    ex.value("bloomH", bloom[0].h)
    ex.piece("breath", frames_of([["."], ["'"], ["`"]], "#8a949a"))
    ex.piece("star", frames_of([["+"], ["·"], ["*"]], "#c8ccd4"))
    ex.piece("glint", frames_of([["*"], ["+"], ["·"]], GOLD))


def main():
    pkg = sys.argv[1]
    os.makedirs(pkg, exist_ok=True)
    head = "// Generated by tools/build_scene9.py. Don't edit by hand; change the script and rebuild.\n"
    ex = Exporter(head)
    ex.piece("ledge", [build_ledge()])
    ex.value("seat", SEAT)
    ex.value("lip", LIP)
    flank, tops = build_flank()
    ex.piece("flank", [flank])
    # the slope's top row per column, for the glint to creep up along
    ex.value("flankTop", [int(round(t)) for t in tops])
    build_sprites(ex)
    n = ex.write(os.path.join(pkg, "Art9Ledge.txt"))
    print(f"Art9Ledge {n} bytes")


if __name__ == "__main__":
    main()
