"""Builds the art for scene 5 (the Perilous Climb).

    python -I build_scene5.py <package dir>

Writes Art5Climb.txt and Art5Sprites.txt: switchback ledges up a cliff in the cloud, fallen and frozen Pushers,
the snowy crest, and the night sky over it (no sun, it's the Dark World).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_scene1 import (Grid, Exporter, frames_of, mirror, edge_glyph, FAR, BACK, MIDG, GROUND, NEAR, CHAR, TEX,
                          ROCKC, DIMC)
from build_scene3 import crop
import controller_frames as CTRLF
import place_frames as P

SNOW = "#dfe6ea"
SNOW_DIM = "#9aa6ac"
ICE = "#a9c4cf"
ICE_DIM = "#6f8a96"
FOG = "#6b7680"
FOG_DIM = "#454e56"
MOONLIT = "#c8d2dc"          # cloud tops under the moon
YELLOW = "#ffff62"          # the tier
STAR = "#c8ccd4"
CHESTC = "#a08a64"

WW, WH = 120, 132
# the trail he walks, by the row his feet are on
PATH = [(18, 120), (88, 110), (92, 106), (30, 96), (25, 96), (27, 92), (88, 82), (92, 78), (86, 77), (61, 73),
        (30, 68), (27, 64), (24, 61), (46, 59)]
LEDGES = [((18, 120), (88, 110)), ((92, 106), (30, 96)), ((30, 96), (13, 96)), ((27, 92), (88, 82)),
          ((92, 78), (30, 68))]
STAIRS = [((88, 110), (92, 106)), ((25, 96), (27, 92)), ((88, 82), (92, 78)), ((30, 68), (24, 61))]
CREST_ROW = 60              # top of the ridge, roughly
TUNNEL = (12, 22, 116, 120) # haul tunnel mouth: x0, x1, y0, y1
OMEGA_X = 16                # Omega chest's left edge, on the landing at the end of the second ledge
FALLEN = ((66, 1), (58, 2))         # fallen Pushers: x, which ledge (0-based)
FROZEN = ((72, 4), (47, 4))         # frozen ones higher up
SNOW_FROM = 88                      # ledges above this row have snow on them
LASH_SEG = 5                        # trail stretch the Dominotaur lashes along...
D_STOP = 31                         # ...standing here on it
GONE = 2                            # STAIRS index of the stairs that give way behind him
GONE_BOX = (80, 75, 96, 85)         # cliff part the scene redraws after that: x0, y0, x1, y1


def feet_at(x, a, b):
    (x0, y0), (x1, y1) = a, b
    u = (x - x0) / (x1 - x0)
    return y0 + (y1 - y0) * u


def wall(y):
    """The cliff's left and right edges at row y."""
    return (12 + int(round(1.5 * math.sin(y * 0.11) + 0.7 * math.sin(y * 0.37))),
            108 + int(round(1.5 * math.sin(y * 0.09 + 2) + 0.7 * math.sin(y * 0.31 + 1))))


def crest(x):
    return CREST_ROW + int(round(1.6 * math.sin(x * 0.09) + 0.8 * math.sin(x * 0.23 + 1)))


