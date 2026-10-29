"""Builds the art for scene 8 (Grudges).

    python -I build_scene8.py <package dir>

Writes Art8Ridge.txt and Art8Sprites.txt: the broken ridge with Hans's line over the gap, him, the Ki creatures
(from kifoe_frames.py) and the Emerald Egg with its Moonbloom bud. The sky and backdrop are scene 7's.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_scene1 import Grid, Exporter, frames_of, mirror, MIDG, TEX, ROCKC, DIMC, CHAR
from build_scene7 import SNOW, SNOW_DIM, SNOW_BACK, FOG, FOG_DIM, BACK, FRONT, crop
import kifoe_frames as K

STEEL = "#c9d1d6"           # his sword
ICE = "#32da5a"             # the Ki creatures: the game tints a foe in its tier's color (green at 16-20 stars)
PLATE = "#a8d4e6"           # the Plated one's armor: ice
EMERALD = "#32da5a"
BUD = "#c8e0b0"

WW, WH = 400, 44
FEET0, FEET1 = 26, 19       # the path's row at x=0 and x=WW: it climbs as it goes
GAP = (156, 186)            # where the ridge has broken away (the Berserkers go down it)
# one of Hans's haul lines across the gap, sagging between two posts. he rides it over
ZIP = (151, 197)            # far post well back from the edge so he lands between them
ZIP_H = 10                  # how high its ends are above the path
ZIP_SAG = 3
ROPE = "#d2b486"
POST = "#8a7656"


def feet(x):
    return FEET0 + (FEET1 - FEET0) * x / WW


def band(g, x, rr, row):
    """One column of the path, as deep as scene 7's: the far edge BACK rows behind his feet (on row), snow, and the
    lit near edge FRONT rows in front."""
    sub = feet(x) - math.floor(feet(x))
    top = row - BACK
    # the far edge as a line you can follow so the back of the path reads
    g.set(x, top, "_" if rr.random() < 0.75 else rr.choice("-_."), SNOW_BACK)
    for y in range(top + 1, row + FRONT):
        g.blank(x, y, x, y, TEX)
        if rr.random() < 0.11:
            g.set(x, y, rr.choice("_-¯.'`"), SNOW_BACK if y < row else SNOW_DIM)
    g.set(x, row + FRONT, "¯" if sub < 0.34 else ("-" if sub < 0.67 else "_"), SNOW)


def build_ridge():
    """The ridge and the rock under it, broken away at GAP, with drifts and boulders along the far edge."""
    r = random.Random(81)
    g = Grid(WW, WH)
    for x in range(WW):
        row = int(math.floor(feet(x)))
        if GAP[0] <= x < GAP[1]:
            # looking down through it into dark mist, not sky
            for y in range(row - BACK, WH):
                g.blank(x, y, x, y, "#0b0d10")
                if r.random() < 0.05 * (y - row + BACK) / 12:
                    g.set(x, y, r.choice("~-.'"), FOG_DIM)
            continue
        band(g, x, r, row)
        depth = 7 + int(3 * math.sin(x * 0.13) + 2 * math.sin(x * 0.41))
        for y in range(row + FRONT + 1, min(WH, row + FRONT + depth)):
            g.blank(x, y, x, y, TEX)
            d = y - row - FRONT
            p = r.random()
            if d == 1 and p < 0.6:
                g.set(x, y, r.choice(".:'"), SNOW_DIM)
            elif d < 4 and p < 0.3:
                g.set(x, y, r.choice("|'!:"), ROCKC)
            elif p < 0.08:
                g.set(x, y, r.choice(".'`"), TEX)
        g.set(x, min(WH - 1, row + FRONT + depth), r.choice("'`.,"), FOG_DIM)
        if r.random() < 0.05 and not (GAP[0] - 6 <= x < GAP[1]):
            g.text(x, row - BACK - 1, r.choice((".-.", "_.~._", ",.-.")), SNOW_BACK)
    # the broken edges: the floor's cut end, and the rock showing where it sheared off
    for x, ch in ((GAP[0] - 1, "\\"), (GAP[1], "/")):
        row = int(math.floor(feet(x)))
        for y in range(row - BACK + 1, row + FRONT):
            g.set(x, y, ":" if (y + x) % 2 else "|", MIDG)
        for k in range(4):
            g.set(x, row + FRONT + 1 + k, ch if k == 0 else r.choice("|!:"), MIDG)
    # Hans's line across it: a post each side, the cable sagging between their tops
    xa, xb = ZIP
    for x in (xa, xb):
        row = int(math.floor(feet(x)))
        for y in range(row - ZIP_H + 1, row + 1):
            g.set(x, y, "|", POST)
        g.text(x - 1, row - ZIP_H, "─┬─", POST)
        # a brace on its outer side, against the pull of the line
        g.set(x - 1 if x == xa else x + 1, row, "/" if x == xa else "\\", POST)
    for x in range(xa + 1, xb):
        y = cable_row(x)
        sub = y - math.floor(y)
        g.set(x, int(math.floor(y)), "¯" if sub < 0.34 else ("-" if sub < 0.67 else "_"), ROPE)
    return g


def cable_row(x):
    """Where the haul line is at x (a row, with its fraction): from one post's top to the other's, sagging."""
    xa, xb = ZIP
    ya, yb = math.floor(feet(xa)) - ZIP_H, math.floor(feet(xb)) - ZIP_H
    u = (x - xa) / (xb - xa)
    return ya + (yb - ya) * u + ZIP_SAG * math.sin(math.pi * u)


def game_piece(anims, col):
    """Turns the game's frames (lists of (text, hold)) into same-size grids, lined up bottom and right so the backs
    match (they face left). Returns the grids and where each animation starts."""
    texts, starts = [], []
    for anim in anims:
        starts.append(len(texts))
        texts += [t.rstrip("\n") for t, _ in anim]

    def right(t):
        return max(max((i for i, ch in enumerate(row) if ch != "#"), default=-1) for row in t.split("\n"))
    w = max(right(t) for t in texts) + 1
    h = max(len(t.split("\n")) for t in texts)
    grids = []
    for t in texts:
        rows = t.split("\n")
        ox, oy = w - 1 - right(t), h - len(rows)
        g = Grid(w, h)
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == "#":
                    continue
                if ch == " ":
                    g.blank(ox + i, oy + j, ox + i, oy + j, col)
                else:
                    g.set(ox + i, oy + j, ch, col)
        grids.append(g)
    return grids, starts


def slurper_walk():
    """The Ki Slurper's walk from two whole-body frames, since the game builds its walk from body parts: standing
    (end of its lick) and the same with the legs from lick frame 4."""
    a = K.SLURPER_LICK[20][0]
    b = K.SLURPER_LICK[3][0]
    ra, rb = a.split("\n"), b.split("\n")
    return [(a, 1), ("\n".join(ra[:5] + rb[5:]), 1)]


def build_hero():
    """Him with his sword: scene 2's frames, the fight poses, hanging from his sword on the line, and scene 10's
    guard, block and run."""
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
            ["      ", "      ", "│ _\\O ", "┼|\\/  "],                                         # 11 bent low (the game's pickup)
            ["      ", "O  │  ", "\\\\┼   ", " >\\   "],                                         # 12 knocked back
            ["      ", "    O ", "──┼/¯ ", "  / > "],                                         # 13 dash
            ["  │   ", " O┼   ", "/|    ", " />   "],                                         # 14 leap
            ["  O   ", " /|\\  ", " /┼\\  ", "  │   "],                                         # 15 plunge
            ["      ", "      ", "  O┼  ", " /|\\│ "],                                         # 16 crouched
            ["      ", "   O  ", "──┼|\\ ", "  / \\ "],                                        # 17 blade round behind
            ["      ", "\\O/│  ", " |    ", "/ \\   "],                                         # 18 thrown
            ["      ", "      ", "      ", "O<─<┼─"],                                         # 19 flat on his back
            [" ─┼── ", " \\O/  ", "  |   ", " / \\  "],                                        # 20 hanging from his sword
            [" ─┼── ", " \\O/  ", "  |   ", "  />  "],                                         # 21 the same, legs swinging
            ["      ", " O │  ", "/|\\┼  ", "/ \\   "],                                          # 22 on guard
            ["    / ", " O ┼  ", "/|/   ", "/ \\   "],                                          # 23 blade up across him
            # running (scene 10), blade trailing like the dash
            ["      ", "    O ", "──┼/¯ ", "  / > "], ["      ", "    O ", "──┼/¯ ", "   |> "],
            ["      ", "    O ", "──┼/¯ ", "  < \\ "], ["      ", "    O ", "──┼/¯ ", "   |\\ "]]       # 24-27
    return frames_of(hero, CHAR, sw)


def build_plates(gob, rest):
    """The Plated Gobbler's armor as an overlay: three, two, then one ice slab over its front, covering the row his
    blade hits (second from the bottom) and the two above."""
    g0 = gob[rest]
    # its front edge on each of those rows: the first drawn cell
    front = {}
    for y in (4, 5, 6):
        front[y] = min(x for x in range(g0.w) if g0.c[y][x] and g0.c[y][x][0] != " ")
    slabs = [(4, "[=="), (5, "[=]"), (6, "[==")]
    frames = []
    for n in (3, 2, 1):
        g = Grid(g0.w, g0.h)
        for y, s in slabs[3 - n:]:
            g.text(front[y] - 1, y, s, PLATE)
        frames.append(g)
    return frames


def build_cuts():
    """Cuts across a Ki Eater's body, none to five, for the one that heals: bright where the blade went through."""
    r = random.Random(83)
    spots = [(4, 1, "/"), (6, 2, "'"), (5, 1, "\\"), (3, 2, "/"), (7, 1, "'")]
    frames = []
    for n in range(6):
        g = Grid(9, 3)
        for x, y, ch in spots[:n]:
            g.set(x, y, ch, "#ffffff")
        frames.append(g)
    return frames


