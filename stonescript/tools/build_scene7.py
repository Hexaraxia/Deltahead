"""Builds the art for scene 7 (the mountain heights).

    python -I build_scene7.py <package dir>

Writes Art7Heights.txt, Art7Sprites.txt and the shared ArtSky.txt: a ridge over the cloud sea toward a summit
that never gets closer, rock pillars where the path runs out, the green aurora, and Hans's signposts at the fork.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_scene1 import Grid, Exporter, frames_of, FAR, BACK, MIDG, GROUND, NEAR, TEX, ROCKC, DIMC
import place_frames as P

SNOW = "#dfe6ea"
SNOW_DIM = "#9aa6ac"
SNOW_BACK = "#6c767e"       # the path's far edge, in shadow
FOG = "#6b7680"
FOG_DIM = "#454e56"
STAR = "#c8ccd4"
GREEN = "#32da5a"           # the tier
GREEN_MID = "#1f9a40"
GREEN_DIM = "#136328"
WOOD = "#8a7656"
SIGN = "#c8bfa8"
CRATE = "#8a7a5a"
FAR_EDGE = "#3e4752"        # far ranges
FAR_LIT = "#4e5864"
FAR_FILL = "#161a1f"
BACK_EDGE = "#4a525c"       # nearer ridge behind the path
BACK_FILL = "#101317"
NEAR_EDGE = "#2c3238"       # rocks close to the camera
NEAR_FILL = "#08090b"

WW, WH = 400, 44
FEET0, FEET1 = 26, 18       # path row at x=0 and x=WW, it climbs as it goes
# gaps in the path, the scene raises a pillar every PILLAR_W columns to fill them
GAPS = [(70, 100), (150, 190), (262, 400)]
PILLAR_W = 5
PILLAR_H = 40
FORK = 222                  # the signposts


def feet(x):
    return FEET0 + (FEET1 - FEET0) * x / WW


def in_gap(x):
    return any(a <= x < b for a, b in GAPS)


# rows behind and in front of his feet, about as deep as the game's own ground
BACK, FRONT = 3, 3


def band(g, x, rr, row):
    """One column of the path at x, his feet on row `row`: far edge, snow, lit near edge. Also the pillar tops."""
    sub = feet(x) - math.floor(feet(x))
    top = row - BACK
    # far edge as a solid line so the back of the path reads
    g.set(x, top, "_" if rr.random() < 0.75 else rr.choice("-_."), SNOW_BACK)
    for y in range(top + 1, row + FRONT):
        g.blank(x, y, x, y, TEX)
        if rr.random() < 0.11:
            g.set(x, y, rr.choice("_-¯.'`"), SNOW_BACK if y < row else SNOW_DIM)
    g.set(x, row + FRONT, "¯" if sub < 0.34 else ("-" if sub < 0.67 else "_"), SNOW)


def build_ridge():
    """The ridge he walks along, with gaps, the signposts at the fork and the lost crate."""
    r = random.Random(71)
    g = Grid(WW, WH)
    for x in range(WW):
        if in_gap(x):
            continue
        row = int(math.floor(feet(x)))
        band(g, x, r, row)
        depth = 7 + int(3 * math.sin(x * 0.11) + 2 * math.sin(x * 0.37))
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
        # boulders and drifts along the far edge
        if r.random() < 0.05 and not in_gap(x + 4):
            g.text(x, row - BACK - 1, r.choice((".-.", "_.~._", ",.-.")), SNOW_BACK)
    # cut ends of the path at the gaps
    for a, b in GAPS:
        for x, ch in ((a - 1, "\\"), (b, "/")):
            if 0 <= x < WW:
                row = int(math.floor(feet(x)))
                for y in range(row - BACK + 1, row + FRONT):
                    g.set(x, y, ":" if (y + x) % 2 else "|", MIDG)
                g.set(x, row + FRONT + 1, ch, MIDG)
                g.set(x, row + FRONT + 2, "'", TEX)
    sx = FORK
    row = int(math.floor(feet(sx)))
    signs = [" .------------------.",
             " | FAERIE KINGDOM  >|",
             " '------------------'",
             ".------------------. ",
             "|< THE DISTANT LAND | ",
             "'------------------' "]
    for j, s in enumerate(signs):
        y = row - BACK - 9 + j
        a, b = len(s) - len(s.lstrip()), len(s.rstrip()) - 1
        g.blank(sx - 10 + a, y, sx - 10 + b, y, WOOD)
        for i, ch in enumerate(s):
            if ch != " ":
                g.set(sx - 10 + i, y, ch, SIGN if ch.isalpha() or ch in "<>" else WOOD)
    # the post, on the far edge
    for y in range(row - BACK - 3, row - BACK + 1):
        g.set(sx, y, "|", WOOD)
    for k in range(1, 10):
        g.set(sx + 1 + k * 2, row + FRONT + 1 + k, ".", DIMC)
        g.set(sx - 1 - k * 2, row + FRONT + 1 + k, ".", DIMC)
    cx = FORK + 14
    row = int(math.floor(feet(cx)))
    for j, s in enumerate(["┌───┐", "│≡≡≡│", "└───┘"]):
        g.blank(cx, row - 3 + j, cx + 4, row - 3 + j, CRATE)
        g.text(cx, row - 3 + j, s, CRATE)
    return g


def build_sky():
    """The night sky, shared with scene 6 (ArtSky.txt) so the camera can pan from one scene to the next without a
    jump. The moon is its own piece, the scenes keep it still on screen."""
    r = random.Random(72)
    s = Grid(200, 70)
    for _ in range(380):
        x, y = r.randrange(s.w), r.randrange(0, s.h)
        b = r.random()
        s.set(x, y, r.choice(".·") if b < 0.85 else "+", FAR if b < 0.55 else STAR)
    return s


def build_moon():
    """The moon over the Cross Deadwood River, the film's one moon."""
    rows = P.RIVER_MOON
    g = Grid(max(len(r) for r in rows), len(rows))
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == " ":
                g.blank(i, j, i, j, "#e8e4d4")
            elif ch != "#":
                g.set(i, j, ch, "#e8e4d4")
    return g


