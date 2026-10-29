# finds jitter: runs a scene through ssim and counts every anim or text that moves a cell and straight back
#   python jitter.py <entry script> <frames> [skip]   (e.g. entries/Scene7.txt 1250)
# skip: frame ranges where the screen is meant to shake, left out of the count (e.g. 219-226,278-284)
import collections
import math
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import preview_frames as P

entry, frames = sys.argv[1], int(sys.argv[2])
skip = set()
if len(sys.argv) > 3:
    for part in sys.argv[3].split(","):
        a, b = part.split("-")
        skip.update(range(int(a), int(b) + 1))
P.SW, P.SH = 80, 30
sim = P.new_sim(entry)
track = collections.defaultdict(dict)
label = {}


def walk(c, px, py, pw, ph, f, hidden=False):
    hidden = hidden or not P.vis(c)
    p = c.props
    x, y, w, h = p.get("x", 0), p.get("y", 0), p.get("w", 10), p.get("h", 5)
    dock = str(p.get("dock", ""))
    if dock.startswith("center"):
        ax, ay = px + pw // 2 + x - w // 2, py + ph // 2 + y
    elif dock == "top_center":
        ax, ay = px + pw // 2 + x - w // 2, py + y
    else:
        ax, ay = px + x, py + y
    if not hidden and c.TYPE in ("Anim", "Text") and -40 < ax < P.SW + 40 and -40 < ay < P.SH + 40:
        k = id(c)
        track[k][f] = (int(math.floor(ax)), int(math.floor(ay)), p.get("frame", 0))
        if k not in label:
            s = getattr(c, "sheet", None) or str(p.get("text", ""))
            label[k] = "".join(ch for ch in s if ch not in "#\n %")[:18]
    for kid in P.kids(c):
        walk(kid, ax, ay, w, h, f, hidden)


for f in range(frames):
    sim.step()
    root = sim.ui.root if hasattr(sim.ui, "root") else None
    for kid in P.kids(root):
        walk(kid, 0, 0, P.SW, P.SH, f)

report = []
for k, pos in track.items():
    fs = sorted(pos)
    blips = []
    for i in range(1, len(fs) - 1):
        a, b, c = fs[i - 1], fs[i], fs[i + 1]
        if b != a + 1 or c != b + 1 or b in skip:
            continue
        for axis in (0, 1):
            pa, pb, pc = pos[a][axis], pos[b][axis], pos[c][axis]
            if pa == pc and pb != pa and abs(pb - pa) <= 2:
                blips.append((b, "xy"[axis]))
    if blips and len(blips) > 0:
        report.append((len(blips), k, blips))
report.sort(reverse=True)
for n, k, blips in report[:12]:
    frames_ = [b for b, _ in blips]
    print(f"{n:4d} blips  {label.get(k, '?'):18s}  axes {collections.Counter(a for _, a in blips)}  at {frames_[:6]}..{frames_[-1]}")
print("elements tracked:", len(track), " with blips:", len(report))
