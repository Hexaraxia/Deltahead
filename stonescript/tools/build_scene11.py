"""Builds the art and the fall for scene 11 (the fall).

    python -I build_scene11.py <package dir>

Writes Art11Fall.txt: the end of the shoulder, the O and its streaks, and the O's cell on every frame of every shot,
worked out here so the scene just looks it up and nothing wobbles. The places are scenes 10, 6, 5, 4, 3 and 1's.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_scene1 import Grid, Exporter, frames_of, TEX, ROCKC, CHAR
from build_scene7 import SNOW, SNOW_DIM, SNOW_BACK, FOG_DIM, BACK, FRONT
from build_scene10 import feet, WH

MOONLIT = "#b8c2ca"
ROCK_DARK = "#2a3036"
STREAK = "#6a6f74"

EDGE_X0 = -44               # the end of the shoulder, left of where scene 10's snowfield starts
LIP = -30                   # where the snow gives out
G = 0.0534                  # gravity, rows per frame per frame

A_ON = 22                   # frames of dark before the first shot


def row(x):
    return int(math.floor(feet(x)))


def band(g, c, x, rr, r):
    """One column of snowfield like scene 10's. c is the grid column, x the place on the shoulder."""
    sub = feet(x) - math.floor(feet(x))
    top = r - BACK
    g.set(c, top, "_" if rr.random() < 0.75 else rr.choice("-_."), SNOW_BACK)
    for y in range(top + 1, r + FRONT):
        g.blank(c, y, c, y, TEX)
        if rr.random() < 0.11:
            g.set(c, y, rr.choice("_-¯.'`"), SNOW_BACK if y < r else SNOW_DIM)
    g.set(c, r + FRONT, "¯" if sub < 0.34 else ("-" if sub < 0.67 else "_"), SNOW)