def peak(g, px, base, h, lit_left, r, edge, lit, fill, snow=True, lit_p=0.3):
    """A peak h rows tall standing on row base, lit on one side, with a snow cap."""
    for k in range(h):
        y = base - h + k
        x0, x1 = px - k - 1, px + k
        g.blank(x0 + 1, y, x1 - 1, y, fill)
        for x in range(x0 + 1, x1):
            if (x < px) == lit_left and r.random() < lit_p:
                g.set(x, y, r.choice(".:'") if k < 3 and snow else r.choice(".'"), SNOW_DIM if k < 3 and snow else lit)
        g.set(x0, y, "/", SNOW_DIM if k < 2 and snow else edge)
        g.set(x1, y, "\\", SNOW_DIM if k < 2 and snow else edge)


def build_far():
    """Far ranges and the cloud sea. The scene moves this a quarter as fast as the path."""
    r = random.Random(77)
    g = Grid(260, 20)
    sea = 14
    for px, h in ((18, 3), (52, 5), (95, 4), (138, 6), (180, 3), (222, 5)):
        peak(g, px, sea, h, px > 30, r, FAR_EDGE, FAR_LIT, FAR_FILL, lit_p=0.12)
    for y in range(sea - 1, g.h):
        for x in range(g.w):
            top = sea + 0.8 * math.sin(x * 0.11) + 0.5 * math.sin(x * 0.29 + 1)
            if y >= top:
                g.blank(x, y, x, y, "#1a1f26")
                if y - top < 1:
                    g.set(x, y, r.choice("_.-~"), "#6c7888")
                elif r.random() < 0.1:
                    g.set(x, y, r.choice("~-.'"), "#36404a")
    return g


