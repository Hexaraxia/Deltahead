"""Whip animations for the scenes, simulated with whip_sim and baked into sprite frames.

lash() is the crack from the top of the swing, drag() a looped whip trailing behind a walking hand.
"""
import math

import whip_sim as W
from build_scene1 import Grid


# the whip at the top of the lash, as in the Controller's frame 23 (facing right), in cells from the hand
LOOP_PATH = [(0, 0), (1, -1.2), (1.6, -1.8), (3, -1.7), (5, -1.7), (6.2, -1.9), (6.8, -2.5), (6.3, -3.1), (5, -3.3),
             (2, -3.3), (-6, -3.1)]
LOOP_SPAN = (5, 8)   # pieces of the path that make the loop


def resample(path, n, step=1.0, aspect=2.0):
    """n points step apart along a polyline in cells (a row is aspect columns tall), going straight on past its
    end. Also returns which piece of the path each point is on."""
    vis = [(x, y * aspect) for x, y in path]
    out, segs = [vis[0]], [0]
    si, pos = 0, vis[0]
    while len(out) < n:
        need = step
        while need > 1e-9:
            if si + 1 >= len(vis):
                (ax, ay), (bx, by) = vis[-2], vis[-1]
                d = math.hypot(bx - ax, by - ay)
                pos = (pos[0] + (bx - ax) / d * need, pos[1] + (by - ay) / d * need)
                need = 0
                continue
            a, b = pos, vis[si + 1]
            d = math.hypot(b[0] - a[0], b[1] - a[1])
            if d >= need:
                pos = (a[0] + (b[0] - a[0]) * need / d, a[1] + (b[1] - a[1]) * need / d)
                need = 0
            else:
                need -= d
                pos = b
                si += 1
        out.append(pos)
        segs.append(si)
    return [(x, y / aspect) for x, y in out], segs


def lash(n=18, frames=16, ground=lambda x: 0.0, hand_y=-1.0, dir=1, col="#e0e0e0", tip_col=None, pad=2, reel=10, keep=2,
         v=1.8, gravity=0.05, path=LOOP_PATH, span=LOOP_SPAN, scale=1.0):
    """Frames of a lash from a hand at (0, hand_y) above the floor, thrown toward dir (1 right, -1 left), over a
    floor ground(x) (x from the hand's column, y down). Starts from path (the game's top of swing), lays out along
    the floor, cracks, then reels back in to keep pieces. Returns (grids, ox, oy, crack): the hand's cell in every
    grid and the frame the tip snaps. simulated on a flat floor, then laid onto ground(x) so it keeps its shape."""
    slope = ground
    pts, segs = resample([(x * scale, y * scale + hand_y) for x, y in path], n)
    pts = [(dir * x, y) for x, y in pts]
    vel = []
    for s in segs:
        u = min(1.0, max(0.0, (s - span[0] + 0.5) / (span[1] - span[0])))
        vel.append((dir * v * u, 0.0))
    hand = lambda t: (0.0, hand_y)
    sim = W.simulate(n, 1.0, hand, frames, ground=lambda x: 0.0, damping=0.995, gravity=gravity, start=pts, vel=vel)
    sim = [[(x, y + slope(x)) for x, y in pts] for pts in sim]
    # reeled back in along its own path
    last = sim[-1]
    for p in range(1, reel + 1):
        k = int(round(len(last) * p / (reel + 1)))
        sim.append(last[:max(keep, len(last) - k)])
    # the crack is when the tip first gets to its furthest out
    reach = [dir * pts[-1][0] for pts in sim[:frames]]
    far = max(reach)
    crack = next(k for k, r in enumerate(reach) if r >= far - 0.6)
    xs = [x for pts in sim for x, _ in pts]
    ys = [y for pts in sim for _, y in pts]
    x0, x1 = math.floor(min(xs)) - pad, math.ceil(max(xs)) + pad
    y0, y1 = math.floor(min(ys)) - pad, math.ceil(max(ys)) + 1
    grids = []
    for pts in sim:
        g = Grid(x1 - x0 + 1, y1 - y0 + 1)
        W.draw(g, pts, -x0, -y0, col, tip_col)
        grids.append(g)
    return grids, -x0, int(round(hand_y)) - y0, crack