def build_fx():
    """Little things: a hit (a burst, a spark, dying out), a shard of ice armor, a green mote of healing."""
    hit = frames_of([["\\|/", "-*-", "/|\\"], [" . ", ".+.", " ' "], ["   ", " ' ", "   "]], "#ffffff")
    shard = frames_of([["[="], ["=]"], ["-"], ["."]], PLATE)
    mote = frames_of([["+"], ["'"], ["."]], EMERALD)
    return hit, shard, mote


def build_action():
    """For the big moments: an impact (a star of lines, breaking up), the arc of his blade in front of him as it goes
    round, and the streaks behind something going fast."""
    burst = frames_of([["\\   |   /", "  \\ | /  ", "--  *  --", "  / | \\  ", "/   |   \\"],
                       ["    .    ", " '  |  ' ", "- -   - -", " .  |  . ", "    '    "],
                       ["         ", "  .   .  ", "         ", "  '   '  ", "         "]], "#ffffff")
    slash = frames_of([["`.  ", "  \\ ", "  / ", ".'  "]], "#ffffff")
    lines = frames_of([["-- ---  ", "  ---  -", " -  --- "], ["---  -- ", " -  --- ", "--  -   "]], "#6a7076")
    return burst, slash, lines


def build_egg():
    """The Emerald Egg rocking, cracking, then open with a broken rim (the top is the shell piece)."""
    rock = [K.EGG[0][0], K.EGG[1][0]]
    frames, _ = game_piece([[(t, 1) for t in rock]], EMERALD)
    w = frames[0].w
    for rows in ([" ,(. ", ":/ ):", "'.;:'"], ["     ", ":`´`:", "'.;:'"]):
        g = Grid(w, frames[0].h)
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch != " ":
                    g.set(w - len(row) + i, j, ch, EMERALD)
        frames.append(g)
    return frames


