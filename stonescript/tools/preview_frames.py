# steps the Stonescript simulator and draws what the game would show at the given frames (needs Pillow)
# preview only: it assumes a 69 x 30 screen and only roughly matches the game font
#   python -I preview_frames.py <out_dir> <frame> [<frame> ...]
import colorsys
import re
import os
import sys

# where ssim (the offline Stonescript simulator) is: SSIM_TOOLS, or else the first line of ssim_path.txt next to
# this file (each machine's own, not in git)
HERE = os.path.dirname(os.path.abspath(__file__))
SSIM = os.environ.get("SSIM_TOOLS") or open(os.path.join(HERE, "ssim_path.txt"), encoding="utf-8").readline().strip()
sys.path.insert(0, SSIM)
from ssim import Sim, Scenario
from ssim import ui as U
from ssim.values import to_str
from PIL import Image, ImageDraw, ImageFont

PKG = os.path.dirname(HERE)
SW, SH = 69, 30
CW, CHH = 12, 24
FONT = ImageFont.truetype(r"C:\Windows\Fonts\CascadiaMono.ttf", 19)
# glyphs the game font has and Cascadia doesn't (the stars on the banners, the snowflake)
SYMBOLS = ImageFont.truetype(r"C:\Windows\Fonts\seguisym.ttf", 17)
SYMBOL_CHARS = set("☆★❄")


# keep canvas colors (the mock only logs them)
def setfg(self, *a):
    if not hasattr(self, "fgc"):
        self.fgc, self.fga = {}, "#ffffff"
    if len(a) == 1:
        self.fga, self.fgc = to_str(a[0]), {}
    else:
        self.fgc[(a[0], a[1])] = to_str(a[2])


def setbg(self, *a):
    if not hasattr(self, "bgc"):
        self.bgc, self.bga = {}, "#000000"
    if len(a) == 1:
        self.bga, self.bgc = to_str(a[0]), {}
    else:
        self.bgc[(a[0], a[1])] = to_str(a[2])


U.Canvas.m_setfg = setfg
U.Canvas.m_setbg = setbg

# and the colors Set can carry too: Set(x, y, fg, str) and Set(x, y, fg, bg, str)
_set = U.Canvas.m_set


def set_cell(self, *a):
    _set(self, *a)
    if len(a) >= 4:
        setfg(self, a[0], a[1], a[2])
    if len(a) >= 5:
        setbg(self, a[0], a[1], a[3])


U.Canvas.m_set = set_cell

# a canvas taken back out of the pool starts with the default colors, as a new one does
_reset = U.Canvas.reset


def reset_canvas(self):
    _reset(self)
    self.fga, self.fgc = "#ffffff", {}
    self.bga, self.bgc = "#000000", {}


U.Canvas.reset = reset_canvas


def hexrgb(s):
    s = (s or "#ffffff").strip()
    if s.lower().startswith("#rain"):
        return None
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def rainbow(t, col, width, code="#rainFF"):
    """The game's rainbow. Whatever follows #rain is ignored, the game always draws it at full."""
    h = (-0.4 * t + col / (2 * width)) % 1.0
    r, g, b = colorsys.hsv_to_rgb(h, 1, 1)
    return tuple(int(255 * (v + (1 - v) * 0.5)) for v in (r, g, b))


def vis(c):
    v = c.props.get("visible", True)
    return v is not False


def kids(c):
    return getattr(c, "children", []) or []


_pages = {}


def sheet_pages(sheet):
    """An anim's pages, split at each %% line, as (rows, x, y). x and y are always 0, since an anim a script makes
    shows a page offset as text."""
    if sheet in _pages:
        return _pages[sheet]
    out, cur = [], []
    for ln in sheet.split("\\n"):
        if ln.strip() == "%%":
            out.append((cur, 0, 0))
            cur = []
        else:
            cur.append(ln)
    out.append((cur, 0, 0))
    _pages[sheet] = out
    return out


STYLES = {0: "         ", 1: "┌─┐│ │└─┘", 2: ".─.│ │'─'", 3: "╔═╗║ ║╚═╝", 4: "┌─┐│ │╘═╛", 5: "╓─┐║ │╚═╛",
          6: "┌─╖│ ║╘═╝", 7: "▄▄▄█ █▀▀▀", 8: "█▀██ ██▄█"}


def box_style(uisys, st):
    """A panel's or button's nine glyphs: a built-in style, or one a script made with ui.AddStyle."""
    try:
        st = int(st)
    except (TypeError, ValueError):
        return STYLES[1]
    for s, i in getattr(uisys, "styles", {}).items():
        if i == st and len(s) >= 9:
            return s[:9]
    return STYLES.get(abs(st) % 9, STYLES[1])


