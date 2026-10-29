"""Builds the art for scene 1 (the Ring).

    python -I build_scene1.py <package dir>

Writes Art1Mine, Art1Descent, Art1Ring, Art1Track and Art1Sprites.txt: one ascii block per color, stacked with
Anim.AddLayer, '#' where a layer has nothing. Line art only, using just glyphs from the game's own art (SAFE).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import controller_frames as CTRLF

SAFE = set("─│┊┌┐└┘├┤┬┴┼═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╡╤╥╦╧╨╩╪╫╬▲▼∆¯´`·∙°†•…‾←↑→↓≈≡⌐∞φ☼♦♥*~^_-=+.,:;'\"!?()<>[]{}/\\|")
SAFE |= set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
SAFE |= set("Ω")                # the Omega chest's mark
SAFE |= set("ζ")                # the Moonbloom's stem
SAFE |= set("ε❄")               # the Bone chest's and the ice chest's marks
BLOCKS = set("█▓▒░▀▄▌▐▁▂▃▅▆▇")

# the game's grays: far, back, main, near, characters
FAR = "#2e2e2e"
BACK = "#474747"
MIDG = "#5e5e5e"
GROUND = "#7c7c7c"
NEAR = "#a6a6a6"
CHAR = "#f0f0f0"
TEX = "#3e3e3e"
RAILC = "#8a8a8a"
TIEC = "#565656"
SIGNC = "#b4b4b4"
WOODC = "#6e6e6e"
LIQA = "#6a6a6a"
LIQB = "#4c4c4c"
CART = "#9a9a9a"
CARGO = "#6e6e6e"
DIMC = "#8a8a8a"
LAMP = "#e0b060"
VENT = "#c0502a"
FIRE1 = "#ffd27a"
FIRE2 = "#ff8a2a"
FIRE3 = "#e0461c"


class Grid:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.c = [[None] * w for _ in range(h)]

    def set(self, x, y, ch, col):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.c[y][x] = (ch, col)

    def get(self, x, y):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h and self.c[y][x]:
            return self.c[y][x][0]
        return " "

    def text(self, x, y, s, col):
        for i, ch in enumerate(s):
            if ch != " ":
                self.set(x + i, y, ch, col)

    def rows(self, x, y, rows, col, cmap=None):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch != " ":
                    self.set(x + i, y + j, ch, (cmap or {}).get(ch, col))

    def blank(self, x0, y0, x1, y1, col):
        """Opaque empty cells: the game draws a space, hiding whatever is behind."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, " ", col)

    def solid(self, x, y, rows, col):
        """Like rows, for something solid: each row is filled from its first mark to its last with opaque
        blanks, so anything behind it (a character walking past) is hidden."""
        for j, row in enumerate(rows):
            a, b = len(row) - len(row.lstrip()), len(row.rstrip()) - 1
            if b >= a:
                self.blank(x + a, y + j, x + b, y + j, col)
        self.rows(x, y, rows, col)


def frames_of(rows_list, col, cmap=None, cfn=None, solid=False):
    """Turns a list of frames (each a list of row strings) into same-size grids.
    Color: cfn(x, y, ch) if given, else cmap[ch], else col. solid: each row is filled from its first mark to its
    last with opaque blanks, so whatever is behind doesn't show through."""
    w = max(len(r) for f in rows_list for r in f)
    h = max(len(f) for f in rows_list)
    out = []
    for f in rows_list:
        g = Grid(w, h)
        for y, row in enumerate(f):
            if solid and row.strip():
                g.blank(len(row) - len(row.lstrip()), y, len(row.rstrip()) - 1, y, col)
            for x, ch in enumerate(row):
                if ch != " ":
                    g.set(x, y, ch, cfn(x, y, ch) if cfn else (cmap or {}).get(ch, col))
        out.append(g)
    return out


MIRROR = {"/": "\\", "\\": "/", "(": ")", ")": "(", "<": ">", ">": "<", "└": "┘", "┘": "└", "┌": "┐", "┐": "┌",
          "╞": "╡", "╡": "╞", "[": "]", "]": "[", "´": "`", "`": "´", "{": "}", "}": "{"}


def mirror(grids):
    out = []
    for g in grids:
        m = Grid(g.w, g.h)
        for y in range(g.h):
            for x in range(g.w):
                cell = g.c[y][x]
                if cell:
                    m.set(g.w - 1 - x, y, MIRROR.get(cell[0], cell[0]), cell[1])
        out.append(m)
    return out


class Exporter:
    def __init__(self, header):
        self.parts = [header]

    def piece(self, name, grids, crop=False, split=False):
        """crop: cut each color's frames down to the cells used, with a {x:.., y:..} page offset. keep it off, an
        anim a script makes shows the offset as text and breaks its lines.
        split: cut each color down to its cells (same cut every frame) as [color, art, x, y], for a scene to draw
        as a panel of one anim per color, since the game walks every cell of an anim's page whenever any of it
        shows."""
        colors = []
        for g in grids:
            for row in g.c:
                for cell in row:
                    if cell and cell[1] not in colors:
                        colors.append(cell[1])
        pairs = []
        for k, col in enumerate(colors):
            cut = crop and not col.startswith("#rain")
            sx = sy = 0
            if split:
                spots = [(x, y) for g in grids for y, row in enumerate(g.c) for x, cell in enumerate(row)
                         if cell and cell[1] == col]
                sx, sy = min(x for x, _ in spots), min(y for _, y in spots)
            pages = []
            for g in grids:
                rows = []
                for row in g.c:
                    s = "".join(cell[0] if cell and cell[1] == col else "#" for cell in row)
                    for ch in s:
                        if ch in BLOCKS:
                            raise SystemExit(f"{name}: block glyph {ch!r} is not allowed")
                        if ch not in "# " and ch not in SAFE:
                            raise SystemExit(f"{name}: glyph {ch!r} (U+{ord(ch):04X}) is not in the game font list")
                    rows.append(s)
                if split:
                    rows = [r[sx:] for r in rows[sy:]]
                meta = ""
                used = [y for y, r in enumerate(rows) if r.strip("#")]
                if cut and used:
                    x0 = min(len(r) - len(r.lstrip("#")) for r in rows if r.strip("#"))
                    y0 = used[0]
                    rows = [r[x0:] for r in rows[y0:used[-1] + 1]]
                    if x0 or y0:
                        meta = "{x:%d, y:%d}" % (x0, y0)
                # the game stores art line breaks as the two characters \n, so no backslash right before an n
                lines = [r.rstrip("#").replace("\\n", "\\·") or "#" for r in rows]
                while len(lines) > 1 and lines[-1] == "#":
                    lines.pop()
                pages.append((meta, "\n".join(lines)))
            text = (pages[0][0] + "\n" if pages[0][0] else "") + pages[0][1]
            for meta, body in pages[1:]:
                text += "\n%%" + (" " + meta if meta else "") + "\n" + body
            var = f"{name}{k}"
            self.parts.append(f"var {var} = ascii\n" + text + "\nasciiend\n")
            pairs.append(f'["{col}", {var}, {sx}, {sy}]' if split else f'["{col}", {var}]')
        self.parts.append(f"var {name} = [{', '.join(pairs)}]\n")

    def value(self, name, v):
        if isinstance(v, list):
            self.parts.append(f"var {name} = [{', '.join(str(x) for x in v)}]\n")
        else:
            self.parts.append(f"var {name} = {v}\n")

    def write(self, path):
        text = "\n".join(self.parts)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        return len(text.encode("utf-8"))