def drag(n=16, speed=0.42, bob=0.15, sway=0.35, steps=6, loop=24, hand_y=-2.0, col="#7fe3de", barbs=None, dir=1):
    """A looped whip dragged behind a hand walking toward dir, bobbing every `steps` frames. Returns
    (grids, ox, oy, reach): the hand's cell in every grid and how far behind the hand the end lies."""
    def hand(t):
        ph = math.pi * t / steps
        return (dir * (speed * t + sway * math.sin(ph)), hand_y + bob * abs(math.sin(ph)))
    ground = lambda x: 0.0
    warm = 120
    sim = W.simulate(n, 1.0, hand, warm + loop, ground=ground, damping=0.97, gravity=0.16)[warm:]
    rel = []
    for k, pts in enumerate(sim):
        hx = dir * speed * (warm + k)
        rel.append([(x - hx, y) for x, y in pts])
    xs = [x for pts in rel for x, _ in pts]
    ys = [y for pts in rel for _, y in pts]
    x0, x1 = math.floor(min(xs)) - 1, math.ceil(max(xs)) + 1
    y0, y1 = math.floor(min(ys)) - 1, math.ceil(max(ys)) + 1
    grids = []
    for k, pts in enumerate(rel):
        g = Grid(x1 - x0 + 1, y1 - y0 + 1)
        W.draw(g, pts, -x0, -y0, col, None, barbs)
        grids.append(g)
    reach = max(abs(pts[-1][0]) for pts in rel)
    return grids, -x0, int(round(hand_y)) - y0, int(round(reach))


def floor_wave(length=70, enter=7, settle=3, travel=16, after=14, height=2.6, width=7.0, col="#e0e0e0"):
    """A whip cracked along the floor from a hand off to the left (x=0) to its tip at x=length: flung out, a loop
    rolls to the tip and snaps, then it's pulled back out left. Returns (grids, crack): the grids span x 0..length+3
    with the floor on their last row."""
    frames = []
    h = int(math.ceil(height)) + 3
    rest = enter + settle
    for k in range(rest + travel + 4 + after):
        pts = []
        if k < enter:
            # flung out, the end still up off the floor
            u = 1 - (1 - (k + 1) / enter) ** 2
            tip = length * u
            lift = 1.6 * (1 - u) + 0.4
            for i in range(int(tip * 4) + 1):
                x = i / 4.0
                j = tip - x
                y = -lift * (1 - j / 10.0) if j < 10 else 0.0
                pts.append((x, y))
        else:
            kk = k - rest
            pull = max(0, kk - travel - 4) * length / after
            tip = length - pull
            c = width / 2 + (length - width) * min(1.0, max(0, kk) / travel)
            for i in range(int(tip * 4) + 1):
                x = i / 4.0
                y = 0.0
                if 0 <= kk < travel + 2 and abs(x - c) < width / 2:
                    # the loop rolling forward, steep at the front
                    u = (x - c + width / 2) / width
                    y = -height * math.sin(math.pi * u ** 1.6)
                pts.append((x, y))
            # the tip flips up as the loop gets there, then lies back down
            flick = kk - travel
            if 0 <= flick < 4 and pts:
                lift = [1.2, 2.4, 1.6, 0.5][flick]
                for j in range(1, 13):
                    if j <= len(pts):
                        x, y = pts[-j]
                        pts[-j] = (x + (0.6 if flick == 1 else 0) * (13 - j) / 12, y - lift * (13 - j) / 12)
        g = Grid(length + 4, h)
        if len(pts) > 1:
            W.draw(g, pts, 0, h - 1, col)
        frames.append(g)
    return frames, rest + travel + 1