def build_cliff():
    r = random.Random(131)
    mid = Grid(WW, WH)
    # the cliff, wandering sides, the crest on top
    for y in range(CREST_ROW - 3, WH):
        a, b = wall(y)
        for x in range(a, b + 1):
            if y < crest(x):
                continue
            mid.blank(x, y, x, y, TEX)
            if r.random() < 0.02:
                mid.set(x, y, r.choice(".'`:"), TEX)
        mid.set(a, y, edge_glyph(wall(y - 1)[0], a, wall(y + 1)[0], True), MIDG)
        mid.set(b, y, edge_glyph(wall(y - 1)[1], b, wall(y + 1)[1], False), MIDG)

    def bare(x, y):
        # rock face cell with nothing on it yet
        return (0 <= y < WH and wall(y)[0] < x < wall(y)[1] and y > crest(x) and mid.c[y][x] is not None
                and mid.c[y][x][0] == " ")

    # strata, broken wavy lines across the face like the game draws them
    for k, y0 in enumerate(range(CREST_ROW + 4, WH, 5)):
        ph = r.random() * 6
        x = wall(y0)[0] + 1
        while x < wall(y0)[1]:
            run, gap = r.randint(4, 14), r.randint(4, 16)
            for i in range(run):
                xx = x + i
                h = y0 + 1.3 * math.sin(xx * 0.07 + ph) + 0.6 * math.sin(xx * 0.19 + k)
                row = int(math.floor(h))
                sub = h - row
                if bare(xx, row):
                    mid.set(xx, row, "¯" if sub < 0.34 else ("-" if sub < 0.67 else "_"), TEX)
            x += run + gap
    # cracks
    for _ in range(45):
        x, y = r.randint(16, 104), r.randint(CREST_ROW + 3, WH - 6)
        for k in range(r.randint(2, 5)):
            dx = r.choice((-1, 0, 0, 1))
            if bare(x, y):
                mid.set(x, y, "|" if dx == 0 else ("/" if dx < 0 else "\\"), TEX)
            x, y = x + dx, y + 1
    # knobs, lit on top
    for _ in range(16):
        x, y = r.randint(18, 100), r.randint(CREST_ROW + 4, WH - 8)
        w = r.randint(3, 6)
        if all(bare(x + i, y) and bare(x + i, y + 1) for i in range(w + 2)):
            mid.text(x, y, "." + "-" * w + ".", ROCKC)
            mid.text(x, y + 1, "`" + "." * (w // 2) + "'", TEX)

    # the crest, with drifts like the game's dunes
    for x in range(wall(CREST_ROW)[0] - 2, wall(CREST_ROW)[1] + 3):
        c = crest(x)
        dy = crest(x + 1) - c
        mid.set(x, c, "_" if dy == 0 else ("\\" if dy > 0 else "/"), SNOW)
        # thick bright snow cap so it stands out from the sky behind
        mid.set(x, c + 1, r.choice(".'-.:"), SNOW if r.random() < 0.6 else SNOW_DIM)
        if r.random() < 0.55:
            mid.set(x, c + 2, r.choice(":.'`"), SNOW_DIM)
        if r.random() < 0.25:
            mid.set(x, c + 3, r.choice(".'`"), MIDG)
    for dx in (34, 58, 84):
        mid.text(dx, crest(dx) - 1, ".-.", SNOW)
        mid.text(dx - 1, crest(dx), "(`'::.", SNOW_DIM)

    # ledges: lit top under his feet (snowy higher up), shadow underneath
    def ledge(a, b):
        x0, x1 = sorted((a[0], b[0]))
        snowy = min(a[1], b[1]) < SNOW_FROM
        for x in range(x0, x1 + 1):
            # the top, a sloping __--¯¯ line like the game's ground
            h = feet_at(x, a, b) + 1
            row = int(math.floor(h))
            sub = h - row
            mid.set(x, row, "¯" if sub < 0.34 else ("-" if sub < 0.67 else "_"), SNOW if snowy else GROUND)
            # the edge and shadow ribs under it, or icicles and frozen meltwater higher up
            mid.set(x, row + 1, "¯" if r.random() < 0.7 else r.choice(":'."), MIDG)
            if snowy and r.random() < 0.22:
                n = r.choice((1, 1, 2, 2, 3))
                for k in range(n):
                    mid.set(x, row + 2 + k, "|" if k < n - 1 else r.choice("'|"), ICE)
                if r.random() < 0.3:
                    for k in range(r.randint(2, 6)):
                        if mid.c[row + 2 + n + k][x] and mid.c[row + 2 + n + k][x][0] in " .'`:":
                            mid.set(x, row + 2 + n + k, r.choice(":|'"), ICE_DIM)
            elif r.random() < 0.4:
                n = r.randint(1, 3)
                for k in range(n):
                    mid.set(x, row + 2 + k, r.choice("||'!") if k < n - 1 else r.choice("'|:"),
                            ROCKC if k < 1 else TEX)
            # drifts
            if snowy and r.random() < 0.12 and x + 4 < x1:
                mid.text(x, row - 1, r.choice((".-.", "_.~._", ".~-.", ",.")), SNOW_DIM)
        # a lip at each end
        mid.set(x0 - 1, int(math.floor(feet_at(x0, a, b))) + 1, ".", GROUND)
        mid.set(x1 + 1, int(math.floor(feet_at(x1, a, b))) + 1, ".", GROUND)

    for a, b in LEDGES:
        ledge(a, b)
    # steps cut in the rock at the turns
    for (xa, ya), (xb, yb) in STAIRS:
        n = ya - yb
        for k in range(n):
            x = xa + int(round((xb - xa) * (k + 1) / n))
            y = ya - k
            mid.set(x, y + 1 - 1, "_", GROUND if y > SNOW_FROM else SNOW)
            mid.set(x + (1 if xb > xa else -1), y, "|", MIDG)

    # haul tunnel mouth
    tx0, tx1, ty0, ty1 = TUNNEL
    for y in range(ty0, ty1 + 1):
        mid.blank(tx0, y, tx1, y, TEX)
        for x in range(tx0, tx1 + 1):
            mid.c[y][x] = (" ", TEX)
    mid.text(tx0, ty0 - 1, "_.-'``'-._", MIDG)
    for y in range(ty0, ty1 + 1):
        mid.set(tx1 + 1, y, "|" if y % 2 else "!", MIDG)

    # fallen Pushers, and the first one's cart on its side with a wheel off
    for x, li in FALLEN:
        a, b = LEDGES[li]
        f = int(math.floor(feet_at(x, a, b)))
        mid.text(x, f, "O<─<", DIMC)
        mid.text(x - 1, f + 1, "`.,", TEX)
    x, li = FALLEN[0]
    a, b = LEDGES[li]
    f = int(math.floor(feet_at(x + 7, a, b)))
    mid.text(x + 6, f - 1, "|¯¯¯|", DIMC)
    mid.text(x + 6, f, "|___|o", DIMC)
    mid.text(x + 13, f, "(o)", TEX)

    # ropes left hanging from pitons, a helmet, a pick
    ROPE = "#8c7a58"
    for x, y, n in ((40, 100, 7), (74, 86, 9), (57, 75, 6)):
        mid.text(x, y, ">-", DIMC)
        for k in range(1, n + 1):
            mid.set(x + 1 + (1 if k % 4 in (1, 2) else 0), y + k, ")" if k % 4 == 1 else ("(" if k % 4 == 3 else "|"),
                    ROPE)
        mid.set(x + 1, y + n + 1, "'", ROPE)
    a, b = LEDGES[3]
    mid.text(50, int(math.floor(feet_at(50, a, b))), ".-.", DIMC)
    mid.text(78, int(math.floor(feet_at(78, a, b))), "─┐", DIMC)

    # frost where the snow starts
    for y in range(CREST_ROW, SNOW_FROM + 3):
        for x in range(wall(y)[0] + 1, wall(y)[1]):
            if bare(x, y) and r.random() < 0.035:
                mid.set(x, y, r.choice(".'`"), SNOW_DIM if r.random() < 0.4 else ICE_DIM)

    # frozen Pushers higher up, like the game's on the Icy Ridge
    frozen = [["     |\\", "    /' \\", "   /  O´|", "  |` /¯ /", " /  /) \\|", "´:.:. .:'`"],
              ["   )`¯\\", "  /  O´|", " |` /¯ \\", " / />  ´|", "´:.:. :'`"]]
    for k, (x, li) in enumerate(FROZEN):
        a, b = LEDGES[li]
        f = int(math.floor(feet_at(x, a, b)))
        art = frozen[k % 2]
        top = f - len(art) + 1
        for j, row in enumerate(art):
            s0, s1 = len(row) - len(row.lstrip()), len(row.rstrip()) - 1
            mid.blank(x + s0, top + j, x + s1, top + j, ICE_DIM)
            for i, ch in enumerate(row):
                if ch != " ":
                    col = CHAR if ch in "O/¯)" and 1 <= j <= len(art) - 2 and i in range(s0 + 2, s1) else ICE
                    if ch in ":.'`´" and j == len(art) - 1:
                        col = SNOW_DIM
                    mid.set(x + i, top + j, ch, col)

    # the Omega chest's landing
    mid.text(13, 97, ".-'¯¯¯¯¯¯¯¯¯¯`-.", GROUND)

    # the sky, kept dim so the crest stands out: stars, the moon, the cloud sea and far peaks
    sky = Grid(WW + 40, 48)
    MOON_X, MOON_Y = 26, 2
    for x in range(sky.w):
        # a faint band of stars across it
        c = 12 - x * 0.085
        for y in range(0, 13):
            d = abs(y - c)
            if d < 3.5 and r.random() < 0.38 * (1 - d / 3.5):
                sky.set(x, y, r.choice(".·.'"), r.choice(("#4a5574", "#5a6584", "#3c4560") if d < 1.5
                                                       else ("#3a4258", "#454e66", "#2f3548")))
    for _ in range(150):
        x, y = r.randrange(sky.w), r.randrange(0, 12)
        b = r.random()
        if b < 0.6:
            sky.set(x, y, r.choice(".·"), "#5a606c")
        elif b < 0.92:
            sky.set(x, y, r.choice(".·'"), "#9aa0ac")
        else:
            sky.set(x, y, r.choice("+*"), "#dfe4ec")
    for j, row in enumerate(P.RIVER_MOON):
        for i, ch in enumerate(row):
            if ch == " ":
                sky.blank(MOON_X + i, MOON_Y + j, MOON_X + i, MOON_Y + j, "#e8e4d4")
            elif ch != "#":
                sky.set(MOON_X + i, MOON_Y + j, ch, "#e8e4d4")
    for y in range(9, 14):
        for x in range(sky.w):
            # moonlit haze over the clouds
            near = 1 - (14 - y) / 5
            under = max(0.0, 1 - abs(x - MOON_X - 3) / 60)
            if r.random() < 0.05 + 0.18 * near * (0.4 + under):
                sky.set(x, y, r.choice(".-'"), "#2a3340" if under < 0.5 else "#36414f")
    for y in range(13, sky.h):
        for x in range(sky.w):
            # the cloud sea, lit on top
            top = 14 + 1.0 * math.sin(x * 0.13) + 0.6 * math.sin(x * 0.31 + 2)
            if y >= top:
                sky.blank(x, y, x, y, "#262d36")
                d = y - top
                lit = max(0.0, 1 - abs(x - MOON_X - 3) / 45)
                if d < 1:
                    sky.set(x, y, r.choice("_.-~"), "#8a97a8" if lit > 0.3 else "#5f6b7a")
                elif d < 2.5 and r.random() < 0.35:
                    sky.set(x, y, r.choice("~-.'"), "#4a5563" if lit > 0.3 else "#3a4450")
                elif r.random() < 0.12:
                    sky.set(x, y, r.choice("~-.'"), "#323b46")
    # far peaks, lit on the moon's side
    for px, h in ((12, 5), (47, 3), (100, 7), (124, 4), (140, 5)):
        lit_left = px > MOON_X
        for k in range(h):
            y = 14 - h + k
            sky.blank(px - k, y, px + k - 1, y, "#1c2229")
            for x in range(px - k, px + k):
                lit = (x < px) == lit_left
                if r.random() < (0.5 if lit else 0.12):
                    sky.set(x, y, r.choice(".:'") if lit else ".", "#7c8794" if lit else "#323a44")
            sky.set(px - k - 1, y, "/", "#b4bec9" if lit_left else "#55606c")
            sky.set(px + k, y, "\\", "#55606c" if lit_left else "#b4bec9")
        sky.text(px - 1, 14 - h - 1, "/\\", SNOW)
        if h > 3:
            sky.text(px - 2 if lit_left else px, 14 - h, ".-" if lit_left else "-.", SNOW_DIM)

    # rock along the bottom, near the camera
    front = Grid(WW, WH)
    for y in range(WH - 4, WH):
        front.blank(0, y, WW - 1, y, TEX)
    for x in range(WW):
        if r.random() < 0.5:
            front.set(x, WH - 4, r.choice("_.-'"), MIDG)
    # that bit of cliff after the stairs give way (scar, broken lip, rubble), laid over it by the scene
    gx0, gy0, gx1, gy1 = GONE_BOX
    gone = Grid(gx1 - gx0 + 1, gy1 - gy0 + 1)
    for y in range(gy0, gy1 + 1):
        for x in range(gx0, gx1 + 1):
            gone.c[y - gy0][x - gx0] = mid.c[y][x]
    (xa, ya), (xb, yb) = STAIRS[GONE]
    n = ya - yb
    for k in range(n):
        x = xa + int(round((xb - xa) * (k + 1) / n))
        y = ya - k
        gone.set(x - gx0, y - gy0, r.choice(",'."), GROUND)
        gone.set(x + 1 - gx0, y - gy0, "/" if k % 2 else ")", ROCKC)
        gone.set(x + 2 - gx0, y - gy0, r.choice(":'"), ICE_DIM)
    gone.set(xb + 2 - gx0, yb - gy0, "'", GROUND)
    foot = int(math.floor(feet_at(xa, *LEDGES[3])))
    gone.text(xa - 5 - gx0, foot - 1, "  .o,", GROUND)
    gone.text(xa - 6 - gx0, foot, ".,(o)'o.", GROUND)
    return mid, sky, front, build_near(r), gone


NEAR_H = 175


def build_near(r):
    """Rock spurs close to the camera at the sides. The scene moves this layer 1.3x the camera so they pass in
    front."""
    near = Grid(WW, NEAR_H)
    for k, y0 in enumerate((70, 86, 101, 117, 133, 148)):
        left = k % 2 == 0
        w, h = r.randint(15, 21), r.randint(5, 8)
        icy = y0 < 110
        reach = []
        for j in range(h):
            u = j / (h - 1)
            reach.append(max(2, int(round(w * (0.55 + 0.45 * math.sin(math.pi * min(1.0, u * 1.3))) * (1 - 0.5 * u)
                                          + r.uniform(-1, 1)))))
        edge = [4 + n if left else 105 - n for n in reach]
        for j in range(h):
            y = y0 + j
            x0, x1 = (4, edge[j]) if left else (edge[j], 105)
            near.blank(x0, y, x1, y, FAR)
            for x in range(x0, x1 + 1):
                if r.random() < 0.08:
                    near.set(x, y, r.choice(".'`"), TEX)
            prev = edge[j - 1] if j > 0 else edge[j]
            nxt = edge[j + 1] if j + 1 < h else edge[j]
            near.set(edge[j], y, edge_glyph(prev, edge[j], nxt, left), BACK)
        # top, underside, icicles up where it's cold
        x0, x1 = (4, edge[0]) if left else (edge[0], 105)
        for x in range(x0, x1):
            near.set(x, y0 - 1, r.choice("_.-") if icy else "_", SNOW_DIM if icy else MIDG)
        x0, x1 = (4, edge[-1]) if left else (edge[-1], 105)
        for x in range(x0, x1 + 1):
            near.set(x, y0 + h, "¯", BACK)
            if icy and r.random() < 0.3:
                n = r.choice((1, 2, 2, 3))
                for q in range(n):
                    near.set(x, y0 + h + 1 + q, "|" if q < n - 1 else "'", ICE_DIM)
    return near


def build_sprites(ex):
    # the game's Omega chest: shut, opening, open
    omega = [[" ___ ", "┼┬Ω┬┼", "└┴─┴┘"], [".───.", "┼┬Ω┬┼", "└┴─┴┘"], ["     ", "┬┬.┬┬", "└┴─┴┘"]]
    ex.piece("omega", frames_of(omega, CHESTC, {"Ω": "#d8d0b0"}))
    ex.piece("rune", frames_of([["(φ)"]], "#b8b4aa"))
    # a thin band of fog
    r = random.Random(5)
    band = Grid(70, 3)
    for y in range(3):
        for x in range(70):
            w = math.sin(math.pi * x / 69)
            if r.random() < 0.28 * w * (1 if y == 1 else 0.5):
                band.set(x, y, r.choice("~-.'"), FOG)
    ex.piece("fog", [band])
    # a twinkling star
    ex.piece("twinkle", frames_of([["."], ["·"], ["+"], ["·"]], "#dfe4ec"))
    # a gust of snow
    gust = []
    for k in range(3):
        g = Grid(26, 3)
        for y in range(3):
            for x in range(26):
                w = math.sin(math.pi * x / 25)
                if r.random() < 0.4 * w * (1.0 if y == 1 else 0.35):
                    g.set(x, y, r.choice("-~-_'.-"), SNOW_DIM if r.random() < 0.6 else FOG)
        gust.append(g)
    ex.piece("gust", gust)
    # the stairs giving way: falling chunks and a dust cloud
    ex.piece("chunk", frames_of([["o"], ["()"], ["."], ["'"], ["°"]], GROUND))
    rr = random.Random(9)
    cdust = []
    for k in range(7):
        g = Grid(15, 6)
        for _ in range(22 - 2 * k):
            x = 7 + int(round(rr.uniform(-1, 1) * (2 + 1.1 * k)))
            y = 5 - int(rr.uniform(0, 2 + 0.5 * k))
            g.set(x, y, rr.choice(":'.,`" if k < 4 else ".`'"), SNOW_DIM if rr.random() < 0.5 else MIDG)
        cdust.append(g)
    ex.piece("cdust", cdust)
    # snow falling
    ex.piece("flake", frames_of([["."], ["'"], ["·"]], SNOW))
    # the Dominotaur (the Controller at the yellow tier), tinted yellow the way the game tints a tier, and mirrored
    b0, b1 = CTRLF.DOMINO_BODY
    # frame 32 has just the whip's handle, for when the scene draws the whip itself
    g = frames_of(CTRLF.DOMINO + [CTRLF.DOMINO_BARE], YELLOW)
    ex.piece("dominoL", g)
    ex.piece("dominoR", mirror(g))
    # one-color copy for his shape in the fog, the scene tints it as he gets closer
    for name, gs in (("dominoSL", g), ("dominoSR", mirror(g))):
        shade = []
        for m in gs:
            s = Grid(m.w, m.h)
            for y in range(m.h):
                for x in range(m.w):
                    if m.c[y][x]:
                        s.c[y][x] = (m.c[y][x][0], CHAR)
            shade.append(s)
        ex.piece(name, shade)
    ex.value("dominoW", g[0].w)
    ex.value("dominoMid", (b0 + b1) // 2)
    # his lash, picking up from the game's frames 21-23: cracks up the ledge at the Pusher's heels, then reels
    # back in. thrown from D_STOP and laid onto the ledge's slope
    import whips
    a, b = PATH[LASH_SEG], PATH[LASH_SEG + 1]
    w = g[0].w
    hand_x = D_STOP + (b0 + b1) // 2 - CTRLF.DOMINO_HAND[0]
    hand_row = math.floor(feet_at(D_STOP, a, b)) - (g[0].h - 1) + CTRLF.DOMINO_HAND[1]
    floor0 = math.floor(feet_at(hand_x, a, b))
    lg, lox, loy, crack = whips.lash(n=27, frames=22, ground=lambda dx: feet_at(hand_x + dx, a, b) - floor0 - 0.79,
                                     hand_y=hand_row - floor0, dir=1, col=YELLOW, keep=8, v=2.0, gravity=0.05,
                                     scale=1.4)
    ex.piece("dLash", lg)
    ex.value("dLashOX", lox)
    ex.value("dLashOY", loy)
    ex.value("dLashCrack", crack)
    ex.value("dLashN", len(lg))
    ex.value("dLashHandX", hand_x)
    ex.value("dLashHandRow", hand_row)
    ex.value("dStop", D_STOP)
    ex.value("lashSeg", LASH_SEG)
    # him shading his eyes, looking up
    ex.piece("lookUp", frames_of([["", " O_ ", "/|\\ ", "/ \\┼"], ["", " O_ ", " |\\ ", "/ \\┼"]], CHAR,
                                 {"┼": "#c9d1d6", "│": "#c9d1d6"}))


def main():
    pkg = sys.argv[1]
    os.makedirs(pkg, exist_ok=True)
    head = "// Generated by tools/build_scene5.py. Don't edit by hand; change the script and rebuild.\n"
    mid, sky, front, near, gone = build_cliff()
    ex = Exporter(head)
    ex.value("pathX", [x for x, _ in PATH])
    ex.value("pathY", [y for _, y in PATH])
    ex.value("crestRow", CREST_ROW)
    ex.value("omegaX", OMEGA_X)
    ex.value("frozenX", [x for x, _ in FROZEN])
    ex.piece("midTop", [crop(mid, 0, 0, WW, 90)])
    ex.piece("midBot", [crop(mid, 0, 90, WW, WH - 90)])
    ex.piece("sky", [sky])
    ex.piece("front", [front])
    ex.piece("near", [near])
    ex.piece("gone", [gone])
    ex.value("goneX", GONE_BOX[0])
    ex.value("goneY", GONE_BOX[1])
    n1 = ex.write(os.path.join(pkg, "Art5Climb.txt"))
    ex = Exporter(head)
    build_sprites(ex)
    n2 = ex.write(os.path.join(pkg, "Art5Sprites.txt"))
    print(f"Art5Climb {n1}, Art5Sprites {n2} bytes")


if __name__ == "__main__":
    main()