def smooth(keys, y):
    for i in range(1, len(keys)):
        if y <= keys[i][0]:
            (y0, a), (y1, b) = keys[i - 1], keys[i]
            u = max(0.0, min(1.0, (y - y0) / (y1 - y0)))
            u = u * u * (3 - 2 * u)
            return a + (b - a) * u
    return keys[-1][1]


# ------------------------------------------------------------------ drawing helpers in the game's manner

def edge_line(g, x0, x1, y, r, col):
    """A ground or ledge edge like the Boiling Mine's: _/`--,-,__,'-,_/`-"""
    pieces = ["--", "_,", "-'", ",-", "_/`", "-,_", "__", "-.", "`-", ",_", "--,", "_", "-"]
    s = ""
    while len(s) < x1 - x0 + 1:
        s += r.choice(pieces)
    g.text(x0, y, s[: x1 - x0 + 1], col)


def ribs(g, x0, x1, y0, depth, r, col):
    """Vertical ribs under an edge that fade out downward: ' | '| || |'"""
    for x in range(x0, x1 + 1):
        if r.random() < 0.5:
            n = r.randint(1, depth)
            for k in range(n):
                g.set(x, y0 + k, r.choice("||||'!") if k < n - 1 else r.choice("'|"), col)


def stipple(g, x, y, d, col, r):
    p = [0.42, 0.26, 0.14, 0.06]
    if d - 1 < len(p) and r.random() < p[d - 1]:
        g.set(x, y, r.choice(":.'," if d < 3 else ".'`"), col)


def shaft_walls(g, walls, y0, y1, col, tex, r):
    """Draws two rock faces as single strokes, with stippled shading on the rock side and drips
    under overhangs. walls[y] = (left, right); rock is outside [left, right]."""
    for side in (0, 1):
        prev = None
        for y in range(y0, y1):
            x = walls[y][side]
            if prev is None:
                prev = x
            dx = x - prev
            if abs(dx) > 1:
                a, b = sorted((prev, x))
                for xx in range(a, b + 1):
                    g.set(xx, y - 1 if side == 0 and dx < 0 or side == 1 and dx > 0 else y, "_", col)
                for xx in range(a + 1, b, r.randint(2, 4)):
                    if r.random() < 0.5:
                        g.set(xx, y, r.choice("V'Y'"), col)
            ch = "|" if dx == 0 else ("\\" if dx > 0 else "/") if abs(dx) == 1 else ("\\" if dx > 0 else "/")
            g.set(x, y, ch, col)
            for d in range(1, 5):
                stipple(g, x - d if side == 0 else x + d, y, d, tex, r)
            prev = x


def pillar_mine(g, x, y0, y1, col):
    """A Boiling Mine support: || with a /()\\ cap and struts."""
    for y in range(y0, y1):
        g.text(x, y, "||", col)
    g.text(x - 1, y1, "/()\\", col)
    g.text(x - 2, y1 + 1, "//||\\\\", col)
    g.text(x - 3, y1 + 2, "// || \\\\", col)


# ------------------------------------------------------------------ the descent world: mine level, shaft, chamber
DW, DH = 172, 152
GROUND_ROW = 24           # the mine walkway's edge; rails sit on rows 22-23, feet on row 21
PIT = (92, 106)
SX = 99                   # shaft center
RING = dict(cx=SX, cy=136)
CTRL = (SX - 1, 134)      # the Controller's head on the mound (his body at x 97-99)
LANTERN = (SX + 11, 132)  # the lantern's flame, on the mound's far shoulder, clear of his whip
LAMPS = [(64, 14), (130, 14)]
MINE_X = 92               # where the camera centers for the mine shot (the pit and its sign in view)
BACK_TRACK = 20           # the back line's rails (on the back layer), under the sign so its Pushers show
SPEED = 0.3               # cells per frame: the Pusher's pace round the Ring, and after it
DEP_X = 112               # the last cell of the near straight before the right-hand bend


def chamber_floor():
    """The chamber floor's few dashes, like the game's cave floors, in world cells."""
    r = random.Random(41)
    cells = {}
    for y in range(141, 149):
        for x in range(300):
            if r.random() < 0.06:
                cells[(x, y)] = r.choice("__.'")
    return cells


