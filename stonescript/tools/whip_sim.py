"""Simulates a whip as a rope and bakes it into animation frames, so lashes and drags move like a real one.

Coordinates are in cells, y down. A cell is about twice as tall as it is wide, which draw() allows for.
"""
import math

from build_scene1 import Grid


def lying(n, seg, hand, ground, back=-1):
    """Starting points: hanging from the hand and lying along the ground behind it (back=-1, left) or in front (1).
    Every piece is seg long so nothing jumps when the simulation starts."""
    hx, hy = hand
    pts = [(hx, hy)]
    x, y = hx, hy
    for i in range(1, n):
        g = ground(x)
        if y + seg * 0.8 < g:
            x, y = x + back * seg * 0.6, y + seg * 0.8
        else:
            x, y = x + back * seg, g
        pts.append((x, y))
    return pts


def simulate(n, seg, hand, frames, ground=None, start=None, gravity=0.15, damping=0.985, sub=12, iters=24, aspect=2.0,
             vel=None):
    """n points seg cells apart, the handle at hand(t), the floor at ground(x), gravity in rows per frame per frame.
    start and vel are the first positions and velocities (cells per frame), by default lying behind the hand.
    Returns the points for each frame. Inside, a row counts aspect columns so loops come out round."""
    A = aspect
    floor = (lambda x: 1e9) if ground is None else ground
    ground = lambda x: floor(x) * A
    drive = hand
    hand = lambda t: (drive(t)[0], drive(t)[1] * A)
    if start:
        pts = [(x, y * A) for x, y in start]
    else:
        pts = lying(n, seg, hand(0), ground)
    prev = list(pts)
    if vel:
        prev = [(x - vx / sub, y - vy * A / sub) for (x, y), (vx, vy) in zip(pts, vel)]
    gravity = gravity * A / (sub * sub)
    out = []
    for f in range(frames):
        for s in range(sub):
            t = f + s / sub
            hx, hy = hand(t)
            nxt = []
            for i, ((x, y), (px, py)) in enumerate(zip(pts, prev)):
                if i == 0:
                    nxt.append((hx, hy))
                    continue
                vx, vy = (x - px) * damping, (y - py) * damping
                nx, ny = x + vx, y + vy + gravity
                g = ground(nx)
                if ny > g:
                    # on the ground: it stops falling and drags
                    ny = g
                    nx = x + vx * 0.6
                nxt.append((nx, ny))
            prev = pts
            pts = nxt
            for _ in range(iters):
                for i in range(n - 1):
                    (x0, y0), (x1, y1) = pts[i], pts[i + 1]
                    dx, dy = x1 - x0, y1 - y0
                    d = math.hypot(dx, dy) or 1e-6
                    k = (d - seg) / d
                    if i == 0:
                        pts[i + 1] = (x1 - dx * k, y1 - dy * k)
                    else:
                        pts[i] = (x0 + dx * k * 0.5, y0 + dy * k * 0.5)
                        pts[i + 1] = (x1 - dx * k * 0.5, y1 - dy * k * 0.5)
                for i in range(1, n):
                    x, y = pts[i]
                    g = ground(x)
                    if y > g:
                        pts[i] = (x, g)
        # anything nearly on the floor gets drawn lying on it
        out.append([(x, (ground(x) if y > ground(x) - 0.35 * A else y) / A) for x, y in pts])
    return out


def tip_speed(frames):
    """How fast the tip moves each frame: the crack is where it peaks."""
    return [0.0] + [math.hypot(b[-1][0] - a[-1][0], b[-1][1] - a[-1][1]) for a, b in zip(frames, frames[1:])]


def _cells(pts):
    """The cells a thin line through pts passes, in order, as [(cx, cy), fys, first, last] each (the sample
    heights inside the cell and its first and last sample), plus the samples."""
    samples = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        m = max(1, int(math.hypot(x1 - x0, (y1 - y0) * 2) / 0.08))
        samples += [(x0 + (x1 - x0) * j / m, y0 + (y1 - y0) * j / m) for j in range(m)]
    samples.append(pts[-1])
    seq = []
    for k, (x, y) in enumerate(samples):
        c = (int(math.floor(x)), int(math.floor(y)))
        if seq and seq[-1][0] == c:
            seq[-1][1].append(y - c[1])
            seq[-1][3] = k
        else:
            seq.append([c, [y - c[1]], k, k])
    # a diagonal step through a corner cell: drop whichever of the two has fewer samples, to keep it one cell wide
    i = 1
    while i < len(seq) - 1:
        (ax, ay), (bx, by), (cx, cy) = seq[i - 1][0], seq[i][0], seq[i + 1][0]
        if abs(ax - cx) == 1 and abs(ay - cy) == 1:
            j = i if len(seq[i][1]) <= len(seq[i + 1][1]) or i + 1 == len(seq) - 1 else i + 1
            del seq[j]
            i = max(1, i - 1)
        else:
            i += 1
    return seq, samples


def draw(g, pts, ox, oy, col, tip_col=None, barbs=None):
    """Draws the rope onto grid g at (ox, oy) as a thin line: slashes and bars where it's steep, _-¯ by height where
    it's flat. barbs (parity, col) puts an x on every other floor cell, like a barbed whip.
    A whip on the floor sits at the bottom of its row (_______), like the game draws one."""
    seq, samples = _cells([(x + ox, y + oy + 0.8) for x, y in pts])
    # each cell's glyph from the way the line runs through it
    chars = []
    for i, (c, fys, k0, k1) in enumerate(seq):
        (ax, ay), (bx, by) = samples[max(0, k0 - 6)], samples[min(len(samples) - 1, k1 + 6)]
        a = (math.degrees(math.atan2(-(by - ay) * 2.0, bx - ax)) + 180) % 180
        if 68 <= a <= 112:
            ch = "|"
        elif 52 < a < 68:
            ch = "/"
        elif 112 < a < 128:
            ch = "\\"
        else:
            fy = sum(fys) / len(fys)
            ch = "¯" if fy < 0.34 else ("-" if fy < 0.67 else "_")
        chars.append(ch)
    # where a flat stretch steps to the next row, the lower cell becomes a slash (_-/ then _-¯ on)
    for i in range(len(seq) - 1):
        (x0, y0), (x1, y1) = seq[i][0], seq[i + 1][0]
        if y0 != y1:
            j = i if y0 > y1 else i + 1
            if chars[j] in "_-¯":
                chars[j] = "|" if x0 == x1 else ("/" if (x1 - x0) * (y1 - y0) < 0 else "\\")
    seen = set()
    cells = []
    for (c, _, _, _), ch in zip(seq, chars):
        if c not in seen:
            seen.add(c)
            cells.append((c[0], c[1], ch))
    low = max((cy for _, cy, _ in cells), default=0)
    for cx, cy, ch in cells:
        cc = col
        if barbs and ch == "_" and cy == low and (cx % 2) == barbs[0]:
            ch, cc = "x", barbs[1]
        g.set(cx, cy, ch, cc)
    if cells:
        cx, cy, _ = cells[-1]
        g.set(cx, cy, "'", tip_col or col)
    return cells