def build_back():
    """A nearer ridge behind the path, moving at 0.6 the path's rate."""
    r = random.Random(78)
    g = Grid(320, 18)
    tops = []
    for x in range(g.w):
        t = 6 + 2.5 * math.sin(x * 0.05) + 1.5 * math.sin(x * 0.17 + 2) + (2 if (x // 23) % 3 == 0 else 0) * math.sin(x * 0.4)
        tops.append(t)
    for x in range(g.w):
        t = int(round(tops[x]))
        nxt = int(round(tops[min(g.w - 1, x + 1)]))
        for y in range(t + 1, g.h):
            g.blank(x, y, x, y, BACK_FILL)
            d = y - t
            if d == 1 and r.random() < 0.3:
                g.set(x, y, r.choice(".:'"), "#4e565e")
            elif r.random() < 0.02:
                g.set(x, y, r.choice(".'`"), "#22272c")
        g.set(x, t, "_" if nxt == t else ("\\" if nxt > t else "/"), BACK_EDGE)
    return g


def build_mist():
    """Cloud at the nearer ridge's foot, behind the path."""
    r = random.Random(79)
    c = Grid(360, 6)
    for y in range(c.h):
        for x in range(c.w):
            w = 0.5 + 0.5 * math.sin(x * 0.06 + y)
            if r.random() < 0.14 * w * (1 - abs(y - 3) / 3.5):
                c.set(x, y, r.choice("~-._~"), "#3e4852" if y < 3 else "#2c333b")
    return c


def build_near():
    """Dark rocks along the bottom, close to the camera. The scene moves them 1.5x as fast as the path."""
    r = random.Random(80)
    g = Grid(640, 12)
    x = 20
    while x < g.w - 20:
        w, h = r.randint(8, 18), r.randint(4, 9)
        for i in range(w):
            u = i / (w - 1)
            top = g.h - int(round(h * math.sin(math.pi * u) ** 0.6)) - 1
            for y in range(top + 1, g.h):
                g.blank(x + i, y, x + i, y, NEAR_FILL)
            g.set(x + i, top, "_" if 0.3 < u < 0.7 else ("/" if u < 0.5 else "\\"), NEAR_EDGE)
            if r.random() < 0.5 and 0.15 < u < 0.85:
                g.set(x + i, top + 1, r.choice(".'`"), "#4a5258")
        x += w + r.randint(40, 90)
    return g


def build_summit():
    """The summit far off on the horizon. It stays put on screen however far he walks."""
    r = random.Random(73)
    w, h = 19, 8
    g = Grid(w, h)
    c = w // 2
    for y in range(h):
        half = (y + 0.5) * 1.05 + 0.6 * math.sin(y * 1.3)
        x0, x1 = int(round(c - half)), int(round(c + half))
        for x in range(max(0, x0 + 1), min(w, x1)):
            g.blank(x, y, x, y, "#12161b")
            lit = x < c - (y * 0.15)
            if y < 4:
                if r.random() < 0.6:
                    g.set(x, y, r.choice(".:'"), "#c8d0d8" if lit else "#6c7680")
            elif lit and r.random() < 0.45:
                g.set(x, y, r.choice(".'`:"), "#5c6672")
            elif not lit and r.random() < 0.15:
                g.set(x, y, r.choice(".'"), "#2c333b")
        if 0 <= x0 < w:
            g.set(x0, y, "/", "#6c7680" if y > 3 else SNOW)
        if 0 <= x1 < w:
            g.set(x1, y, "\\", "#3e4852" if y > 3 else SNOW_DIM)
    g.text(c - 1, 0, "/\\", SNOW)
    return g


def build_aurora():
    """The green aurora, eight frames looped."""
    frames = []
    for k in range(8):
        a = Grid(200, 14)
        r = random.Random(74 + k)
        ph = k / 8 * 2 * math.pi
        for x in range(a.w):
            foot = 8 + 2.2 * math.sin(x * 0.045 + 1 + ph * 0.25) + 0.9 * math.sin(x * 0.15 - ph)
            glow = max(0.0, 0.5 + 0.5 * math.sin(x * 0.07 - ph) + 0.2 * math.sin(x * 0.23 + ph))
            if glow < 0.15:
                continue
            row = int(math.floor(foot))
            sub = foot - row
            a.set(x, row, "¯" if sub < 0.34 else ("-" if sub < 0.67 else "_"), GREEN if glow > 0.55 else GREEN_MID)
            n = int(2 + 5 * glow)
            for j in range(1, n + 1):
                if r.random() < 0.6 - j / (n + 2):
                    ch = "|" if j == 1 and glow > 0.75 else r.choice("'.:'")
                    a.set(x, row - j, ch, GREEN_MID if j < 3 else GREEN_DIM)
        frames.append(a)
    return frames


def build_pillar():
    """A rock pillar that comes up out of the cloud to carry the path. Its top is the path's band, and it's tall
    enough that its foot is never seen."""
    r = random.Random(75)
    g = Grid(PILLAR_W, PILLAR_H)
    for x in range(PILLAR_W):
        band(g, x, r, BACK)
    for y in range(BACK + FRONT + 1, g.h):
        g.blank(0, y, PILLAR_W - 1, y, TEX)
        g.set(0, y, "|" if y % 4 else ":", MIDG)
        g.set(PILLAR_W - 1, y, "|" if (y + 2) % 4 else "!", "#2c3238")
        if r.random() < 0.5:
            g.set(r.randint(1, PILLAR_W - 2), y, r.choice(".'`:"), ROCKC if y < BACK + FRONT + 5 else TEX)
    for x in range(PILLAR_W):
        g.set(x, BACK + FRONT + 1, r.choice(".:'"), SNOW_DIM)
    return g


def build_puff():
    """Snow puff when a pillar stops, four frames."""
    frames = []
    r = random.Random(81)
    for k in range(4):
        g = Grid(13, 4)
        for _ in range(10 - 2 * k):
            x = 6 + int(round(r.uniform(-1, 1) * (2 + 1.5 * k)))
            y = 3 - int(r.uniform(0, 2.2 - 0.4 * k))
            g.set(x, y, r.choice("'.,:`" if k < 2 else ".`"), SNOW_DIM if k < 2 else FOG)
        frames.append(g)
    return frames


def build_cloud():
    """Cloud in front of the pillars' feet so they come up out of it."""
    r = random.Random(76)
    c = Grid(WW + 60, 12)
    for y in range(c.h):
        for x in range(c.w):
            top = 2 + 1.2 * math.sin(x * 0.07) + 0.8 * math.sin(x * 0.19 + 2)
            if y >= top:
                c.blank(x, y, x, y, "#1c2128")
                if y - top < 1:
                    c.set(x, y, r.choice("_.-~"), FOG)
                elif r.random() < 0.15:
                    c.set(x, y, r.choice("~-.'"), FOG_DIM)
    return c


def crop(g, x0, y0, w, h):
    out = Grid(w, h)
    for y in range(h):
        for x in range(w):
            if 0 <= y0 + y < g.h and 0 <= x0 + x < g.w:
                out.c[y][x] = g.c[y0 + y][x0 + x]
    return out


def main():
    pkg = sys.argv[1]
    os.makedirs(pkg, exist_ok=True)
    head = "// Generated by tools/build_scene7.py. Don't edit by hand; change the script and rebuild.\n"
    ex = Exporter(head)
    ex.value("ww", WW)
    ex.value("feet0", FEET0)
    ex.value("feet1", FEET1)
    ex.value("fork", FORK)
    ex.value("floorBack", BACK)
    ex.value("floorFront", FRONT)
    pillars = [x for a, b in GAPS for x in range(a, min(b, WW), PILLAR_W)]
    ex.value("pillarX", pillars)
    ex.value("gapA", [a for a, _ in GAPS])
    ex.value("gapB", [b for _, b in GAPS])
    ridge = build_ridge()
    ex.piece("ridgeA", [crop(ridge, 0, 0, 200, WH)])
    ex.piece("ridgeB", [crop(ridge, 200, 0, WW - 200, WH)])
    ex.piece("far", [build_far()])
    ex.value("farSea", 14)
    ex.piece("back", [build_back()])
    n1 = ex.write(os.path.join(pkg, "Art7Heights.txt"))
    sky = Exporter(head)
    sky.piece("sky", [build_sky()])
    sky.piece("moon", [build_moon()])
    sky.write(os.path.join(pkg, "ArtSky.txt"))
    ex = Exporter(head)
    ex.piece("summit", [build_summit()])
    frames = build_aurora()
    # one piece per green so the scene can fade each in on its own
    for name, col in (("auroraHi", GREEN), ("auroraMid", GREEN_MID), ("auroraLo", GREEN_DIM)):
        part = []
        for fr in frames:
            g = Grid(fr.w, fr.h)
            for y in range(fr.h):
                for x in range(fr.w):
                    if fr.c[y][x] and fr.c[y][x][1] == col:
                        g.c[y][x] = fr.c[y][x]
            part.append(g)
        ex.piece(name, part)
    ex.piece("pillar", [build_pillar()])
    ex.piece("puff", build_puff())
    ex.piece("cloud", [build_cloud()])
    ex.piece("mist", [build_mist()])
    ex.piece("near", [build_near()])
    ex.piece("flake", frames_of([["."], ["'"], ["·"]], SNOW_DIM))
    n2 = ex.write(os.path.join(pkg, "Art7Sprites.txt"))
    print(f"Art7Heights {n1}, Art7Sprites {n2} bytes; {len(pillars)} pillars")


if __name__ == "__main__":
    main()