def build_descent():
    r = random.Random(7)
    main = Grid(DW, DH)

    # rails across the whole level, carried over the pit on a little trestle
    for x in range(DW):
        main.set(x, 22, "." if x % 3 == 0 else "_", RAILC)
        main.set(x, 23, "`" if x % 3 == 1 else "¯", TIEC)
    for x in range(PIT[0], PIT[1] + 1):
        main.set(x, 24, "\\" if x % 2 else "/", WOODC)
    for x in (PIT[0] + 2, PIT[1] - 2):
        for y in range(25, 31):
            main.set(x, y, "|", WOODC)
    # the ground either side of the pit, with ribs under its edge
    edge_line(main, 0, PIT[0] - 1, GROUND_ROW, r, GROUND)
    edge_line(main, PIT[1] + 1, DW - 1, GROUND_ROW, r, GROUND)
    ribs(main, 0, PIT[0] - 2, GROUND_ROW + 1, 3, r, MIDG)
    ribs(main, PIT[1] + 2, DW - 1, GROUND_ROW + 1, 3, r, MIDG)
    # the Pushers' warning sign over the pit, words from the Sight Stone's line on a Flame Geyser
    sign = [" _________________________ ",
            "|o You REALLY don't want o|",
            "|  to go down there.  ↓   |",
            "'--|-----------------|----'"]
    sx = SX - len(sign[0]) // 2
    main.solid(sx, 13, sign, WOODC)
    main.text(sx + 3, 14, "You REALLY don't want", SIGNC)
    main.text(sx + 3, 15, "to go down there.", SIGNC)
    main.set(sx + 22, 15, "↓", SIGNC)
    for px in (sx + 3, sx + 21):
        for y in range(17, 22):
            main.set(px, y, "|", WOODC)
    # lamps on posts
    for lx, ly in LAMPS:
        main.text(lx - 1, ly, " _ ", WOODC)
        main.text(lx - 1, ly + 1, "( )", WOODC)
        main.set(lx, ly + 1, "*", LAMP)
        for y in range(ly + 2, 22):
            main.set(lx, y, "|", WOODC)

    # the shaft below the pit, the geyser ledges, and the Ring's chamber (wide enough that its walls stay out of frame)
    hw_keys = [(24, 7), (40, 8), (56, 13), (68, 14), (82, 9), (96, 6), (104, 6), (113, 68), (152, 68)]
    walls = {}
    for y in range(GROUND_ROW, DH):
        nl = 1.6 * math.sin(y * 0.37) + 1.2 * math.sin(y * 0.13 + 2)
        nr = 1.6 * math.sin(y * 0.29 + 1) + 1.2 * math.sin(y * 0.11)
        hw = smooth(hw_keys, y)
        walls[y] = (int(round(SX - hw - nl)), int(round(SX + hw + nr)))
    walls[GROUND_ROW] = (PIT[0], PIT[1])
    shaft_walls(main, walls, GROUND_ROW, DH - 6, GROUND, TEX, r)
    geysers = []
    for gy, side in ((64, 0), (72, 1)):
        x0 = walls[gy][side]
        step = 1 if side == 0 else -1
        ledge = "¯¯¯¯¯¯"
        for k in range(6):
            main.set(x0 + step * k, gy, "¯", GROUND)
            main.set(x0 + step * k, gy + 1, r.choice("V'Y"), TEX)
        vx = x0 + step * 3
        main.text(vx - 1, gy - 1, "/^\\", VENT)
        geysers.append((vx, gy - 2))
    # what's left of the old workings: a rope off the trestle, a broken ladder, a ledge with junk
    for y in range(25, 58):
        if y % 7 != 3:
            main.set(PIT[0] + 4 + (1 if 40 < y < 50 else 0), y, "┊", MIDG)
    for y in range(40, 50):
        if y not in (45, 46):
            main.set(walls[y][0] + 1, y, "|", MIDG)
            main.set(walls[y][0] + 3, y, "|", MIDG)
            if y % 2 == 0:
                main.set(walls[y][0] + 2, y, "=", MIDG)
    rx = walls[52][1]
    main.text(rx - 7, 52, "_______", GROUND)
    main.text(rx - 6, 51, ",o.__", MIDG)
    main.text(rx - 6, 53, "V ' Y", TEX)
    for (x, y), ch in chamber_floor().items():
        if walls[y][0] < x < walls[y][1]:
            main.set(x, y, ch, MIDG)
    oval_track(main, RING["cx"], RING["cy"])
    # the Controller's mound and the bend the rock breaks are sprites of their own (build_post, take_bend)

    # far: Boiling Mine pillars and a high beam, then dark rock all the way down
    far = Grid(DW, 110)
    for px in range(5, DW, 17):
        pillar_mine(far, px, 0, 16, FAR)
    for x in range(DW):
        far.set(x, 8, "." if x % 3 == 0 else "_", FAR)
        far.set(x, 9, "`" if x % 3 == 1 else "¯", FAR)
    for y in range(22, far.h):
        for x in range(DW):
            if r.random() < 0.025:
                far.set(x, y, r.choice(".`'"), FAR)

    # back: rock mounds with ribs, like the Boiling Mine's background edge
    back = Grid(DW, 130)
    for mx in range(8, DW, 37):
        mw = r.randint(16, 26)
        top = 14 + r.randint(0, 3)
        back.text(mx, top, "/¯`-,.", BACK)
        back.text(mx - 2, top + 1, ",:¯\\_,-,_`-._", BACK)
        back.text(mx - 4, top + 2, "/ | | | ||`:-,¯`-.", BACK)
        for x in range(mx - 4, mx - 4 + mw):
            for y in range(top + 3, top + 6):
                if r.random() < 0.45:
                    back.set(x, y, r.choice("|'|!"), BACK)
    for y in range(26, back.h):
        for x in range(DW):
            if r.random() < 0.018:
                back.set(x, y, r.choice(".'`:"), BACK)
    # a second line of track at the back of the walkway, for the Pushers going the other way
    rails_row(back, 0, DW - 1, BACK_TRACK, "#3e3e3e")

    # fore: a dripping ceiling, a big support near the camera and the boiling liquid. the scene pins its top row
    # just under the letterbox at the mine view
    fore = Grid(DW + 60, 34)
    top = ""
    while len(top) < fore.w:
        top += r.choice(["_/ `-.", "_,--' `-.", "/ \\,-´", "  `.__", ",-' \\ ", "__  "])
    fore.text(0, 1, top[: fore.w], NEAR)
    for x in range(fore.w):
        if fore.get(x, 1) in "\\/" and r.random() < 0.6:
            fore.set(x, 2, r.choice("VY"), NEAR)
    px = 62
    for y in range(0, 30):
        fore.text(px, y, "||", NEAR)
    fore.rows(px - 5, 0, ["\\\\  ||  //", " \\\\ || //", "  \\\\||//", "   \\()/"], NEAR)
    fore.solid(px - 4, 20, ["  /()\\", " //||\\\\", "// || \\\\"], NEAR)

    liq_a, liq_b = Grid(DW + 70, 3), Grid(DW + 70, 4)
    for x in range(liq_a.w):
        if r.random() < 0.8:
            liq_a.set(x, 0, r.choice("~~~--^"), LIQA)
        if r.random() < 0.4:
            liq_a.set(x, 2, r.choice("~-_"), LIQA)
    for x in range(liq_b.w):
        if r.random() < 0.55:
            liq_b.set(x, 0, r.choice("~-~_"), LIQB)
        if r.random() < 0.25:
            liq_b.set(x, 2, r.choice("~_"), LIQB)
        if r.random() < 0.12:
            liq_b.set(x, 3, "~", LIQB)
    bend = take_bend(main)
    return dict(main=main, far=far, back=back, fore=fore, liqa=liq_a, liqb=liq_b, geysers=geysers, bend=bend)


def rails_row(g, x0, x1, y, col):
    for x in range(x0, x1 + 1):
        g.set(x, y, "." if (x - x0) % 3 == 0 else "_", col)


