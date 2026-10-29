"""Builds the light of the ∆ over the places in scene 16 (the world looks up).

    python -I build_light16.py <package dir>

Writes Art16Light.txt from the art the other builders write, so run it after them. For each place: the line work
that can see the ∆ (in rainbow rings out from it), the rest for the scene to dim, and a shadow.
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_scene1 import SAFE

# the ∆ is where the scene draws it on an 80 x 30 screen, a little off on other sizes but it doesn't show
SW, SH = 80, 30
LB = max(2, SH // 12)
RINGS = [22, 36, 52]                 # how far out each ring of the lit reaches (cells, rows counted double)
REACH = 6                            # how far along the line to the ∆ another mark puts a mark in its shadow
BRIGHT = 0x50                        # line work: marks at least this bright (the mean of red, green and blue)


def parse(path):
    """The pieces of an art file: name -> list of layers, each [color, frames], each frame a list of rows."""
    text = open(path, encoding="utf-8").read()
    blocks = dict(re.findall(r"var (\w+) = ascii\n(.*?)\nasciiend", text, re.S))
    pieces = {}
    for name, body in re.findall(r"var (\w+) = (\[\[.*?\]\])\n", text):
        layers = []
        for col, var in re.findall(r'\["(#[0-9a-zA-Z]+)", (\w+)\]', body):
            layers.append([col, pages(blocks[var])])
        pieces[name] = layers
    return pieces, text


def pages(block):
    """An ascii block's frames as lists of rows, put back where they're drawn: a cut-down page starts with
    {x:.., y:..} (on its first line or its %% line) and gets moved back out by that much."""
    chunks, cur = [], []
    for ln in block.split("\n"):
        if ln.lstrip().startswith("%%"):
            chunks.append(cur)
            cur = [ln.lstrip()[2:].strip()]
        else:
            cur.append(ln)
    chunks.append(cur)
    out = []
    for k, ch in enumerate(chunks):
        head = ch[0] if ch else ""
        meta = "{" in head and "}" in head and head.index("{") < head.index("}")
        rows = ch[1:] if (k > 0 or meta) else ch
        mx = my = 0
        if meta:
            m = re.search(r"(?<![\w])x\s*:\s*(-?\d+)", head)
            mx = int(m.group(1)) if m else 0
            m = re.search(r"(?<![\w])y\s*:\s*(-?\d+)", head)
            my = int(m.group(1)) if m else 0
        out.append([""] * my + ["#" * mx + r for r in rows])
    return out


def value(text, name):
    m = re.search(r"^var %s = (.+)$" % name, text, re.M)
    return eval(m.group(1))


class Pic:
    """One frame of a piece, all its layers together: what's drawn on top in each cell, in what color."""

    def __init__(self, layers, frame, w=None, h=None):
        rows = [layer[1][frame] for layer in layers]
        self.h = h or max(len(r) for r in rows)
        self.w = w or max((len(line) for r in rows for line in r), default=1)
        self.ch = [[None] * self.w for _ in range(self.h)]
        self.col = [[None] * self.w for _ in range(self.h)]
        for layer, r in zip(layers, rows):
            for y, line in enumerate(r):
                for x, c in enumerate(line):
                    if c != "#" and x < self.w and y < self.h:
                        self.ch[y][x] = c
                        self.col[y][x] = layer[0]

    def solid(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h and self.ch[y][x] is not None

    def mark(self, x, y):
        return self.solid(x, y) and self.ch[y][x] != " "

    def bright(self, x, y):
        c = self.col[y][x]
        return c.startswith("#rain") or sum(int(c[i:i + 2], 16) for i in (1, 3, 5)) // 3 >= BRIGHT


def joined(a, b):
    """A picture cut in two halves (...A and ...B) put back together."""
    p = Pic(a, 0)
    q = Pic(b, 0)
    out = Pic([["#000000", [[]]]], 0, p.w + q.w, max(p.h, q.h))
    for y in range(out.h):
        for x in range(out.w):
            src, sx = (p, x) if x < p.w else (q, x - p.w)
            if src.solid(sx, y):
                out.ch[y][x] = src.ch[y][sx]
                out.col[y][x] = src.col[y][sx]
    return out


def sees(p, x, y, lx, ly):
    """Whether the line from this mark toward the light crosses no other mark of its picture for REACH cells."""
    dx, dy = lx - x, ly - y
    n = max(abs(dx), abs(dy))
    if n < 1:
        return True
    for i in range(1, REACH + 1):
        px, py = int(round(x + dx * i / n)), int(round(y + dy * i / n))
        if not (0 <= px < p.w and 0 <= py < p.h):
            return True
        if p.mark(px, py):
            return False
    return True


def ring_of(x, y, lx, ly):
    d = math.hypot(x - lx, 2 * (y - ly))
    for k, r in enumerate(RINGS):
        if d < r:
            return k
    return len(RINGS)


def lit(pics, light, behind=None, also=()):
    """For each frame: the lit by ring ({(x, y): ch} per ring), the dark ({(x, y): (ch, color)}) and the shadow
    ({(x, y): ch}). also: other spots the ∆ is seen from as the camera moves, a mark that sees it from any is lit."""
    lx, ly = light
    lits, darks, shadows = [], [], []
    for p in pics:
        rings = [dict() for _ in range(len(RINGS) + 1)]
        dark = {}
        shadow = {}
        tops = {}
        for x in range(p.w):
            tops[x] = next((y for y in range(p.h) if p.solid(x, y)), p.h)
        for y in range(p.h):
            for x in range(p.w):
                if not p.mark(x, y):
                    continue
                if p.bright(x, y) and any(sees(p, x, y, ax, ay) for ax, ay in ((lx, ly),) + tuple(also)):
                    rings[ring_of(x, y, lx, ly)][(x, y)] = p.ch[y][x]
                else:
                    dark[(x, y)] = (p.ch[y][x], p.col[y][x])
                if not p.bright(x, y):
                    continue
                side = 1 if x > lx + 3 else (-1 if x < lx - 3 else 0)
                sx, sy = x + side, y + 1
                if (0 <= sx < p.w and sy < p.h and not p.mark(sx, sy) and (p.solid(sx, sy) or sy > tops[sx])
                        and not (behind and behind(sx, sy)) and (sx, sy) not in shadow):
                    shadow[(sx, sy)] = p.ch[y][x]
        lits.append(rings)
        darks.append(dark)
        shadows.append(shadow)
    return lits, darks, shadows


def top(pic):
    """A figure in the light from above: its tops (the marks with nothing of it over them), and the rest."""
    lit, dark = {}, {}
    for y in range(pic.h):
        for x in range(pic.w):
            if pic.mark(x, y):
                if pic.mark(x, y - 1):
                    dark[(x, y)] = (pic.ch[y][x], pic.col[y][x])
                else:
                    lit[(x, y)] = pic.ch[y][x]
    return lit, dark


class Out:
    def __init__(self, header):
        self.parts = [header]

    def piece(self, name, frames, col, w=None):
        """frames: a list of {(x, y): ch} from the piece's top left. w: pad the first row to that width with
        see-through cells, so the game's rainbow spreads over all of it."""
        h = max([y for f in frames for (_, y) in f] + [0]) + 1
        ww = w or max([x for f in frames for (x, _) in f] + [0]) + 1
        out = []
        for f in frames:
            # no cutting down with a page offset, a script's anim shows the offset as text in the game
            x0 = y0 = 0
            lines = []
            for y in range(y0, h):
                s = "".join(f.get((x, y), "#") for x in range(x0, ww))
                if not (w and y == 0):
                    s = s.rstrip("#")
                for ch in s:
                    if ch not in "# " and ch not in SAFE:
                        raise SystemExit(f"{name}: glyph {ch!r} is not in the game font list")
                lines.append(s.replace("\\n", "\\·") or "#")
            while len(lines) > 1 and lines[-1] == "#":
                lines.pop()
            out.append(("{x:%d, y:%d}" % (x0, y0) if x0 or y0 else "", "\n".join(lines)))
        text = (out[0][0] + "\n" if out[0][0] else "") + out[0][1]
        for meta, body in out[1:]:
            text += "\n%%" + (" " + meta if meta else "") + "\n" + body
        # the art var gets "Art" on the end, name + "0" could clash with the next piece's name
        self.parts.append(f"var {name}Art = ascii\n" + text + "\nasciiend\n")
        self.parts.append(f'var {name} = [["{col}", {name}Art]]\n')

    def darks(self, name, darks):
        """The dark of a piece, one piece per color (each frame for frame), and the list of them."""
        cols = []
        for d in darks:
            for _, c in d.values():
                if c not in cols:
                    cols.append(c)
        for k, c in enumerate(cols):
            self.piece(f"{name}Dark{k}", [{p: ch for p, (ch, cc) in d.items() if cc == c} for d in darks], c)
        self.value(f"{name}Dark", "[" + ", ".join(f"{name}Dark{k}" for k in range(len(cols))) + "]")
        return sum(len(d) for d in darks)

    def value(self, name, v):
        self.parts.append(f"var {name} = {v}\n")

    def write(self, path):
        text = "\n".join(self.parts)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        return len(text.encode("utf-8"))


def place(out, name, lits, darks, shadows, w):
    """A place's lit rings (each cut down to its rows, plus the row each starts at), its dark as it is, and its
    shadow cut down to its rows."""
    ys = []
    for k in range(len(RINGS) + 1):
        cells = [c for r in lits for c in r[k]]
        y0 = min((y for (_, y) in cells), default=0)
        out.piece(f"{name}Lit{k}", [{(x, y - y0): ch for (x, y), ch in r[k].items()} for r in lits], "#rainFF", w)
        ys.append(y0)
    out.value(f"{name}LitY", ys)
    out.value(f"{name}Lit", "[" + ", ".join(f"{name}Lit{k}" for k in range(len(RINGS) + 1)) + "]")
    n = out.darks(name, darks)
    cells = [c for s in shadows for c in s]
    y0 = min((y for (_, y) in cells), default=0)
    out.piece(f"{name}Shadow", [{(x, y - y0): ch for (x, y), ch in s.items()} for s in shadows], "#000000")
    out.value(f"{name}ShadowY", y0)
    return sum(len(r[k]) for r in lits for k in range(len(RINGS) + 1)), n, sum(len(s) for s in shadows)


def figure(out, name, layers):
    pics = [Pic(layers, i) for i in range(len(layers[0][1]))]
    parts = [top(p) for p in pics]
    out.piece(f"{name}Lit", [l for l, _ in parts], "#rainFF", max(p.w for p in pics))
    out.darks(name, [d for _, d in parts])


def main():
    pkg = sys.argv[1]
    mouth, mt = parse(os.path.join(pkg, "Art16Mouth.txt"))
    places, _ = parse(os.path.join(pkg, "Art16Places.txt"))
    s1, _ = parse(os.path.join(pkg, "Art1Sprites.txt"))
    s8, _ = parse(os.path.join(pkg, "Art8Sprites.txt"))
    _, dt = parse(os.path.join(pkg, "ArtDelta3D.txt"))
    out = Out("// Generated by tools/build_light16.py. Don't edit by hand; change the script and rebuild.\n")
    report = []

    # the mine's mouth: the ∆ over the cliff at (16, 1) on screen. the camera tilts up TILT rows while the ∆ stays
    # put in the sky, so the cliff is lit from every step of the way up
    cam_x = value(mt, "mouthX") - (SW - 4)
    cam_y = value(mt, "feet") + 8 - SH
    tilt = int(re.search(r"^var TILT = (\d+)", open(os.path.join(pkg, "Scene16.txt"), encoding="utf-8").read(),
                         re.M).group(1))
    light = (16 + value(dt, "w1") / 2 + cam_x, 1 + value(dt, "h1") / 2 + cam_y)
    up = [(light[0], light[1] - d) for d in range(4, tilt + 1, 4)]
    back = joined(mouth["mouthA"], mouth["mouthB"])
    near = joined(mouth["nearA"], mouth["nearB"])
    w = max(back.w, near.w)
    report.append(("mouth", place(out, "mouth", *lit([back], light, also=up), w)))
    report.append(("near", place(out, "near", *lit([near], light, back.mark, up), w)))

    # the Icy Ridge: the ∆ at (47, 1); its snow from x -10, the dunes from row lb + 9 and the field in front from lb + 14
    lx, ly = 47 + value(dt, "w2") / 2, 1 + value(dt, "h2") / 2
    dunes = [Pic(places["ridgeDunes"], i) for i in range(len(places["ridgeDunes"][0][1]))]
    field = Pic(places["ridgeField"], 0)
    w = max(max(p.w for p in dunes), field.w)
    report.append(("dunes", place(out, "dunes", *lit(dunes, (lx + 10, ly - (LB + 9))), w)))
    under = lambda x, y: any(p.mark(x, y + 5) for p in dunes)
    report.append(("field", place(out, "field", *lit([field], (lx + 10, ly - (LB + 14)), under), w)))

    # the Cross Deadwood River: the ∆ at (55, 1), the canyon from (-25, 1). its moon is left out, it has its own light
    lx, ly = 55 + value(dt, "w3") / 2, 1 + value(dt, "h3") / 2
    river = Pic(places["river"], 0)
    for y in range(min(9, river.h)):
        for x in range(55, min(82, river.w)):
            river.ch[y][x] = None
    report.append(("river", place(out, "river", *lit([river], (lx + 25, ly - 1)), river.w)))

    # the figures, lit along their tops
    figure(out, "body", mouth["body"])
    figure(out, "cart", s1["cart"])
    figure(out, "gobbler", s8["gobbler"])
    figure(out, "eater", s8["eater"])
    figure(out, "tentacle", places["tentacle"])
    figure(out, "frog", places["frog"])

    size = out.write(os.path.join(pkg, "Art16Light.txt"))
    print(f"Art16Light {size} bytes; lit / dark / shadow cells: "
          + ", ".join(f"{n} {a}/{b}/{c}" for n, (a, b, c) in report))


if __name__ == "__main__":
    main()