def build_edge():
    """The end of the shoulder: scene 10's snowfield running on to a lip over the drop, and the cliff under it."""
    r = random.Random(111)
    w = -EDGE_X0
    g = Grid(w, WH)
    for c in range(LIP - EDGE_X0, w):
        x = EDGE_X0 + c
        rr = row(x)
        band(g, c, x, r, rr)
        depth = 9 + int(3 * math.sin(x * 0.12) + 2 * math.sin(x * 0.37))
        for y in range(rr + FRONT + 1, min(WH, rr + FRONT + depth)):
            g.blank(c, y, c, y, TEX)
            d = y - rr - FRONT
            p = r.random()
            if d == 1 and p < 0.6:
                g.set(c, y, r.choice(".:'"), SNOW_DIM)
            elif d < 4 and p < 0.3:
                g.set(c, y, r.choice("|'!:"), ROCKC)
            elif p < 0.08:
                g.set(c, y, r.choice(".'`"), TEX)
        g.set(c, min(WH - 1, rr + FRONT + depth), r.choice("'`.,"), FOG_DIM)
    # the lip, and the cliff going back in under the overhang
    lc = LIP - EDGE_X0
    lr = row(LIP)
    g.text(lc - 1, lr - BACK - 1, ",-._", SNOW)
    for y in range(lr - BACK, lr + FRONT + 1):
        g.set(lc - 1, y, "|" if y % 2 else ":", MOONLIT)
    for y in range(lr + FRONT + 1, WH):
        d = y - lr - FRONT
        edge = lc - 1 + min(5, d // 2) - int(1.3 * math.sin(d * 0.8))
        for x in range(edge + 1, edge + 4):
            if 0 <= x < w and g.c[y][x] is None and r.random() < 0.5 - d * 0.02:
                g.set(x, y, r.choice(".:'"), MOONLIT if d < 6 else ROCK_DARK)
        g.set(edge, y, r.choice("|/|(") if d > 1 else "/", MOONLIT if d < 9 else ROCK_DARK)
        for x in range(0, edge):
            g.c[y][x] = None
    for x, n in ((lc + 1, 2), (lc + 3, 1)):
        for k in range(n):
            g.set(x, lr + FRONT + 1 + k, "V" if k == n - 1 else "|", SNOW_DIM)
    return g


# ---------------------------------------------------------------- the fall, shot by shot

def despike(vs):
    """Holds back one-frame steps out and back, so nothing jitters."""
    vs = list(vs)
    for i in range(1, len(vs) - 1):
        if vs[i - 1] == vs[i + 1] != vs[i]:
            vs[i] = vs[i - 1]
    return vs


def cells(path):
    return despike(int(round(x)) for x, _ in path), despike(int(round(y)) for _, y in path)


def streaks(xs, ys):
    """Which streak the O leaves each frame, from how it moved: none, falling, left, right or rising."""
    out = [0]
    for i in range(1, len(xs)):
        dx, dy = xs[i] - xs[i - 1], ys[i] - ys[i - 1]
        if dy >= 1 and abs(dx) <= dy:
            out.append(1)
        elif dx <= -2:
            out.append(2)
        elif dx >= 2:
            out.append(3)
        elif dy <= -1 and abs(dx) <= 1:
            out.append(4)
        else:
            out.append(0)
    return out


def shot_summit(cloud_row):
    """Up off the shoulder, down on the snow, a bounce, a roll over the lip and down into the cloud."""
    x, y, vx, vy = 47.0, 21.0, -1.55, -0.95
    path, hits = [], []
    mode, bounces = "air", 0
    while y < cloud_row + 6:
        for _ in range(4):
            dt = 0.25
            if mode == "air":
                vy += G * dt
                x += vx * dt
                y += vy * dt
                if vy > 0 and x >= LIP and y >= row(x):
                    y = row(x)
                    bounces += 1
                    hits.append(len(path))
                    if bounces == 1:
                        vx, vy = -0.8, -0.5
                    else:
                        mode, vx = "roll", -0.6
            elif mode == "roll":
                x += vx * dt
                y = row(x)
                if x < LIP - 0.5:
                    mode, vy = "fall", 0.0
                    hits.append(len(path))
            else:
                vy += G * dt
                x += vx * 0.8 * dt
                y += vy * dt
        path.append((x, y))
    return path, hits


def shot_mountain():
    """A speck far off going down the trail into the cloud."""
    pts = [(79, 13), (72, 19), (87, 26), (66, 34), (89, 42)]
    path = [pts[0]]
    v, k, u = 0.7, 0, 0.0
    x, y = pts[0]
    while y < 39:
        (x0, y0), (x1, y1) = pts[k], pts[k + 1]
        seg = math.hypot(x1 - x0, 2 * (y1 - y0))
        u += v / seg
        v = min(1.0, v + 0.004)
        if u >= 1:
            u -= 1
            k += 1
            (x0, y0), (x1, y1) = pts[k], pts[k + 1]
        x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        path.append((x, y))
    return path


def shot_climb():
    """Out of the cloud and down the Perilous Climb's switchbacks: rolling down the ramps, hopping down the steps,
    bouncing off the cliff at the turns, into the tunnel at the foot."""
    path, hits, walls = [], [], []
    # out of the cloud onto the ramp
    x, y, vy = 40.0, 50.0, 0.4
    while y < 69.6:
        vy += G * 1.4
        y = min(69.6, y + vy)
        path.append((x, y))
    hits.append(len(path) - 1)
    for k in range(5):
        path.append((x + 0.2 * k, 69.6 - math.sin(math.pi * (k + 1) / 6)))
    pts = [(41, 69.8), (61, 73), (86, 77), (92, 78), (88, 82), (27, 92), (25, 96), (30, 96), (92, 106), (88, 110),
           (18, 120), (10, 120)]
    v, going = 1.0, 1
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = x1 - x0, y1 - y0
        if abs(dx) >= 3 * abs(dy):
            way = 1 if dx > 0 else -1
            if way != going:
                # back off the cliff at the turn
                walls.append(len(path))
                v = 0.7
            going = way
            n, d = abs(dx), 0.0
            while d < n:
                v = min(2.8, v + 0.06 + 0.2 * dy / n)
                d = min(n, d + v)
                path.append((x0 + way * d, y0 + dy * d / n))
        else:
            # hop down the steps
            frames = 6 + int(1.5 * dy)
            for k in range(1, frames + 1):
                u = k / frames
                path.append((x0 + dx * u, y0 + dy * u * u - 1.6 * math.sin(math.pi * u)))
            hits.append(len(path) - 1)
            v = 1.0
            going = 1 if dx > 0 else -1
    return path, hits, walls


def shot_tunnel(floor, hole):
    """Rolling along the haul tunnel, a hop over a stone, and down the hole."""
    path, x = [], 150.0
    hop = None
    while x > hole:
        x -= 1.6
        y = floor
        if hop is None and x < 118:
            hop = len(path)
        if hop is not None and len(path) - hop < 7:
            y = floor - math.sin(math.pi * (len(path) - hop) / 7)
        path.append((x, y))
    drop = len(path)
    y, vy = float(floor), 0.0
    for _ in range(14):
        vy += 0.09
        y += vy
        x -= 0.25
        path.append((x, y))
    return path, hop, drop


def shot_fountain(land_x, floor):
    """Down past the crystal into the pool, then under."""
    path = []
    t = 0
    while True:
        y = -2 + 0.015 * t * t if t < 43 else 25.735 + 1.29 * (t - 43)
        if y >= floor:
            break
        path.append((land_x, min(y, floor - 1)))
        t += 1
    land = len(path)
    for k in range(14):
        path.append((land_x, floor - 1))
    sink = len(path)
    return path, land, sink


def shot_ring(track_row, end_x):
    """Down onto the Ring, two bounces, then a roll to the broken end of the track, a little way back, and still."""
    path, hits = [], []
    x, y, vx, vy = 100.0, 110.0, 0.08, 0.0
    bounce = [(0.35, -0.55), (0.3, -0.3)]
    while True:
        for _ in range(4):
            vy += 0.06 * 0.25
            x += vx * 0.25
            y += vy * 0.25
            if vy > 0 and y >= track_row:
                y = track_row
                hits.append(len(path))
                if not bounce:
                    break
                vx, vy = bounce.pop(0)
        path.append((x, y))
        if len(hits) == 3:
            break
    x3, n = x, 60
    for k in range(1, n + 1):
        u = k / n
        path.append((x3 + (end_x - x3) * (1 - (1 - u) ** 2.4), track_row))
    rest = len(path)
    for k in range(12):
        path.append((end_x, track_row))
    for k in range(8):
        path.append((end_x - 1, track_row))
    return path, hits, rest


def main():
    pkg = sys.argv[1]
    os.makedirs(pkg, exist_ok=True)
    head = "// Generated by tools/build_scene11.py. Don't edit by hand; change the script and rebuild.\n"
    ex = Exporter(head)
    ex.piece("edge", [build_edge()])
    ex.value("edgeX", EDGE_X0)
    ex.value("lip", LIP)
    ex.piece("head", frames_of([["O"]], CHAR))
    ex.piece("speck", frames_of([["o"]], CHAR))
    # streaks round the O (at the middle of 5x5): none, falling, left, right, rising
    blank = ["     "] * 5
    ex.piece("streak", frames_of([blank, ["     ", "  '  ", "     ", "     ", "     "],
                                  ["     ", "     ", "   --", "     ", "     "],
                                  ["     ", "     ", "--   ", "     ", "     "],
                                  ["     ", "     ", "     ", "  '  ", "     "]], STREAK))

    cloud_row = row(LIP) + 7 + FRONT
    a, a_hits = shot_summit(cloud_row)
    b = shot_mountain()
    c, c_hits, c_walls = shot_climb()
    d, d_hop, d_drop = shot_tunnel(26, 24)
    e, e_land, e_sink = shot_fountain(34, 89)
    fr, f_hits, f_rest = shot_ring(139, 117)

    s_b = A_ON + len(a) + 2
    s_c = s_b + len(b) + 14
    s_d = s_c + len(c) + 4
    s_e = s_d + len(d) + 2
    s_f = s_e + len(e) + 30
    f_on = s_f + 16
    t_fade = f_on + len(fr) + 110
    ex.value("cloudRow", cloud_row)
    ex.value("aOn", A_ON)
    ex.value("sB", s_b)
    ex.value("sC", s_c)
    ex.value("sD", s_d)
    ex.value("sE", s_e)
    ex.value("sF", s_f)
    ex.value("fOn", f_on)
    ex.value("tFade", t_fade)
    for name, path in (("a", a), ("b", b), ("c", c), ("d", d), ("e", e), ("f", fr)):
        xs, ys = cells(path)
        ex.value(name + "X", xs)
        ex.value(name + "Y", ys)
        if name != "b":
            ex.value(name + "K", streaks(xs, ys))
        if name in ("a", "c"):
            # lowest so far, so the cameras following it down never go back up
            ex.value(name + "Ymax", [max(ys[:k + 1]) for k in range(len(ys))])
    ex.value("aHits", a_hits)
    ex.value("cHits", c_hits)
    ex.value("cWalls", c_walls)
    ex.value("dHop", d_hop)
    ex.value("dDrop", d_drop)
    ex.value("eLand", e_land)
    ex.value("eSink", e_sink)
    ex.value("fHits", f_hits)
    ex.value("fRest", f_rest)
    n = ex.write(os.path.join(pkg, "Art11Fall.txt"))
    print(f"Art11Fall {n} bytes; shots at {A_ON}, {s_b}, {s_c}, {s_d}, {s_e}, {s_f} (ring {f_on}), fade {t_fade}; "
          f"lengths {len(a)} {len(b)} {len(c)} {len(d)} {len(e)} {len(fr)}")


if __name__ == "__main__":
    main()