def oval_track(g, cx, cy):
    """The Ring seen low and side-on like the game's floors: a flattened loop of rails, the far half dimmer, the
    ends curved in .-' strokes."""
    far, near = BACK, RAILC
    # outer rail
    rails_row(g, cx - 20, cx + 20, cy - 4, far)
    g.text(cx - 24, cy - 3, "_.-'", far); g.text(cx + 21, cy - 3, "'-._", far)
    g.text(cx - 27, cy - 2, ".-'", far); g.text(cx + 25, cy - 2, "'-.", far)
    g.set(cx - 28, cy - 1, "/", far); g.set(cx + 28, cy - 1, "\\", far)
    g.set(cx - 28, cy, "|", near); g.set(cx + 28, cy, "|", near)
    g.set(cx - 28, cy + 1, "\\", near); g.set(cx + 28, cy + 1, "/", near)
    g.text(cx - 27, cy + 2, "'-.", near); g.text(cx + 25, cy + 2, ".-'", near)
    g.text(cx - 24, cy + 3, "'-._", near); g.text(cx + 21, cy + 3, "_.-'", near)
    g.text(cx - 20, cy + 4, "'", near); g.text(cx + 20, cy + 4, "'", near)
    rails_row(g, cx - 19, cx + 19, cy + 4, NEAR)
    # inner rail
    rails_row(g, cx - 16, cx + 16, cy - 2, TIEC)
    g.text(cx - 20, cy - 1, ".-'", TIEC); g.text(cx + 18, cy - 1, "'-.", TIEC)
    g.set(cx - 21, cy, "(", MIDG); g.set(cx + 21, cy, ")", MIDG)
    g.text(cx - 20, cy + 1, "'-.", MIDG); g.text(cx + 18, cy + 1, ".-'", MIDG)
    rails_row(g, cx - 16, cx + 16, cy + 2, GROUND)


def ring_path():
    """The middle of the track, anticlockwise on screen, at one pace all the way round (rows count double) with a
    point every 3 frames. Returns xs, ys, dirs, the lap in frames, and the point where he leaves the Ring."""
    m = 4000
    pts = []
    for i in range(m + 1):
        a = math.pi / 2 - i * 2 * math.pi / m
        pts.append((RING["cx"] + 24.5 * math.cos(a), RING["cy"] + 3.0 * math.sin(a), math.sin(a)))
    s = [0.0]
    for i in range(1, m + 1):
        s.append(s[-1] + math.hypot(pts[i][0] - pts[i - 1][0], 2 * (pts[i][1] - pts[i - 1][1])))
    n = int(round(s[-1] / SPEED / 3))
    xs, ys, dirs = [], [], []
    j = 0
    for k in range(n):
        while s[j + 1] < k * s[-1] / n:
            j += 1
        x, y, sn = pts[j]
        xs.append(int(math.floor(x + 0.5)))
        ys.append(int(math.floor(y + 0.5)))
        dirs.append(1 if sn > 0 else -1)
    # where he leaves: the end of the near straight, the last point before the bend
    near = [k for k in range(n) if dirs[k] > 0 and ys[k] == RING["cy"] + 3 and xs[k] <= DEP_X]
    dep = max(near, key=lambda k: xs[k])
    return xs, ys, dirs, n * 3, dep


BEND = (RING["cx"] + 17, RING["cy"] - 4)   # world position of the right-hand bend's top-left cell


def take_bend(main):
    """Lifts the Ring's right-hand bend out of the main layer into a two-frame sprite: whole, and smashed by the
    rock (the near rails end in a stub and the floor beyond is open)."""
    x0, y0 = BEND
    whole = Grid(12, 9)
    for y in range(whole.h):
        for x in range(whole.w):
            whole.c[y][x] = main.c[y0 + y][x0 + x]
            main.c[y0 + y][x0 + x] = None
    broken = Grid(12, 9)
    for y in range(broken.h):
        for x in range(broken.w):
            c = whole.c[y][x]
            # the far half and the end of the loop are gone, the near rails keep their first few cells
            if c and (x <= 2 or (y >= 7 and x <= 4)):
                broken.c[y][x] = c
    for x, y, ch in ((3, 3, ","), (5, 7, "/"), (6, 8, ","), (8, 7, "."), (9, 8, "'"), (10, 6, ","),
                     (7, 6, "'"), (11, 7, "."), (9, 5, "/"), (10, 4, "_"), (3, 8, ".")):
        broken.set(x, y, ch, RAILC if ch in "/_" else MIDG)
    return [whole, broken]


# the chamber around the Ring in two layers: a back wall drifting slower than the track, rocks in front faster
CB = (56, 116)     # world position of the back wall's top-left cell
CF = (48, 116)     # world position of the foreground's top-left cell
VIEW_CY = RING["cy"] - 4   # the wide shot's camera center: wall above, track, floor below


def build_chamber():
    r = random.Random(29)
    back = Grid(90, 20)
    cx = RING["cx"] - CB[0]
    # the back wall: a ceiling edge with drips, a ribbed and stippled face
    for x in range(back.w):
        y = 2 + int(round(math.sin(x * 0.23) + 0.8 * math.sin(x * 0.09 + 2)))
        back.set(x, y, "_" if x % 5 else "-", BACK)
        if r.random() < 0.25:
            back.set(x, y + 1, r.choice("V'Y"), FAR)
        for yy in range(y + 2, 18):
            if r.random() < 0.05:
                back.set(x, yy, r.choice("|'!:."), FAR)
    # derelict supports at the edges of the frame
    for px in (8, back.w - 10):
        for y in range(3, 15):
            if not (px > 40 and 8 < y < 11):
                back.text(px, y, "||", BACK)
        back.text(px - 1, 15, "/()\\", BACK)
        back.text(px - 2, 16, "//||\\\\", BACK)
        back.text(px - 3, 17, "// || \\\\", BACK)
    # a low tunnel mouth choked with rubble, where the old tracks went out
    ax = 14
    back.text(ax + 5, 11, "_.------._", BACK)
    back.text(ax + 2, 12, ".-'", BACK); back.text(ax + 15, 12, "'-.", BACK)
    back.set(ax + 1, 13, "/", BACK); back.set(ax + 18, 13, "\\", BACK)
    for y in range(14, 16):
        back.set(ax, y, "|", BACK)
        back.set(ax + 19, y, "|", BACK)
    back.text(ax + 2, 14, ",.", FAR)
    back.text(ax + 1, 15, ".:'.,_.:,.'::.,'.:", FAR)
    # chains hanging from the ceiling
    for px, n in ((cx + 9, 6), (cx + 16, 9), (cx - 3, 4)):
        for y in range(3, 3 + n):
            back.set(px, y, "┊", FAR)

    front = Grid(110, 34)
    # rocks close to the camera in the bottom corners, a drip of rock at the top right
    left = ["      /\\", "  _.-'  `\\_", "_/   ,     `-._", "  ,  '  .      `-."]
    right = ["    /\\", "  _/  `-._", "_/  ,     `\\", "  .   '    `-._"]
    front.solid(18, 26, left, NEAR)
    front.solid(70, 26, right, NEAR)
    front.solid(86, 0, ["\\     /", " \\   /", "  \\ /", "   V", "   '"], NEAR)
    return back, front


POST = (RING["cx"] - 8, LANTERN[1] - 1)   # world position of the post sprite's top-left cell