def compose(uisys, t):
    """What's on the screen at time t: rows of [glyph, foreground, background] (render draws it)."""
    grid = [[[" ", (0, 0, 0), (0, 0, 0)] for _ in range(SW)] for _ in range(SH)]

    def put(x, y, ch, fg):
        if 0 <= x < SW and 0 <= y < SH:
            grid[y][x][0] = ch
            grid[y][x][1] = fg

    def draw_sheet(sheet, frame, ox, oy, color):
        pages = sheet_pages(sheet)
        rows, mx, my = pages[frame % len(pages)]
        rows = rows or [""]
        width = max(len(r) for r in rows)
        rgb = hexrgb(color)
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch != "#":
                    put(ox + mx + i, oy + my + j, ch, rgb or rainbow(t, i, width, color))

    def walk(c, px, py, pw, ph, hidden=False):
        # like the game: a canvas is drawn even when it or its panel is hidden
        hidden = hidden or not vis(c)
        if hidden and c.TYPE not in ("Canvas", "Panel"):
            return
        p = c.props
        x, y, w, h = p.get("x", 0), p.get("y", 0), p.get("w", 10), p.get("h", 5)
        dock = str(p.get("dock", ""))
        if dock.startswith("center"):
            ax, ay = px + pw // 2 + x - w // 2, py + ph // 2 + y
        elif dock == "top_center":
            ax, ay = px + pw // 2 + x - w // 2, py + y
        else:
            ax, ay = px + x, py + y
        kind = c.TYPE
        if kind == "Anim":
            fr = p.get("frame", 0)
            draw_sheet(c.sheet, fr, ax, ay, p.get("color"))
            for l in c.layers:
                draw_sheet(l.sheet, fr, ax, ay, l.props.get("color"))
        elif kind == "Canvas":
            blend = str(p.get("blend", "opaque")).lower()
            fill = getattr(c, "fill", "#")
            fga, bga = getattr(c, "fga", "#ffffff"), getattr(c, "bga", "#000000")
            fgc, bgc = getattr(c, "fgc", {}), getattr(c, "bgc", {})
            for j in range(min(h, 27)):
                for i in range(min(w, 100)):
                    gx, gy = ax + i, ay + j
                    if not (0 <= gx < SW and 0 <= gy < SH):
                        continue
                    sym = c.cells.get((i, j), fill)
                    f = hexrgb(fgc.get((i, j), fga)) or (255, 255, 255)
                    b = hexrgb(bgc.get((i, j), bga)) or (0, 0, 0)
                    cell = grid[gy][gx]
                    if blend == "opaque":
                        if sym == "#":
                            continue
                        cell[0], cell[1], cell[2] = sym, f, b
                    elif blend == "multiply":
                        cell[1] = tuple(int(a * m / 255) for a, m in zip(cell[1], f))
                        cell[2] = tuple(int(a * m / 255) for a, m in zip(cell[2], b))
                    elif blend == "add":
                        cell[1] = tuple(min(255, a + m) for a, m in zip(cell[1], f))
                        cell[2] = tuple(min(255, a + m) for a, m in zip(cell[2], b))
        elif kind in ("Panel", "Button") and not hidden:
            # the box in its style ('#' cells skipped), centered like the game on a center anchor, a button's label
            # on the middle row
            if dock.startswith("center"):
                ay = py + ph // 2 + y - h // 2
            glyphs = box_style(uisys, p.get("style", 1))
            col = hexrgb(p.get("color" if kind == "Panel" else "bcolor")) or (255, 255, 255)
            for j in range(h):
                for i in range(w):
                    r = 0 if j == 0 else 2 if j == h - 1 else 1
                    k = 0 if i == 0 else 2 if i == w - 1 else 1
                    g = glyphs[r * 3 + k]
                    if g != "#":
                        put(ax + i, ay + j, g, col)
            if kind == "Button":
                s = to_str(p.get("text", ""))
                tcol = hexrgb(p.get("tcolor")) or (255, 255, 255)
                for i, ch in enumerate(s):
                    if ch != "#":
                        put(ax + w // 2 - len(s) // 2 + i, ay + h // 2, ch, tcol)
        elif kind == "Text":
            s = to_str(p.get("text", ""))
            col = hexrgb(p.get("color")) or (255, 255, 255)
            if dock.startswith("center") or dock == "top_center":
                sx = px + pw // 2 + x - len(s) // 2
            else:
                # docked top-left, text centered in its box
                sx = ax + (w - len(s)) // 2
            for i, ch in enumerate(s):
                put(sx + i, ay, ch, col)
        for k in kids(c):
            walk(k, ax, ay, w, h, hidden)

    root = uisys.root
    for k in kids(root):
        walk(k, 0, 0, SW, SH)
    return grid


def render(uisys, t, path=None):
    grid = compose(uisys, t)
    img = Image.new("RGB", (SW * CW, SH * CHH), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(SH):
        for x in range(SW):
            ch, fg, bg = grid[y][x]
            if bg != (0, 0, 0):
                d.rectangle([x * CW, y * CHH, x * CW + CW - 1, y * CHH + CHH - 1], fill=bg)
            if ch not in (" ", "#"):
                d.text((x * CW + CW / 2, y * CHH + CHH / 2), ch, fill=fg, font=SYMBOLS if ch in SYMBOL_CHARS else FONT,
                       anchor="mm")
    if path:
        img.save(path)
    return img


def new_sim(entry=None):
    """The package running at the Deadwood waterfall on a SW x SH screen. entry: a script to run instead of
    Deltahead/Main (tools/entries has single-scene ones)."""
    sc = Scenario(loc_id="waterfall", loc_name="Deadwood Waterfall", stars=0, hp=40)
    sc.set("screen.w", SW)
    sc.set("screen.h", SH)
    return Sim(entry or PKG + r"\Deltahead\Main.txt", sc, search_paths=[PKG])


def main():
    out = sys.argv[1]
    want = sorted(int(a) for a in sys.argv[2:])
    os.makedirs(out, exist_ok=True)
    sim = new_sim()
    frame = 0
    for target in want:
        while frame <= target:
            sim.step()
            frame += 1
        film = sim.var("film")
        fval = film.get_var("f") if hasattr(film, "get_var") else None
        render(sim.ui, target / 30.0, os.path.join(out, f"f{target:04d}.png"))
        print("rendered", target, "film f =", fval)


if __name__ == "__main__":
    main()