def build_shell():
    """The top of the egg's shell, tumbling as it flies off."""
    return frames_of([[",(."], ["(.´"], [".´,"], ["´,("]], EMERALD)


def main():
    pkg = sys.argv[1]
    os.makedirs(pkg, exist_ok=True)
    head = "// Generated by tools/build_scene8.py. Don't edit by hand; change the script and rebuild.\n"
    ex = Exporter(head)
    ex.value("ww", WW)
    ex.value("feet0", FEET0)
    ex.value("feet1", FEET1)
    ex.value("gapA", GAP[0])
    ex.value("gapB", GAP[1])
    ex.value("floorBack", BACK)
    ex.value("floorFront", FRONT)
    ridge = build_ridge()
    ex.piece("ridgeA", [crop(ridge, 0, 0, 200, WH)])
    ex.piece("ridgeB", [crop(ridge, 200, 0, WW - 200, WH)])
    ex.value("zipA", ZIP[0])
    ex.value("zipB", ZIP[1])
    ex.value("zipH", ZIP_H)
    ex.value("zipSag", ZIP_SAG)
    n1 = ex.write(os.path.join(pkg, "Art8Ridge.txt"))

    ex = Exporter(head)
    hero = build_hero()
    ex.piece("hero", hero)
    ex.piece("heroL", mirror(hero))
    eater, es = game_piece([K.EATER_WAKE, K.EATER_WALK, K.EATER_BITE], ICE)
    ex.piece("eater", eater)
    ex.piece("eaterR", mirror(eater))
    ex.value("eWake", es[0])
    ex.value("eWalk", es[1])
    ex.value("eBite", es[2])
    ex.value("eW", eater[0].w)
    ex.value("eH", eater[0].h)
    gob, gs = game_piece([K.GOBBLER_WAKE, K.GOBBLER_WALK, K.GOBBLER_BITE], ICE)
    ex.piece("gobbler", gob)
    ex.value("gWake", gs[0])
    ex.value("gWalk", gs[1])
    ex.value("gBite", gs[2])
    ex.value("gW", gob[0].w)
    ex.value("gH", gob[0].h)
    ex.piece("plates", build_plates(gob, gs[2] + 16))
    slur, ss = game_piece([K.SLURPER_WAKE, K.SLURPER_LICK, K.SLURPER_DEAD, slurper_walk()], ICE)
    ex.piece("slurper", slur)
    ex.value("sWake", ss[0])
    ex.value("sLick", ss[1])
    ex.value("sDead", ss[2])
    ex.value("sWalk", ss[3])
    ex.value("sW", slur[0].w)
    ex.value("sH", slur[0].h)
    ex.piece("cuts", build_cuts())
    hit, shard, mote = build_fx()
    ex.piece("hit", hit)
    ex.piece("shard", shard)
    # not cropped, the scene draws these in the game's rainbow and it runs across the page
    ex.piece("mote", mote, crop=False)
    burst, slash, lines = build_action()
    ex.piece("burst", burst, crop=False)
    ex.piece("slashR", slash)
    ex.piece("slashL", mirror(slash))
    ex.piece("lines", lines)
    egg = build_egg()
    ex.piece("egg", egg)
    ex.value("eggW", egg[0].w)
    ex.piece("shell", build_shell())
    bud, _ = game_piece([K.BUD], BUD)
    ex.piece("bud", bud)
    ex.value("budW", bud[0].w)
    ex.value("budH", bud[0].h)
    n2 = ex.write(os.path.join(pkg, "Art8Sprites.txt"))
    print(f"Art8Ridge {n1}, Art8Sprites {n2} bytes; eater {eater[0].w}x{eater[0].h}, gobbler {gob[0].w}x{gob[0].h}, "
          f"slurper {slur[0].w}x{slur[0].h}")


if __name__ == "__main__":
    main()