def build_post():
    """The Controller's mound and lantern post. It's inside the Ring, so it's its own sprite: in front of the
    Pusher on the far side, behind him on the near side."""
    mound = "_,.-'¯¯¯¯¯¯¯¯¯¯¯'-.,_"
    g = Grid(len(mound), 7)
    lx, ly = LANTERN[0] - POST[0], LANTERN[1] - POST[1]
    g.text(lx - 2, ly - 1, "_.", WOODC)
    g.text(lx - 2, ly, "|(", WOODC)
    g.set(lx + 1, ly, ")", WOODC)
    g.set(lx, ly, "*", LAMP)
    for y in range(ly + 1, RING["cy"] - POST[1] + 1):
        g.set(lx - 2, y, "|", WOODC)
    g.text(0, RING["cy"] + 1 - POST[1], mound, MIDG)
    return g


# ------------------------------------------------------------------ the tracking shot: off the Ring, still pushing
# under the geysers, raw rock the mine gave up on. laid out like the game's maps: a wall at the back split by
# fissures onto a deeper cavern, a floor he walks inside, a ledge at the front, and rock near the camera
PW, PH = 214, 42
CEIL = 10                  # the ceiling's lowest line, roughly; it wanders a few rows either way
TIP = 11                   # stalactites that drip end on this row
BACK_EDGE = 23             # where the wall meets the floor
FRONT_EDGE = 29            # the floor's near edge, a ledge over the dark
WHEELS = 26                # the floor row his wheels run on
COLUMNS = (30, 98, 160)                      # rock columns standing in front of the wall
FISSURES = ((53, 14), (124, 16), (187, 12))  # openings onto the deeper cavern: (center, width)
SUPPORTS = ((10, False), (76, True), (146, False), (206, True))   # old timber supports: (x, snapped)
CRACKS = ((88, 26), (196, 25))               # where the heat glows through the floor: (center x, row)
VENTS = ((64, 24), (146, 25))                # steam vents in the floor: (x, row)
POOL = (113, 27)                             # a small boiling pool
DRIPS = (38, 140, 184)        # under the high parts of the ceiling, so their stalactites reach row TIP
CHAINS = (82, 202)
FAR_FIRES = (30, 96, 142)
CART_AT = 167
NEAR_COLS = (19, 67, 108)  # in the front layer, whose x = 0 sits mid-screen at the start of the shot
FLOOR_RAMP = {23: "#444444", 24: "#4a4a4a", 25: "#525252", 26: "#5a5a5a", 27: "#626262", 28: "#6c6c6c"}
ROCKC = "#4c4c4c"          # the rock face's ribs and strata
FARC = "#363636"
HOT, HOT_EDGE, DEEP = "#d2602a", "#7a3018", "#4a2618"
POOLC = "#5e4c40"
EMBERC = FIRE2


def ceiling(x):
    return CEIL + int(round(1.8 * math.sin(x * 0.13) + 1.2 * math.sin(x * 0.29 + 1)))


def edge_glyph(prev, cur, nxt, left):
    """A glyph for one row of a wavy, mostly vertical edge (a column's or a fissure's side)."""
    d = nxt - prev
    if d > 0:
        return "\\"
    if d < 0:
        return "/"
    return "(" if left and cur < prev else (")" if not left and cur > prev else "|")


def rock_column(g, px, top, bottom, r, near=False):
    """A rock column from ceiling to floor, edges wandering, foot and head flared, shaded round with a bright lit
    edge, a dotted terminator and stipple toward the dark side. Solid, it hides whatever walks behind it."""
    lit, dark = (NEAR, MIDG) if near else (GROUND, MIDG)
    ys = range(top, bottom + 1)
    L = {y: px - 3 + int(round(1.1 * math.sin(y * 0.45 + px))) for y in range(top - 1, bottom + 2)}
    R = {y: px + 3 + int(round(1.1 * math.sin(y * 0.37 + px * 0.7))) for y in range(top - 1, bottom + 2)}
    for y in ys:
        flare = max(0, 2 - (y - top)) + max(0, 3 - (bottom - y))
        L[y] -= flare
        R[y] += flare
    for y in ys:
        a, b = L[y], R[y]
        g.blank(a + 1, y, b - 1, y, BACK)
        g.set(a, y, edge_glyph(L.get(y - 1, a), a, L.get(y + 1, a), True), lit)
        g.set(b, y, edge_glyph(R.get(y - 1, b), b, R.get(y + 1, b), False), dark)
        t = a + int(round((b - a) * 0.62))
        if a < t < b:
            g.set(t, y, "┊", MIDG if near else TEX)
        for x in range(t + 1, b):
            if r.random() < 0.6:
                g.set(x, y, r.choice("::.") if x == b - 1 else r.choice(":.'"), TEX)
        if r.random() < 0.1 and a + 1 < t:
            g.set(a + 1 + r.randint(0, max(0, t - a - 2)), y, r.choice(".'"), TEX)
    # rubble round the foot
    for x in range(L[bottom] - 2, R[bottom] + 3):
        if r.random() < 0.5 and g.get(x, bottom) == " ":
            g.set(x, bottom, r.choice("._,'"), MIDG)


def timber(g, x, snapped, r):
    """One of the old workings' supports, Boiling Mine style, rotting where it stands."""
    top = ceiling(x) + 1
    stop = 16 if snapped else top
    for y in range(stop, BACK_EDGE - 3):
        g.text(x, y, "||", MIDG)
    if snapped:
        g.text(x - 1, stop - 1, "/\\/", MIDG)
        # its upper half hangs from the ceiling, its beam fell across the floor at its foot
        for y in range(top, top + 3):
            g.text(x, y, "||", MIDG)
        g.text(x, top + 3, "\\/", MIDG)
        g.text(x + 3, BACK_EDGE, "═══/═══", TIEC)
    g.text(x - 1, BACK_EDGE - 3, "/()\\", MIDG)
    g.text(x - 2, BACK_EDGE - 2, "//||\\\\", MIDG)
    g.text(x - 3, BACK_EDGE - 1, "// || \\\\", MIDG)


def build_passage():
    r = random.Random(23)
    mid = Grid(PW, PH)

    # the ceiling: solid rock down to a wandering edge, with drips under it
    for x in range(PW):
        c = ceiling(x)
        mid.blank(x, 0, x, c - 1, BACK)
        dy = ceiling(x + 1) - c
        mid.set(x, c, "_" if dy == 0 else ("\\" if dy > 0 else "/"), MIDG)
        for d in range(1, 5):
            stipple(mid, x, c - d, d, TEX, r)
        if r.random() < 0.22:
            mid.set(x, c + 1, r.choice("V'Y`"), TEX)

    # the back wall: solid, ribbed, strata, cracks, and fissures onto the deep cavern
    def in_fissure(x, y):
        for fx, fw in FISSURES:
            top, bot = ceiling(fx) + 3, BACK_EDGE - 1
            if top <= y <= bot:
                hw = fw / 2 * (0.35 + 0.65 * (y - top) / (bot - top)) + math.sin(y * 1.7 + fx) * 0.8
                if abs(x - fx) < hw:
                    return True
        return False

    for x in range(PW):
        for y in range(ceiling(x) + 1, BACK_EDGE):
            if not in_fissure(x, y):
                mid.blank(x, y, x, y, BACK)
    # strata: wandering bands across the face
    for k, base in enumerate((14, 17, 20)):
        for x in range(PW):
            h = base + 0.9 * math.sin(x * 0.07 + k * 2) + 0.5 * math.sin(x * 0.19 + k)
            row = int(math.floor(h))
            if row > ceiling(x) + 1 and not in_fissure(x, row) and r.random() < 0.7:
                sub = h - row
                mid.set(x, row, "'" if sub < 0.34 else ("-" if sub < 0.67 else "_"), ROCKC)
    # ribs and stipple
    for x in range(PW):
        if r.random() < 0.35:
            y0 = ceiling(x) + 2
            for k in range(r.randint(1, 4)):
                if not in_fissure(x, y0 + k) and mid.get(x, y0 + k) == " ":
                    mid.set(x, y0 + k, r.choice("||'!:"), ROCKC)
        for y in range(ceiling(x) + 2, BACK_EDGE):
            if not in_fissure(x, y) and mid.get(x, y) == " " and r.random() < 0.035:
                mid.set(x, y, r.choice(".'`,:"), TEX)
    # a few cracks in the face
    for cx0 in (20, 92, 150, 172):
        y = ceiling(cx0) + 3
        x = cx0
        for _ in range(5):
            if not in_fissure(x, y):
                mid.set(x, y, r.choice("/\\"), ROCKC)
            x += r.choice((-1, 0, 1))
            y += 1
    # the fissures' ragged edges and the lip where the floor ends inside them
    for fx, fw in FISSURES:
        top, bot = ceiling(fx) + 3, BACK_EDGE - 1
        for y in range(top, bot + 1):
            xs = [x for x in range(fx - fw, fx + fw) if in_fissure(x, y)]
            if xs:
                mid.set(xs[0] - 1, y, r.choice("/(|"), MIDG)
                mid.set(xs[-1] + 1, y, r.choice("\\)|"), MIDG)
        for x in range(fx - fw // 2, fx + fw // 2):
            if in_fissure(x, bot) and r.random() < 0.7:
                mid.set(x, BACK_EDGE, r.choice("_.,"), MIDG)

    # stalactites; the ones over the puddles drip
    for sx in list(DRIPS) + [16, 70, 104, 150, 180]:
        c = ceiling(sx)
        n = max(1, TIP - c - 1) if sx in DRIPS else r.randint(1, 3)
        for k in range(n):
            w = max(0, (n - k) // 2)
            mid.set(sx - w - 1, c + 1 + k, "\\", MIDG)
            mid.set(sx + w + 1, c + 1 + k, "/", MIDG)
            mid.blank(sx - w, c + 1 + k, sx + w, c + 1 + k, BACK)
        mid.set(sx, c + 1 + n, "V" if n > 1 else "'", MIDG)

    for x, snapped in SUPPORTS:
        timber(mid, x, snapped, r)
    for px in COLUMNS:
        rock_column(mid, px, ceiling(px) + 1, BACK_EDGE, r)

    # the floor: rubble and grit, lumps of fallen rock, old rails half buried, darker toward the back
    for x in range(PW):
        if mid.get(x, BACK_EDGE) == " " and r.random() < 0.6:
            mid.set(x, BACK_EDGE, r.choice("_.-,'"), FLOOR_RAMP[BACK_EDGE])
    for y in range(BACK_EDGE + 1, FRONT_EDGE):
        col = FLOOR_RAMP[y]
        for x in range(PW):
            if mid.get(x, y) != " ":
                continue
            p = r.random()
            if p < 0.05:
                mid.set(x, y, r.choice(".,'`"), col)
            elif p < 0.065:
                mid.set(x, y, r.choice("o°"), col)
            elif p < 0.075:
                mid.set(x, y, r.choice("_/\\"), TEX)
    for lx, ly in ((24, 25), (58, 27), (102, 24), (134, 26), (186, 27), (200, 24)):
        mid.text(lx, ly, r.choice((".-.", "_.-._", ".o.")), MIDG)
    for rx, ry, n in ((36, 27, 9), (118, 25, 7), (156, 27, 11), (192, 26, 6)):
        for k in range(n):
            if r.random() < 0.8:
                mid.set(rx + k, ry, "." if k % 3 == 0 else "_", TIEC)
    # the old cart, on its back and filling with grit
    mid.text(CART_AT, BACK_EDGE - 1, " ()  () ", MIDG)
    mid.text(CART_AT, BACK_EDGE, "┌──────┐", MIDG)
    mid.text(CART_AT, BACK_EDGE + 1, "└──────┘", MIDG)
    mid.text(CART_AT + 8, BACK_EDGE + 1, ".:.", TEX)
    # where the heat comes through: cracks glowing in the floor
    for cx0, cy0 in CRACKS:
        path = "_/\\/\\_/\\__/\\/"
        for k, ch in enumerate(path):
            x = cx0 - len(path) // 2 + k
            y = cy0 + (1 if k % 5 == 2 else 0) - (1 if k % 7 == 4 else 0)
            mid.set(x, y, ch, HOT)
            if r.random() < 0.5:
                mid.set(x, y + 1, r.choice(",.'"), HOT_EDGE)
    # steam vents, a boiling pool, puddles under the drips
    for vx, vy in VENTS:
        mid.text(vx - 3, vy, "_.-' `-._", MIDG)
    px0, py0 = POOL
    mid.text(px0 - 5, py0, " .-~~-~-. ", POOLC)
    mid.text(px0 - 5, py0 + 1, "(~ ~-~ ~ )", POOLC)
    mid.text(px0 - 5, py0 + 1, "(", MIDG)
    mid.set(px0 + 4, py0 + 1, ")", MIDG)
    for dx in DRIPS:
        mid.text(dx - 1, TIP + 15, "~-~", MIDG)

    # the ledge's edge, ribs under it, drips off the overhang, and the dark below with the heat far down in it
    edge_line(mid, 0, PW - 1, FRONT_EDGE, r, GROUND)
    ribs(mid, 0, PW - 1, FRONT_EDGE + 1, 3, r, MIDG)
    for x in range(PW):
        if r.random() < 0.12:
            mid.set(x, FRONT_EDGE + 1, r.choice("VY'"), TEX)
    for y in range(FRONT_EDGE + 4, PH):
        for x in range(PW):
            if r.random() < 0.015:
                mid.set(x, y, r.choice(".`'"), DEEP if r.random() < 0.4 else FARC)

    # far: the deep cavern beyond the fissures; columns, a ledge far below, the fires down there
    far = Grid(170, PH)
    for x in range(far.w):
        if r.random() < 0.3:
            far.set(x, 9 + r.randint(0, 3), r.choice("V'Y`"), FARC)
    for px in range(8, far.w, 26):
        for y in range(10, 21):
            a = px - 2 + int(round(math.sin(y * 0.5 + px)))
            far.set(a, y, "(" if y % 3 else "|", FARC)
            far.set(a + 5, y, ")" if y % 3 else "|", FARC)
    edge_line(far, 0, far.w - 1, 21, r, "#3a3a3a")
    for y in range(12, 21):
        for x in range(far.w):
            if r.random() < 0.02:
                far.set(x, y, r.choice(".`'"), FARC)
    for x in range(far.w):
        if r.random() < 0.06:
            far.set(x, 22, r.choice(".'"), DEEP)

    # near the camera: rock columns (one broken into a stalactite and a stalagmite), stalactites overhead, outcrops
    front = Grid(200, PH)
    for k, px in enumerate(NEAR_COLS):
        if k == 1:
            for n, (y0, y1, down) in enumerate(((0, 9, True), (26, 35, False))):
                for y in range(y0, y1):
                    w = (y1 - y) // 3 if down else (y - y0) // 3
                    front.blank(px + 3 - w, y, px + 1 + w, y, MIDG)
                    front.set(px + 2 - w, y, "\\" if down else "/", NEAR)
                    front.set(px + 2 + w, y, "/" if down else "\\", MIDG)
                    if w > 1:
                        front.set(px + 2 + w - 1, y, ":", TEX)
                front.set(px + 2, y1 if down else y0 - 1, "V" if down else "^", NEAR)
        else:
            rock_column(front, px + 2, 0, 35, r, near=True)
    for sx in (45, 130, 170):
        front.solid(sx, 0, ["\\     /", " \\ : /", "  \\:/", "   V", "   '"], NEAR)
    for rx in (40, 88, 150):
        front.solid(rx, FRONT_EDGE + 3, ["    /\\  _", "  _/ :`-' `._", "_/ ,  :  '   `\\", "  .  '  :   .  `-._"], NEAR)
    return far, mid, front


# ------------------------------------------------------------------ sprites

def build_sprites(ex):
    # the game's own push pose: ore heaped in the cart and a four-step walk. the game's push left, ours mostly push
    # right, so those are mirrored
    push = [[" ,;;. O", "│¯¯¯¯│¯\\", "└()()┘" + legs] for legs in (" |\\", " |v", "<|", "/ \\")]

    def push_col(x, y, ch):
        if x >= 6:
            return CHAR
        if y == 0:
            return CARGO
        return CARGO if ch in "()" else CART

    left = frames_of(push, CHAR, cfn=push_col)
    right = mirror(left)
    ex.piece("pusherWideR", right)
    ex.piece("pusherWideL", left)

    # the same Pusher on the far side of the Ring, and the far line in the mine: further off, so dimmer
    dim = {CHAR: "#8c8c8c", CART: "#626262", CARGO: "#4e4e4e"}
    ex.piece("pusherFarL", frames_of(push, CHAR, cfn=lambda x, y, ch: dim[push_col(x, y, ch)]))

    # the Controller's whip attack from controller_frames.py, facing left like the game draws him and mirrored for
    # right. the scenes place him by his head's column
    cmap = {"└": DIMC, "┘": DIMC, "─": DIMC}
    left = frames_of(CTRLF.FRAMES, CHAR, cmap)
    ex.piece("ctrlL", left)
    ex.piece("ctrlR", mirror(left))
    ex.value("ctrlHeadL", CTRLF.HEAD_COL)
    ex.value("ctrlHeadR", left[0].w - 1 - CTRLF.HEAD_COL)

    # the rock that breaks the Ring: line art with an opaque inside, so the rails behind it vanish
    rock = ["   _.----._", " .'        `.", "/           \\", "`-._______.-'"]
    g = Grid(max(len(s) for s in rock), len(rock))
    for y, row in enumerate(rock):
        a, b = len(row) - len(row.lstrip()), len(row.rstrip()) - 1
        g.blank(a, y, b, y, GROUND)
        g.text(0, y, row, RAILC)
    for x, y, ch in ((5, 1, "."), (9, 1, "'"), (3, 2, "'"), (7, 2, ","), (10, 2, ".")):
        g.set(x, y, ch, TEX)
    ex.piece("rock", [g])
    # dust thrown up where it lands, settling over a few frames
    rr = random.Random(5)
    dust = []
    for k in range(6):
        g = Grid(21, 5)
        for _ in range(16 - 2 * k):
            x = 10 + int(round(rr.uniform(-1, 1) * (2 + 1.6 * k)))
            y = 4 - int(rr.uniform(0, 2.5 if k < 3 else 1.5))
            g.set(x, y, rr.choice(":'.,`" if k < 3 else ".`'"), MIDG if k < 3 else TEX)
        dust.append(g)
    ex.piece("dust", dust)
    # grit trickling from the ceiling before the rock comes down
    speck = []
    for k in range(16):
        rows = [" "] * 16
        if k < 15:
            rows[k] = "."
        speck.append(rows)
    ex.piece("speck", frames_of(speck, MIDG))

    # for the tracking shot the Pusher is split so he can hop while the cart rolls on: the cart (columns 3-8 of the
    # right-facing frames), his body (columns 0-2), and a hop pose
    cart = Grid(6, 3)
    for y in range(3):
        for x in range(6):
            cart.c[y][x] = right[0].c[y][x + 3]
    ex.piece("cart", [cart])
    bodies = []
    for fr in right:
        b = Grid(3, 3)
        for y in range(3):
            for x in range(3):
                b.c[y][x] = fr.c[y][x]
        bodies.append(b)
    bodies += frames_of([["  O", " /¯", " />"]], CHAR)
    ex.piece("body", bodies)

    # the lash sweeping the floor from the Controller behind him: a loop rolls along the whip to its tip, which
    # cracks at the Pusher's heels (whips.py)
    import whips
    frames, crack = whips.floor_wave(length=70, col=CHAR)
    ex.piece("lash", frames)
    ex.value("lashReach", 70)
    ex.value("lashH", frames[0].h)
    ex.value("lashN", len(frames))
    ex.value("lashCrack", crack)

    flames = [["^", "/^\\"], [" ^", "(^)"], ["^ ", "/^\\"], [" '", "(^)"]]
    fmap = {"^": FIRE1, "'": FIRE1, "/": FIRE2, "\\": FIRE2, "(": FIRE3, ")": FIRE3}
    ex.piece("flame", frames_of(flames, FIRE2, fmap))

    # a bubble that forms in the boiling liquid and pops, and a drip that falls from the ceiling
    bubble = [["   ", " . "], ["   ", " o "], [" _ ", "(_)"], [" _ ", "(_)"], ["   ", "(_)"],
              [" ' ", " ` "], ["` ,", "   "], ["   ", "   "], ["   ", "   "], ["   ", "   "]]
    ex.piece("bubble", frames_of(bubble, LIQA))
    drip = []
    for k in range(9):
        rows = [" "] * 9
        if k < 8:
            rows[k] = "."
        else:
            rows[8] = "'"
        drip.append(rows)
    ex.piece("drip", frames_of(drip, NEAR))

    # --- small life ---
    # a long drip: falls n rows from the ceiling, splashes, and is gone
    def long_drip(n):
        frames = []
        for k in range(n):
            rows = ["   "] * (n + 1)
            rows[k] = " . "
            frames.append(rows)
        for s in (". .", "' '", " . "):
            rows = ["   "] * (n + 1)
            rows[n] = s
            frames.append(rows)
        return frames
    ex.piece("drip14", frames_of(long_drip(14), "#8a8a8a"))
    ex.piece("drip20", frames_of(long_drip(20), "#8a8a8a"))
    # steam rising off the boiling liquid where a bubble pops
    puff = [[""] * 5 + ["  .  "], [""] * 4 + ["  o  "], [""] * 3 + [" ( ) "], [""] * 2 + ["(   )"], ["", " ' . "]]
    ex.piece("puff", frames_of(puff, "#7a7a7a"))
    # a lamp's flame flickering
    ex.piece("lampFlame", frames_of([["*"], ["+"], ["*"], ["'"]], LAMP, {"+": FIRE1, "'": FIRE2}))
    # a fire far below in the dark, seen through the arches
    ex.piece("farFire", frames_of([[" ^ ", "/^\\"], [" ' ", "(^)"]], "#8a4420"))
    # a bat, wings up, level, down
    ex.piece("bat", frames_of([["\\v/"], ["-v-"], ["/v\\"]], MIDG))
    # a hanging chain and hook, swinging a little
    straight = [" ┊ "] * 5 + [" J "]
    ex.piece("chain", frames_of([straight, [" ┊ "] * 3 + ["  ┊"] * 2 + ["  J"],
                                 straight, [" ┊ "] * 3 + ["┊  "] * 2 + ["J  "]], MIDG))
    # a speck of dust turning in the light
    ex.piece("mote", frames_of([["·"]], "#8a7550"))
    # an ember rising off the heat, flickering as it goes
    ex.piece("ember", frames_of([["·"], ["'"], ["·"], ["."]], FIRE2, {"'": FIRE1, ".": FIRE3}))
    # the far line in the mine: the same Controller, dimmer, walking the other way
    dimc = {CHAR: "#8c8c8c", DIMC: "#5a5a5a"}
    ex.piece("ctrlFarL", frames_of(CTRLF.FRAMES[CTRLF.STEP:CTRLF.STEP + 4], CHAR, cfn=lambda x, y, ch: dimc[cmap.get(ch, CHAR)]))


def main():
    pkg = sys.argv[1]
    os.makedirs(pkg, exist_ok=True)
    head = "// Generated by tools/build_scene1.py. Don't edit by hand; change the script and rebuild.\n"
    for old in ("Art1Shaft.txt", "Art1Tunnel.txt"):
        p = os.path.join(pkg, old)
        if os.path.exists(p):
            os.remove(p)

    d = build_descent()
    ex = Exporter(head)
    ex.value("w", DW)
    ex.value("groundRow", GROUND_ROW)
    ex.value("pitX", SX)
    ex.value("mineX", MINE_X)
    ex.piece("far", [d["far"]])
    ex.piece("back", [d["back"]])
    ex.piece("fore", [d["fore"]])
    ex.piece("liqA", [d["liqa"]])
    ex.piece("liqB", [d["liqb"]])
    ex.value("lampX", [p[0] for p in LAMPS])
    ex.value("lampY", [p[1] + 1 for p in LAMPS])
    ex.value("backTrack", BACK_TRACK)
    n1 = ex.write(os.path.join(pkg, "Art1Mine.txt"))

    ex = Exporter(head)
    ex.piece("main", [d["main"]])
    ex.value("geyserX", [p[0] for p in d["geysers"]])
    ex.value("geyserY", [p[1] for p in d["geysers"]])
    ex.value("ringCX", RING["cx"])
    ex.value("viewCY", VIEW_CY)
    n2 = ex.write(os.path.join(pkg, "Art1Descent.txt"))

    cback, cfront = build_chamber()
    ex = Exporter(head)
    ex.piece("back", [cback])
    ex.piece("front", [cfront])
    ex.value("backX", CB[0])
    ex.value("backY", CB[1])
    ex.value("frontX", CF[0])
    ex.value("frontY", CF[1])
    ex.value("ctrlX", CTRL[0])
    ex.value("ctrlY", CTRL[1])
    ex.value("lampX", LANTERN[0])
    ex.value("lampY", LANTERN[1])
    ex.piece("post", [build_post()])
    ex.value("postX", POST[0])
    ex.value("postY", POST[1])
    ex.piece("bend", d["bend"])
    ex.value("bendX", BEND[0])
    ex.value("bendY", BEND[1])
    # where the rock comes to rest on the bend, and where its dust rises (centered on its base)
    ex.value("rockX", BEND[0] + 1)
    ex.value("rockY", BEND[1])
    ex.value("dustX", BEND[0] + 7 - 10)
    ex.value("dustY", BEND[1] + 4 - 4)
    xs, ys, dirs, lap, dep = ring_path()
    ex.value("pathX", xs)
    ex.value("pathY", ys)
    ex.value("pathDir", dirs)
    ex.value("lap", lap)
    ex.value("depIdx", dep)
    ex.value("speed", SPEED)
    n5 = ex.write(os.path.join(pkg, "Art1Ring.txt"))

    pfar, pmid, pfront = build_passage()
    ex = Exporter(head)
    ex.value("wheels", WHEELS)
    ex.piece("far", [pfar])
    ex.piece("mid", [pmid])
    ex.piece("front", [pfront])
    ex.value("dripX", list(DRIPS))
    ex.value("dripTop", TIP + 1)
    ex.value("chainX", list(CHAINS))
    ex.value("chainTop", [ceiling(x) + 1 for x in CHAINS])
    ex.value("fireX", list(FAR_FIRES))
    ex.value("fireY", 20)
    ex.value("glowX", [c[0] for c in CRACKS])
    ex.value("glowY", [c[1] for c in CRACKS])
    ex.value("ventX", [v[0] for v in VENTS])
    ex.value("ventY", [v[1] for v in VENTS])
    ex.value("poolX", POOL[0])
    ex.value("poolY", POOL[1])
    n3 = ex.write(os.path.join(pkg, "Art1Track.txt"))

    ex = Exporter(head)
    build_sprites(ex)
    n4 = ex.write(os.path.join(pkg, "Art1Sprites.txt"))
    print(f"Art1Mine {n1}, Art1Descent {n2}, Art1Ring {n5}, Art1Track {n3}, Art1Sprites {n4} bytes")
    print(f"ring: {len(xs)} points, lap {lap} frames, leaves at point {dep} = ({xs[dep]}, {ys[dep]})")


if __name__ == "__main__":
    main()
